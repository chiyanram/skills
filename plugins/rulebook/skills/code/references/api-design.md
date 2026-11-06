# API design

How an HTTP API pages its lists, how it changes without breaking clients, and where its version goes. Read it when you
write or review a list endpoint, a page response, a change to a published request or response type, a client of
another service, or a request mapping's path.

Contents: Rules · When X, use Y · Good / Bad (AP2, AP4, AP5) · Decided edges · Review checks

## Rules

- **AP1** — Paginate every list endpoint from its first release, with a documented default and maximum page size, and
  cap a larger request at the maximum, because adding pagination later breaks clients that read the whole list.
- **AP2** — Page with an opaque cursor that the client returns unchanged, absent on the last page, not an offset,
  because an offset skips or repeats rows when data changes and slows on deep pages.
- **AP3** — Return every page in one shape across the API, `items` plus a `next` cursor, because a different shape per
  endpoint makes every client write its own pager.
- **AP4** — Change a published API only compatibly: add optional fields; never remove, rename or retype a field,
  change its meaning or make an optional input required, because clients built on the old contract break.
- **AP5** — Make each client of another service ignore unknown response fields and map an unknown enum value to a
  fallback that every use handles, because a compatible addition on the server otherwise breaks the client.
- **AP7** — Skip and log a record in another service's response that the client cannot read, never fail the whole
  batch, because one unreadable record otherwise stops every record behind it.
- **AP6** — Put the major version in every path from the first release (`/v1/…`); add `/v2` only for a change AP4
  forbids, because clients and gateways route on the URL, and a late version moves every URL.

## When X, use Y

| the API has | use | why |
|---|---|---|
| an endpoint that returns a collection | a page from the first release, with a default and a maximum size; a larger request capped at the maximum (AP1) | pagination added later breaks every client that read the whole list |
| the next page to point at | an opaque cursor, absent on the last page (AP2) | an offset skips or repeats rows when data changes |
| a page response | `items` and `next`, the same on every endpoint (AP3) | one client pager works for the whole API |
| a new piece of data in a published response | a new optional field beside the old ones (AP4) | old clients ignore it and keep working |
| a field to rename, retype or remove | a new field, with the old one kept (AP4) | a rename is a removal for every old client |
| a client DTO for another service's response | unknown fields ignored and an enum with a fallback value (AP5) | the server may add both without a new version |
| a fallback enum value | a branch for the fallback at every use (AP5) | an unhandled fallback crashes the client where it is used |
| a record in another service's response that the client cannot read | the record skipped and logged, the rest processed (AP7); a consumed message goes to MS4 in `messaging.md` | one unreadable record otherwise stops the batch |
| a client that reads a resource and sends it back with PUT | unknown fields and the raw enum string kept and sent back (AP5) | dropping them erases data the client does not know |
| a new API | `/v1/` at the start of every path (AP6) | the version is in the URL that clients and gateways route on |
| a change that AP4 forbids | a `/v2/` path beside `/v1/` (AP6) | old clients keep `/v1/` until they move |

## Good / Bad

### AP2 — An opaque cursor, not an offset

**Bad**
```java
@GetMapping("/v1/invoices")
InvoicePage list(
        @RequestParam(defaultValue = "0") @PositiveOrZero final int offset,
        @RequestParam(defaultValue = DEFAULT_PAGE_SIZE) @Positive final int size) {
    return invoices.page(offset, Math.min(size, MAX_PAGE_SIZE));
}
```
Each page is `OFFSET n` in SQL. An invoice created between two requests shifts every row, so the client sees one row
twice. Page 5,000 makes the database read and drop every row before it.

**Good**
```java
@GetMapping("/v1/invoices")
InvoicePage list(
        @RequestParam(required = false) final String cursor,
        @RequestParam(defaultValue = DEFAULT_PAGE_SIZE) @Positive final int size) {
    return invoices.page(Cursor.parse(cursor), Math.min(size, MAX_PAGE_SIZE));
}
```
`Cursor.parse` decodes the opaque cursor into the last id of the previous page, or the first page when it is absent.
The service reads `WHERE id > :last ORDER BY id LIMIT :size` and sets `next` only when more rows remain. A
`@JsonInclude(NON_NULL)` on the page leaves `next` out of the last page, not `null`.

