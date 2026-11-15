# Stack notes

Read this when the change touches Java, a Maven or Gradle build file, a Spring bean or setting, a JPA entity or query,
or an Angular component, template or `tsconfig`. The general rules are in [SKILL.md](SKILL.md).

## Time

- Take an injected `Clock` and call `now(clock)`, never no-argument `now()`, because a test cannot fix the wall clock
  and flakes at midnight or across zones.
- Compute time in `java.time` types (`Instant`, `Duration`), never `Date`, `Calendar` or a raw `long` of millis.
  Convert only at a library or display edge, because `Date` and its formatters are mutable and not thread-safe.

## Streams and collections

- Use sequential streams in code that serves requests or queues. Never `parallelStream()` or `.parallel()`, because
  they run on the one JVM-wide common pool, and one blocking task stalls every other user of it.
- Keep stream lambdas free of I/O, logging and mutation, and never do work in `peek`, because the stream may skip
  those calls and the effect then does not happen.
- Give every `toMap` a merge function, because a duplicate key throws `IllegalStateException` at runtime.
- Collect with `toList()` when nobody changes the result, and with `Collectors.toCollection(ArrayList::new)` when the
  caller must. Never call `sort`, `add` or `remove` on a `toList()` result, because it throws; never rely on a
  `Collectors.toList()` result being mutable, because it promises nothing.
- In a record or class that takes a collection, store `List.copyOf`, `Set.copyOf` or `Map.copyOf` of the argument in
  the compact constructor, never the argument, a view or an array, because the caller keeps the original and can
  change the object later. `copyOf` throws on a `null` element on purpose: parse the `null` away in the adapter, never
  switch to a copy that admits it.

## Java language

- Declare an immutable data carrier (a DTO, an event, a settings group, a value) as a record, because a field added to
  a hand-written class is easily left out of `equals` and `hashCode`. A JPA entity stays a class.
- Write every `switch` in arrow form, and make one that yields a value a switch expression, because a colon case
  without `break` falls through and a statement case can forget to assign. `default ->` is right only for an `int` or
  `String` selector.
- Dispatch on a sealed type with a pattern `switch`, never an `if`/`else if` chain of `instanceof`, because the chain
  has no exhaustiveness check and a new subtype takes the last branch. Test and bind in one step
  (`x instanceof Type t`), never a test then a cast.
- Name an unused catch parameter, lambda parameter or pattern variable `_`, because a named one reads as used. In a
  record pattern, write the component type or `_`, never `var`.
- Use `var` only when the initializer names the type (a constructor, a factory, a literal), and never with `<>`,
  because the reader cannot see a hidden type and `var` with a diamond infers `Object`. A framework style guide that
  bans `var` does not apply to application code.
- Use `Optional` only as a return type, never as a field, parameter or collection element, because an `Optional`
  parameter has three states and every callee must check all three. Unwrap it with `map`, `orElse`, `orElseGet` or
  `orElseThrow`, never `get()` or `isPresent()` then `get()`, because `get()` hides that it throws.
- Compare `BigDecimal` values with `compareTo`, never `equals`, because `equals` treats 2.0 and 2.00 as different.
- Add, multiply or narrow counts and minor-unit money with `Math.addExact`, `multiplyExact` and `toIntExact`, never
  bare `+`, `*` or an `(int)` cast, because overflow wraps silently to a wrong total.
- Write a multi-line SQL, JSON or HTML string as a text block, never `+`-joined literals with `\n`.
- Open every `AutoCloseable` backed by I/O (a file, a socket, a connection) in a try-with-resources header, because a
  resource not closed when an exception fires leaks until the process runs out of handles. A `Stream` over a
  collection needs none.
- Put braces on every `if`, `else`, `for`, `do` and `while` body, because a line added under a brace-less body looks
  guarded but always runs.
- Make a class with only static members `final` with a private constructor, because Java adds a public one. The
  `@SpringBootApplication` class is the exception: the context builds it.
- In a package-private class, make a method `public` only when it overrides, because a public method there widens
  visibility by accident.
- Write output through the logger, never `System.out`, `System.err` or `printStackTrace()` outside a `main` method,
  because console output skips the logger's level and context.
- Let the formatter decide wrapping: the configured line length for Java and Groovy, Prettier for TypeScript, because
  a hand-wrapping style fights the formatter's output.

## The build

- Use only features that are final in the target JDK, and never compile or run production code with
  `--enable-preview`, because a preview feature may change next release and its class files load only on that JDK.
  Where the target JDK is older than the release that made a feature final, write the form that JDK offers. A new
  project targets the newest JDK the team runs.
