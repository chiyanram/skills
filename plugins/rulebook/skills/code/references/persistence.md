# Persistence

How a JPA application fetches associations, bounds and pages its queries, writes in bulk and in batches, generates
ids, compares and locks entities, and sizes its connection pool. Read it when you write or review a JPA entity, a
repository or query method, a service method that reads entities, or the JPA, Hibernate or Hikari settings.

Contents: Rules · When X, use Y · Good / Bad (PS2, PS4, PS5, PS3, PS9, PS11, PS12) · Decided edges · Review checks

## Rules

- **PS1** — Declare every `@ManyToOne` and `@OneToOne` `fetch = FetchType.LAZY`, and never write `FetchType.EAGER`,
  because JPA's eager to-one default loads the associated row on every query, often as one extra select per result.
- **PS2** — Fetch each association a use case navigates in the owner's query (`join fetch`, `@EntityGraph` or a DTO
  projection), never lazily per result element, because each element then costs one more select (N+1).
- **PS6** — Bound every query whose result grows with the data with a `Pageable`, `Limit` or SQL `LIMIT`; never return
  the whole table as a `List` (`findAll()`), because each call then loads it into the heap.
- **PS4** — Never page (`Pageable`, `Limit`, `setMaxResults`) a query that fetches a collection; page the owner ids,
  then fetch the collection for those ids, because Hibernate loads every matching row and pages in memory.
- **PS5** — Give every paged or limited query an `ORDER BY` that ends on a unique column, such as the id, because
  without a unique order PostgreSQL returns an unpredictable subset and pages skip or repeat rows.
- **PS3** — Fetch at most one collection per query; load each further collection with its own query or `@BatchSize`,
  because two collection fetches multiply rows into a Cartesian product or throw `MultipleBagFetchException`.
- **PS7** — Set `spring.jpa.open-in-view: false`, because Boot's default keeps the persistence context open through
  response rendering, so lazy loads there run unplanned queries outside the service's transaction.
- **PS13** — Give every entity that two requests can update concurrently a `@Version` field, never set by hand,
  because without it the later of two edits silently overwrites the earlier.
- **PS8** — Write `@Modifying(flushAutomatically = true, clearAutomatically = true)` on every modifying repository
  query, because the bulk statement bypasses the persistence context: it misses pending changes and leaves managed
  entities stale.
- **PS9** — Change rows that all get the same new value with one `@Modifying` update or delete, never by loading
  entities and setting fields in a loop, because dirty checking loads every row, one `UPDATE` each.
- **PS10** — Set `spring.jpa.properties.hibernate.jdbc.batch_size`, starting between 10 and 50, because Hibernate's
  default of 0 sends every insert and update in its own round trip.
- **PS11** — For an entity inserted in bulk, map its generated id as `GenerationType.SEQUENCE` with a
  `@SequenceGenerator` whose `allocationSize` equals the sequence's `INCREMENT BY`, never `IDENTITY`, because Hibernate
  cannot batch inserts of `IDENTITY` entities.
- **PS12** — Base an entity's `equals` and `hashCode` on its immutable `@NaturalId`, using `instanceof` and accessor
  reads; never a generated id, a mutable field or `getClass()`, because ids appear only on persist and proxies fail
  `getClass()`.
- **PS14** — Run Hikari as a small fixed pool: `maximum-pool-size` from a load test, starting near twice the
  database's cores, a few dozen at most, no `minimum-idle`, because surplus connections contend and lower throughput.
- **PS15** — Stop a bulk update or delete whose target list is empty before it runs; never let an empty list mean no
  filter, because an empty filter applies the command to every row.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a `@ManyToOne` or `@OneToOne` | `fetch = FetchType.LAZY` (PS1) | the eager default loads the associated row on every query |
