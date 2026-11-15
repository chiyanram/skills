# HTTP APIs

Read this when you write or review a list endpoint, a change to a published request or response, a client of another
service, or a request path.

## Lists

- Page every list endpoint from its first release, with a documented default and maximum page size. Cap a larger
  request at the maximum. Pagination added later breaks clients that read the whole list. A small collection paged
  in memory is enough; an endpoint that returns the whole collection is not.
- Page with an opaque cursor that the client sends back unchanged, absent on the last page, never an offset or page
  number. An offset skips or repeats rows when data changes. A cursor the client could build, such as a raw id, is
  not opaque. Use an offset only when a user must jump to page N of a bounded result. A paged query that never
  reaches an API client, such as a batch job, needs only an ordered page.
- Return every page in one shape across the API: `items` plus a `next` cursor. A different shape per endpoint makes
  every client write its own pager.

**Bad**: an offset.
```java
@GetMapping("/v1/loans")
LoanPage list(@RequestParam(defaultValue = "0") @PositiveOrZero int offset,
              @RequestParam(defaultValue = DEFAULT_PAGE_SIZE) @Positive int size) {
    return loans.page(offset, Math.min(size, MAX_PAGE_SIZE));
}
```
A loan created between two requests shifts the rows, so the client sees one loan twice.

**Good**: an opaque cursor.
```java
@GetMapping("/v1/loans")
LoanPage list(@RequestParam(required = false) String cursor,
              @RequestParam(defaultValue = DEFAULT_PAGE_SIZE) @Positive int size) {
    return loans.page(Cursor.parse(cursor), Math.min(size, MAX_PAGE_SIZE));
}
```
`Cursor.parse` decodes the last id of the previous page. The query reads `WHERE id > :last ORDER BY id LIMIT :size`
and sets `next` only when more rows remain. `@JsonInclude(NON_NULL)` leaves `next` out of the last page.

## Changing a published API

- Change a published request or response only compatibly: add optional fields. Never remove, rename or retype a
  field, change its meaning, or make an optional input required, because clients built on the old contract break.
  To rename or retype, add a new field and keep the old one. This covers every serialized type, whatever its name.

## Versions

- Put the major version at the start of every path from the first release (`/v1/...`), joined with any class-level
  prefix. Clients and gateways route on the URL, so a late version moves every URL. Add `/v2/` beside `/v1/` only for
  a change the compatibility rule forbids, never for a compatible one.

## Clients of another service

- Make each client DTO ignore unknown fields and map an unknown enum value to a fallback. Handle the fallback at every
  `switch` or lookup on the enum. Otherwise a compatible addition on the server breaks the client.
- When the client reads a resource and sends it back with PUT, keep unknown fields (`@JsonAnySetter`) and the raw enum
  string, and send them back, because dropping them erases data the client does not know.
- Skip and log a record in another service's response that the client cannot read, and process the rest, because one
  bad record otherwise stops the batch. A consumed message follows [async-jobs.md](async-jobs.md).

**Bad**: a closed enum.
```java
record BookResponse(String isbn, Status status) {
    enum Status { ON_SHELF, ON_LOAN, LOST }
}
```
When the catalogue adds `IN_REPAIR`, the client cannot read any response with that status.

**Good**: a tolerant DTO.
```java
@JsonIgnoreProperties(ignoreUnknown = true)
record BookResponse(String isbn,
        @JsonFormat(with = JsonFormat.Feature.READ_UNKNOWN_ENUM_VALUES_USING_DEFAULT_VALUE) Status status) {
    enum Status { ON_SHELF, ON_LOAN, LOST, @JsonEnumDefaultValue UNKNOWN }
}
```
A new field is ignored. A new status reads as `UNKNOWN`, which the caller handles as one more case.