- Set the Java level with `--release` (Maven `maven.compiler.release` or `<release>`), never `-source`/`-target` or
  `maven.compiler.source`/`target`, because those compile against the build JDK's API and can emit classes that fail
  on the target JDK.

## Spring beans

- Give each bean one constructor that takes every required dependency into a `final` field, without `@Autowired`, and
  no second constructor for tests. Never inject through a field or setter, because the bean can then start with a null
  dependency. Tests may use `@Autowired`.
- Take an optional collaborator as `ObjectProvider<T>` and resolve it where it is used, never in the constructor or a
  `@Bean` method, so its absence is a decision in code, not a null.
- Cut every bean dependency cycle. Where it cannot be cut, inject `ObjectProvider<T>` and resolve it at call time,
  because a constructor cycle fails startup and an AOT context refuses it.
- Never inject a prototype-, request- or session-scoped bean straight into a singleton. Inject `ObjectProvider<T>` and
  resolve it per use, because the singleton keeps the first instance forever.
- Never enable global lazy initialization, because a misconfigured bean then fails on first use, not at startup.
- When only one implementation of an interface should run, give each one `@ConditionalOnProperty` for its own value so
  exactly one matches and an unset value fails startup. Never select it with `@Primary`, `@Fallback` or a
  `@ConditionalOnMissingBean` stub, because each builds or hides the choice in code, not configuration. `@Primary` or
  `@Qualifier` is right only when both must exist at once and callers pick one.
- Prove each property-selected bean with an `ApplicationContextRunner` spec: one case per value, one for the missing
  value, because a wrong bean choice otherwise ships with no failing test.
- Put `@ConditionalOnBean` and `@ConditionalOnMissingBean` only on auto-configuration classes, because the conditions
  see only the definitions processed so far, and only auto-configuration loads after every user bean.
- Declare each configuration class `@Configuration(proxyBeanMethods = false)` and pass collaborators as `@Bean` method
  parameters, never by calling another `@Bean` method, because without the proxy a direct call builds a second
  instance.
- Declare a `@Bean` method's return type as the most specific type it builds, because before creation the container
  and type-based conditions see only the declared type. Callers still inject the interface.
- Put `@EnableScheduling`, `@EnableAsync` and `@Enable*Auditing` on a dedicated `@Configuration`, never on the
  `@SpringBootApplication` class, because every slice test loads the main class and so turns them on.

## Spring settings

- Bind related settings to one `@Validated` `@ConfigurationProperties` record with Jakarta constraints, each key read
  in one place. Use `@Value` only for a lone scalar no other class reads, because scattered `@Value` reads each carry
  their own default and skip validation.
- Register a settings record with `@EnableConfigurationProperties` or `@ConfigurationPropertiesScan`, never as
  `@Component` or a `@Bean` method, because constructor binding does not apply to a record made that way.
- Prove with an `ApplicationContextRunner` that a missing and an invalid value fail startup, because otherwise a bad
  value shows only when the code first reads it.
- Read configuration only through binding or the `Environment`, as kebab-case keys under the app's own prefix. Never
  call `System.getenv` or put an env-var name in `@Value` or `@ConditionalOnProperty`, because that skips config-tree
  secrets and tests cannot override it. State both `havingValue` and `matchIfMissing` on `@ConditionalOnProperty`.
- Bind times and sizes as `Duration` or `DataSize` with the unit in the value (`2s`), never a `long` key named `*-ms`
  or `*-seconds`, because a bare number hides its unit and seconds bind silently as milliseconds.
- Give a secret or a required endpoint no default, so its absence fails startup, because a shipped default credential
  or blank key runs production insecure.
- Never hold a secret as a plain `String` record component. Wrap it in a type whose `toString` redacts it, because a
  record's `toString` prints every component into logs.
- Use no `@Profile` and no `application-<profile>.yml` for environments. Vary settings by environment variables or a
  config tree and features by `@ConditionalOnProperty`, because profile configuration leaks test doubles. Test
  settings live in `src/test/resources/application.yml`.

## Spring startup

- Limit `@PostConstruct` to checking injected state. Move I/O, calls to other beans, and thread or container starts to
  an `ApplicationRunner` or `SmartLifecycle`, because `@PostConstruct` runs inside the singleton creation lock and can
  deadlock.
- Run startup work that must finish before traffic in an `ApplicationRunner`. Hand later work to another thread from
  `@EventListener(ApplicationReadyEvent.class)` and return at once, because event listeners must not run long tasks.
- Make a component that starts and stops background work (a listener container, a consumer loop) a `SmartLifecycle`
  bean, never `new`-ed and started by hand, because a hand-started one misses the context's shutdown phases.