| a use case that reads an association of each result | `join fetch`, `@EntityGraph` or a DTO projection in the owner's query (PS2) | one query loads the owners and the association, not one more select per owner |
| two collections to load with one owner | one collection in the owner's query, each further one in its own query or by `@BatchSize` (PS3) | two collection fetches multiply rows or throw `MultipleBagFetchException` |
| a page of owners that needs a collection | a paged query for the owner ids, then a fetch of the collection for those ids (PS4) | SQL cuts the page, so Hibernate does not load every row to cut it in memory |
| a paged or limited query | an `ORDER BY` whose last key is the id or another unique column (PS5) | rows that tie have no defined order, so pages skip or repeat them |
| a query whose result grows with the data | a `Pageable`, `Limit` or SQL `LIMIT` (PS6) | an unbounded `List` loads the whole table into the heap |
| a JPA application's `application.yml` | `spring.jpa.open-in-view: false` (PS7) and `hibernate.jdbc.batch_size` (PS10) under `spring.jpa.properties` | lazy loads stay inside the service's transaction, and writes go in batches |
| a repository `@Query` that updates or deletes | `@Modifying(flushAutomatically = true, clearAutomatically = true)` (PS8) | pending changes reach the database first, and no managed entity stays stale |
| rows that all take the same new value | one `@Modifying` update or delete (PS9) | one statement, no load and no dirty check per row |
| an entity inserted in bulk (`saveAll`, `persist` in a loop) | `GenerationType.SEQUENCE` with `allocationSize` equal to the sequence's `INCREMENT BY` (PS11) | Hibernate batches the inserts and fetches ids once per allocation |
| an entity's `equals` and `hashCode` | its `@NaturalId`, compared with `instanceof` and accessors (PS12) | the value is there before persist, and a proxy passes `instanceof` |
| an entity two requests can update | a `@Version` field that only Hibernate sets (PS13) | the later of two edits fails instead of overwriting the earlier |
| the Hikari pool settings | `maximum-pool-size` from a load test and no `minimum-idle` (PS14) | a small fixed pool gives more throughput than a large one |
| a bulk update or delete that takes a list of targets | a guard that stops on an empty list before the statement runs (PS15) | an empty list must not mean every row |

The key column of a PS11 entity is MG36 in [postgres-design.md](../../migrations/references/postgres-design.md),
declared `GENERATED BY DEFAULT AS IDENTITY (INCREMENT BY 50)`, because `GENERATED ALWAYS` rejects the ids Hibernate
assigns.

## Good / Bad

### PS2 — Fetch what the use case navigates in the owner's query

**Bad**
```java
// InvoiceQueries, a @Transactional(readOnly = true) service
List<InvoiceRow> overdue(final Pageable page) {
    return invoices.findByStatusOrderByDueOnAscIdAsc(InvoiceStatus.OVERDUE, page).stream()
            .map(invoice -> new InvoiceRow(invoice.number(), invoice.customer().name()))
            .toList();
}
```
Each `invoice.customer()` loads one customer, so a page of 50 runs 51 selects.

**Good**
```java
@Query("""
        select i from Invoice i join fetch i.customer
        where i.status = :status order by i.dueOn, i.id""")
Slice<Invoice> findWithCustomerByStatus(InvoiceStatus status, Pageable page);
```
A single query loads each invoice with its customer.

### PS4 — Page the owner ids, then fetch the collection for those ids

**Bad**
```java
@Query("select o from Order o left join fetch o.lines where o.status = :status order by o.placedAt, o.id")
Page<Order> findWithLines(OrderStatus status, Pageable page);
```
Hibernate reads every matching order and line, then cuts the page in memory.

**Good**
```java
@Query("select o.id from Order o where o.status = :status order by o.placedAt, o.id")
Slice<Long> findIdsByStatus(OrderStatus status, Pageable page);

@Query("select o from Order o left join fetch o.lines where o.id in :ids order by o.placedAt, o.id")
List<Order> findWithLinesByIdIn(Collection<Long> ids);
```
The page is cut in SQL on the ids. The second query re-sorts because `IN` does not keep their order.