### AP4 — Add a field; never rename or retype one

The published response has `number`, `customerName` and `total` as a decimal.

**Bad**
```java
record InvoiceResponse(
        String number,
        String customer,
        Money total) {}
```
Every old client reads `customerName` and finds nothing, and its `total` parser fails on an object.

**Good**
```java
record InvoiceResponse(
        String number,
        String customerName,
        BigDecimal total,
        Money totalWithCurrency) {}
```
The new data is a new field. Old clients ignore it, and new clients read `totalWithCurrency`.

### AP5 — A tolerant client DTO

**Bad**
```java
record ShipmentResponse(
        String trackingNumber,
        Status status) {
    enum Status { CREATED, IN_TRANSIT, DELIVERED }
}
```
When the carrier adds `RETURNED`, the client cannot read any response with that status.

**Good**
```java
@JsonIgnoreProperties(ignoreUnknown = true)
record ShipmentResponse(
        String trackingNumber,
        @JsonFormat(with = JsonFormat.Feature.READ_UNKNOWN_ENUM_VALUES_USING_DEFAULT_VALUE) Status status) {
    enum Status { CREATED, IN_TRANSIT, DELIVERED, @JsonEnumDefaultValue UNKNOWN }
}
```
A new field is ignored, and a new status reads as `UNKNOWN`, which the caller handles as one more case.

## Decided edges

- **Skip when** a small collection is paged in memory: an in-memory page satisfies AP1 while the collection is
  small. — **Do not skip when** the endpoint returns the whole collection with no page size. — **Confidence** high
- **Skip when** a user must jump to page N of a bounded result: an offset is allowed (AP2). — **Do not skip when**
  clients only move to the next or the previous page. — **Confidence** high
- **Skip when** a paged query never reaches an API client, such as a batch job: PS5's ordered page in
  `persistence.md` is enough (AP2). — **Do not skip when** the page is returned to an API client. — **Confidence**
  high
- **Skip when** a client only reads the response: the enum's fallback value is enough (AP5). — **Do not skip when**
  the client sends the resource back with PUT: it keeps unknown fields (`@JsonAnySetter`) and the raw enum string, and
  sends them back. — **Confidence** high

## Review checks

Walk every request mapping, page response type, published request or response type, and client DTO added or changed
in the diff.

- [ ] AP1 — `grep -rn -A3 "@GetMapping"` in controllers, and read each return type. A `List`, `Set` or array of
  resources, or a page size with no default or no maximum, is a finding.
- [ ] AP2 — `grep -rnE "\b(offset|skip|page|pageNumber)\b|Pageable|PageRequest\.of"` in controllers. An offset or page
  number outside the jump-to-page edge is a finding, and so is a cursor a client could build, such as a raw id.
- [ ] AP3 — For each page response type, read its fields. A page without `items` and `next`, or with other names for
  them, is a finding.
- [ ] AP4 — `git diff <base>` over every type serialized in a released request or response, whatever its name. A
  removed, renamed or retyped field, a changed meaning, or a new required input field is a finding.
- [ ] AP5 — For each DTO that reads another service's response, find unknown fields ignored
  (`@JsonIgnoreProperties(ignoreUnknown = true)`, or a mapper with `FAIL_ON_UNKNOWN_PROPERTIES` off, as Spring Boot's
  is) and a fallback on each enum. Either one missing is a finding, and so is a `switch` or index on the enum with no
  branch for the fallback.
- [ ] AP7 — For each reader of another service's response that holds many records, a parse failure that fails the
  whole batch is a finding.
- [ ] AP6 — `grep -rnE '@(Request|Get|Post|Put|Patch|Delete)Mapping\(((value|path) *= *)?"/'`, and join each
  method path to its class-level prefix. A full path that does not start with `/v<major>/`, or a new major version for
  a change AP4 allows, is a finding.