## Spring proxies and transactions

- Call a method with a proxied annotation (`@Transactional`, `@Async`, `@Retryable`, `@Cacheable`) only from another
  bean. Move it to a second bean, with no self-injection and no `AopContext`, because a `this` call skips the proxy and
  the annotation does nothing.

**Bad**: the call goes through `this`, so no transaction starts and a failed insert leaves the stock reduced.
```java
@Service
class LoanService {
    void lend(final long bookId) {
        this.reserveCopy(bookId);
    }

    @Transactional
    void reserveCopy(final long bookId) {
        jdbc.sql("UPDATE copies SET on_shelf = on_shelf - 1 WHERE book_id = ?").param(bookId).update();
        jdbc.sql("INSERT INTO reservations (book_id) VALUES (?)").param(bookId).update();
    }
}
```
**Good**: the transactional method lives on a second bean, so the call crosses the proxy.
```java
@Service
class LoanService {
    private final CopyReservations reservations;

    LoanService(final CopyReservations reservations) {
        this.reservations = reservations;
    }

    void lend(final long bookId) {
        reservations.reserve(bookId);
    }
}
// CopyReservations: a second @Service; its @Transactional reserve(bookId) holds both writes
```

- Put `@Retryable` on the `@Transactional` method or on a caller with no open transaction, never inside an outer
  transaction, because each attempt then joins a transaction already marked rollback-only.
- Put `@Transactional(readOnly = true)` on a service class whose methods mostly read, and plain `@Transactional` on
  each write method, because without the read-only default every query pays for dirty checking.

## JPA fetching

- Declare every `@ManyToOne` and `@OneToOne` `fetch = FetchType.LAZY`, because the eager default loads the associated
  row on every query, often as one extra select per result.
- Fetch each association the use case navigates in the owner's query (`join fetch`, `@EntityGraph` or a DTO
  projection), never lazily per result element, because each element then costs one more select (N+1).
- Fetch at most one collection per query. Load each further collection with its own query or `@BatchSize`, because two
  collection fetches multiply rows or throw `MultipleBagFetchException`.
- Set `spring.jpa.open-in-view: false`, because the default keeps the persistence context open through rendering, and
  lazy loads there run unplanned queries outside the service's transaction.

## JPA queries and paging

- Bound every query whose result grows with the data with a `Pageable`, `Limit` or SQL `LIMIT`. Never return the whole
  table as a `List`, because each call loads it into the heap. A list bounded by its parent is fine.
- Never page a query that fetches a collection. Page the owner ids, then fetch the collection for those ids, because
  Hibernate otherwise loads every matching row and cuts the page in memory. Paging a fetched to-one is fine.

**Bad**: Hibernate reads every matching loan and its renewals, then cuts the page in memory.
```java
@Query("select l from Loan l left join fetch l.renewals where l.status = :status order by l.dueOn, l.id")
Page<Loan> findWithRenewals(LoanStatus status, Pageable page);
```
**Good**: SQL cuts the page on the ids. The second query sorts again, because `IN` does not keep their order.
```java
@Query("select l.id from Loan l where l.status = :status order by l.dueOn, l.id")
Slice<Long> findIdsByStatus(LoanStatus status, Pageable page);

@Query("select l from Loan l left join fetch l.renewals where l.id in :ids order by l.dueOn, l.id")
List<Loan> findWithRenewalsByIdIn(Collection<Long> ids);
```

- End the `ORDER BY` of every paged or limited query on a unique column, such as the id, because rows that tie have no
  defined order and pages skip or repeat them.

## JPA writes

- Change rows that all take the same new value with one `@Modifying` update or delete, never by loading entities and
  setting fields in a loop, because dirty checking loads every row and sends one `UPDATE` each. Write
  `update versioned` so the statement increments `@Version`.
- Write `@Modifying(flushAutomatically = true, clearAutomatically = true)` on every modifying repository query,
  because the bulk statement bypasses the persistence context: it misses pending changes and leaves managed entities
  stale.
- Stop a bulk update or delete whose target list is empty before it runs, because a filter added only for a non-empty
  list turns an empty list into every row.
- Set `spring.jpa.properties.hibernate.jdbc.batch_size`, starting between 10 and 50, because the default sends every
  insert and update in its own round trip. Hibernate ignores the `batch-size` and `batchSize` spellings.
- Map the id of an entity inserted in bulk as `GenerationType.SEQUENCE` with a `@SequenceGenerator` whose
  `allocationSize` equals the sequence's `INCREMENT BY`, never `IDENTITY`, because Hibernate cannot batch `IDENTITY`
  inserts. Declare the key column `GENERATED BY DEFAULT AS IDENTITY (INCREMENT BY 50)`, never `GENERATED ALWAYS`,
  which rejects the ids Hibernate assigns.