### PS5 — A paged order that ends on a unique column

**Bad**
```java
final var page = PageRequest.of(pageNumber, 50, Sort.by("dueOn"));
```
Many invoices share a due date, so rows that tie can move between pages.

**Good**
```java
final var page = PageRequest.of(pageNumber, 50, Sort.by("dueOn", "id"));
```
The id breaks every tie, so each row sits on exactly one page.

### PS3 — One collection per query; each further one in its own query

**Bad**
```java
@EntityGraph(attributePaths = {"lines", "payments"})
Optional<Order> findDetailedById(long id);
```
Two `List` collections throw `MultipleBagFetchException`; as `Set`s they multiply into lines × payments rows.

**Good**
```java
@EntityGraph(attributePaths = "lines")
Optional<Order> findWithLinesById(long id);

// PaymentRepository: the second collection, in its own query
List<Payment> findByOrderIdOrderByPaidAtAscIdAsc(long orderId);
```
Each query fetches one collection, so no row is repeated for every payment.

### PS9 — One statement for rows that all take the same value

**Bad**
```java
@Transactional
public void markOverdue(final LocalDate today) {
    invoices.findByStatusAndDueOnBeforeOrderByIdAsc(InvoiceStatus.OPEN, today, Limit.of(500))
            .forEach(Invoice::markOverdue);
}
```
Each batch of open invoices is loaded and dirty-checked, then updated one row at a time.

**Good**
```java
@Modifying(flushAutomatically = true, clearAutomatically = true)
@Query("""
        update versioned Invoice i set i.status = :overdue
        where i.status = :open and i.dueOn < :today""")
int markOverdue(InvoiceStatus open, InvoiceStatus overdue, LocalDate today);
```
A single statement does the update, and `versioned` makes it increment `@Version`, so concurrent editors still see the
conflict.

### PS11 — A sequence id for an entity inserted in bulk

**Bad**
```java
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```
Each insert must run alone to read back its id, so `saveAll` of 500 invoices sends 500 statements.

**Good**
```java
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "invoice_id")
@SequenceGenerator(name = "invoice_id", sequenceName = "invoices_id_seq", allocationSize = 50)
private Long id; // the migration declares id bigint GENERATED BY DEFAULT AS IDENTITY (INCREMENT BY 50)
```
With these ids, `saveAll` of 500 invoices sends batched inserts and takes about 10 sequence calls.

### PS12 — Equality on the natural id, with `instanceof`

**Bad**
```java
@Override
public boolean equals(final Object other) {
    if (other == null || getClass() != other.getClass()) {
        return false;
    }
    return Objects.equals(id, ((Invoice) other).id);
}

@Override
public int hashCode() {
    return Objects.hash(id);
}
```
An invoice put in a `Set` before it is persisted changes its hash on persist. A lazy proxy never equals the real
invoice.

**Good**
```java
@NaturalId
@Column(nullable = false, updatable = false)
private String number;

@Override
public boolean equals(final Object other) {
    return other instanceof Invoice invoice && number.equals(invoice.number());
}

@Override
public int hashCode() {
    return number.hashCode();
}
```
The number exists before persist and never changes, and a proxy of `Invoice` passes `instanceof`.

## Decided edges

- **Skip when** the field is a persistent field or the id of a JPA `@Entity`: it may be non-`final` (TY4), the entity
  is a class with its own `equals` and `hashCode`, not a record (MJ1), and its id is `null` before persist (TY1),
  because the JPA specification forbids final persistent fields and record entities. — **Do not skip when** the class
  is not an entity, such as a DTO or a projection, or a method returns a value that may be absent: it still returns
  `Optional` (TY1). — **Confidence** high

## Review checks

Walk every changed `@Entity` class, every changed repository and query method, every changed service method that reads
entities, and every changed `application*.yml` or `application*.properties` in `src/main`.

- [ ] PS1 — `grep -rnE "@(ManyToOne|OneToOne)\b|FetchType\.EAGER" src/main | grep -v "FetchType.LAZY"`. Each hit is a
  finding; when the annotation spans several lines, read them.
- [ ] PS2 — List the associations (`grep -rnE "@(OneToMany|ManyToMany|ManyToOne|OneToOne)\b" src/main`). In each loop,
  stream or `map` over a query result, a getter of one of them that the query did not fetch is a finding.
- [ ] PS6 — `grep -rnE "\.findAll\(\)|List<\w+> find\w*\([^,()]*\);" src/main | grep -vE "By\w*Id(In)?(OrderBy\w*)?\("`,
  then read each hit: a list that grows with the table is a finding; one bounded by its parent is not.
- [ ] PS4 — `grep -rnE -A4 "join fetch|@EntityGraph" src/main | grep -E "Pageable|Limit\b|setMaxResults"`, then read
  each hit and its method signature: a fetched collection is a finding; a fetched to-one is not.
- [ ] PS5 — `grep -rnE "PageRequest\.of\([^,()]+,[^,()]+\)|Sort\.by\(\"[^\"]+\"\)|Sort\.by\(Sort\.Direction\.\w+, *\"[^\"]+\"\)" src/main` (no sort, or one key), and
  `grep -rnE "\bLIMIT\b" src/main | grep -v "ORDER BY"`. Then read each paged or limited query: a last order key that
  is not unique is a finding.
- [ ] PS3 — `grep -rnE "(join fetch .*){2}|attributePaths *= *\{[^}]*," src/main`, then read each hit: two fetched
  collections are a finding; a collection with to-one attributes is not.
- [ ] PS7 — `grep -rnE "open-in-view[:=] *false" src/main/resources`: no hit is a finding.
- [ ] PS13 — `grep -rlE "^\s*@Entity\b" src/main | xargs grep -L "@Version"`, then read which of those entities are
  updated: one that two requests can update is a finding. A setter or assignment of the `@Version` field is a finding.
- [ ] PS8 — `grep -rnE "@Modifying\b" src/main | grep -vE "clearAutomatically *= *true"`: each hit is a finding. Read
  every `@Modifying` for `flushAutomatically = true`; one without it is a finding.
- [ ] PS9 — `grep -rnE "\.find\w*\(.*\)\.forEach\(|^\s*\.forEach\(|for \(.*: *\w+\.find\w*\(" src/main`, then read the
  body: a setter or state change with the same value for every row is a finding.
- [ ] PS10 — `grep -rnE "batch_size|batch-size|batchSize" src/main/resources`: no hit is a finding, and so is the
  `batch-size` or `batchSize` spelling, which Hibernate ignores.
- [ ] PS11 — `grep -rnE "GenerationType\.IDENTITY|@GeneratedValue *(\( *\))? *$" src/main`, then read whether the
  entity is inserted in bulk (`saveAll`, `persist` in a loop): such an entity is a finding. For each `allocationSize`,
  an `INCREMENT BY` in the migration that differs is a finding, and so is a key column declared
  `GENERATED ALWAYS`.
- [ ] PS12 — `grep -rlE "^\s*@Entity\b" src/main | xargs grep -LE "boolean equals\("`: an entity compared or put in a
  `Set` is a finding. `grep -rnE "getClass\(\) *!= *\w+\.getClass\(\)|Objects\.hash\(id\)|id\.hashCode\(\)"` in
  entity files: each hit is a finding, and so is `equals` on a field that is not the `@NaturalId`.
- [ ] PS14 — `grep -rnE "minimum-idle|maximum-pool-size[:=] *([5-9][0-9]|[0-9]{3,})" src/main/resources`: each hit is a
  finding. A `maximum-pool-size` with no load test behind it is a finding.
- [ ] PS15 — For each bulk update or delete whose list predicate is added only when the list is non-empty (Criteria
  or a `Specification` built in an `if`, dynamic SQL, a remote command with an optional filter), a missing guard that
  stops on an empty list is a finding.