## JPA entities and the pool

- Give every entity that two requests can update a `@Version` field, never set by hand, because without it the later
  edit silently overwrites the earlier.
- Base an entity's `equals` and `hashCode` on its immutable `@NaturalId`, compared with `instanceof` and accessors.
  Never use the generated id, a mutable field or `getClass()`, because the id appears only on persist and a lazy proxy
  fails `getClass()`.
- An entity is a non-final class with mutable persistent fields and an id that is `null` before persist, because JPA
  requires it. A DTO or projection is not an entity, and a method that may find nothing still returns `Optional`.
- Run Hikari as a small fixed pool: `maximum-pool-size` from a load test, starting near twice the database's cores, a
  few dozen at most, and no `minimum-idle`, because surplus connections contend and lower throughput.

## TypeScript types

- Keep `strict` and `strictTemplates` on and fix the type error, never set a strict flag to `false`, because a
  disabled check lets null and type errors through to runtime.
- Type a value of unknown shape as `unknown` and narrow it, never `any`, because `any` turns off checking on every use.
  An `any` a fix cannot remove takes a suppression scoped to one declaration, with a comment saying why.
- Add a check or fix the type; never silence the compiler with a non-null `!` or an `as` cast, because each hides a
  runtime crash the compiler could catch. Check a value against a type with `satisfies`, and narrow a union by its
  discriminant, `in`, `typeof` or an `isX` predicate.
- End a `switch` over a union with `const _exhaustive: never = x` in the default arm, because without it a new variant
  compiles with no case.
- Derive frontend DTO types from the backend's OpenAPI schema, never a hand-written parallel type, because a copy
  drifts when the schema changes.

## Angular components

- Write standalone components, never an NgModule, and omit `standalone: true`, which is the default, because NgModule
  declarations hide each component's dependencies.
- Keep every component on OnPush: set it on Angular 21, omit it on 22 and later. Never add `Eager`, `Default` or
  Zone.js, and remove the `Eager` the v22 migration adds, because an eager component re-checks its whole subtree on
  every event.
- Hold component state in `signal()` and derived state in `computed()`. Use `effect()` only for side effects, never to
  copy state, because a hand-synced copy stays stale when its source loads later.

**Bad**: `visibleLoans` is a copy one handler syncs. When the loans load after the member picks a branch, the list
stays empty. An `effect()` that calls `.set()` makes the same copy.
```ts
readonly loans = signal<Loan[]>([]);
readonly branch = signal('all');
readonly visibleLoans = signal<Loan[]>([]);

onBranchChange(branch: string): void {
  this.branch.set(branch);
  this.visibleLoans.set(this.loans().filter((loan) => branch === 'all' || loan.branch === branch));
}
```
**Good**: the list is derived from both signals, so it is right whichever changes first.
```ts
readonly loans = signal<Loan[]>([]);
readonly branch = signal('all');
readonly visibleLoans = computed(() =>
  this.loans().filter((loan) => this.branch() === 'all' || loan.branch === this.branch()),
);

onBranchChange(branch: string): void {
  this.branch.set(branch);
}
```

- Declare inputs, outputs and two-way bindings with `input()`, `output()` and `model()`, queries with `viewChild()`,
  and host bindings in `host: {}`, never the `@Input`, `@Output`, `@ViewChild`, `@HostBinding` or `@HostListener`
  decorators, because decorator inputs are not signals that `computed()` can read.
- Inject with `inject()` in a field initialiser, never through constructor parameters, because constructor injection
  does not work in functional guards and interceptors, and the code ends up with two styles.
- Bind a subscription that outlives one HTTP call with `takeUntilDestroyed()`, or render it with the `async` pipe,
  because an unbound subscription keeps a destroyed component alive. Call `takeUntilDestroyed()` without a
  `DestroyRef` only in a constructor or field initialiser.

## Angular templates

- Use `@if`, `@for` with `track`, `@switch`, `[class.x]` and `[style.x]`, never `*ngIf`, `*ngFor`, `ngClass`,
  `ngStyle` or `CommonModule`, because the directives add runtime cost and `@for` without a stable `track` rebuilds
  the DOM.
- Make anything clickable a `<button type="button">`, or an `<a>` when it navigates, never a clickable `div`, `span`
  or `tr`, because a `div` cannot take focus and a bare `<button>` submits its form.
- Give an icon-only button an `aria-label` or visually hidden text, not only a `title`, because assistive technology
  exposes `title` inconsistently and keyboard and touch users never see it.
