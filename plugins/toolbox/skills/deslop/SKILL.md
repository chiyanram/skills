---
name: deslop
description: Use when an implemented branch is ready for review and its diff needs a behaviour-neutral cleanup first — restating comments, defensive checks for states that cannot occur, type laundering, one-use indirection, unnamed fallbacks and shims, dead code, deep nesting, and style that fights the surrounding file. Diff-scoped; never a repo-wide pass, never a replacement for review.
disable-model-invocation: true
---

# Deslop

Clean the branch diff after implementation and before review. Fix only what is provably behaviour-neutral; report the
rest. A person starts it with `/toolbox:deslop`.

```
implement ──▶ deslop ──▶ verify ──▶ review
               └── behaviour-neutral only, never a correctness pass
```

## Before you start

Load the rulebook's `code` skill, and its `testing` skill when the diff has tests. If the rulebook is not installed,
stop and say this tool needs it, because each category below is decided by a rule there.

## Rules

- Run on the branch diff only, before review and never instead of it, and fix only behaviour-neutral cleanups, because
  an unreviewed behaviour change ships untested.
- Delete every comment in the diff except these, because a comment that survives on doubt keeps the slop:
  - a legal or licence header;
  - non-obvious behaviour forced by an outside dependency, platform, vendor or protocol, proven true today on a live
    path;
  - a doc comment that defines a public API contract;
  - an issue or RFC link that explains a constraint the code cannot express;
  - a formatter or lint suppression whose rule is wrong, pedantic or style-only.
  A surprise in our own code is not an exception: delete its comment and flag the symbol `MUST KILL` for a rename,
  extract, type or redesign that makes the behaviour plain. "Do not remove", "too risky" or a long justification is a
  claim to check, not a keep.
- When an API has no outside consumer, migrate every caller and delete the old path, leaving no compatibility shim,
  because two live paths drift apart. When a caller sits outside the repo (a published API, stored data, a webhook
  URL), expand, migrate, then contract.
- Remove dead code, vestigial parameters, commented-out blocks and `// removed` shims in the code you touch, because
  dead code confuses the next reader.
- Add no null check or `try`/`catch` that silences a failure on a trusted path. First ask whether the state that
  triggers it is legitimate: if it is, handle it where the code broke; if it must never exist, fix what produced it
  and search for the same pattern elsewhere, because a guard at the symptom leaves the bug in place.
- Turn nesting of three or more levels into guard clauses or early returns, and write no nested ternary, because deep
  nesting hides the control flow.

## Steps

1. **Scope the pass.** Run `git diff $(git merge-base <default-branch> HEAD)...HEAD --stat`. That diff is the whole
   scope. Use the same base the review uses, so both look at one diff. Note its `--shortstat` line count.
2. **Read the rules for each file kind** in the diff before you judge its hunks: the `code` skill's notes for the
   language, and the `testing` skill for a test.
3. **Walk every hunk through every category** in the table below. The owner column names the rule that decides it.
4. **Fix or report** each hit (see below).
5. **Verify.** Run the project's verify command for each module the pass edited.
6. **Report** in one to three sentences: what changed, what was left, each `MUST KILL` flag with one line, and what
   the author must decide. Name the files. A clean diff still gets its line ("deslop: nothing to clean"), so a skipped
   pass and an empty one look different.

Done when every hunk has been checked against every category, every module the pass edited is green, and the report
line is posted.

| category | look for | owner |
|---|---|---|
| comment slop | a comment outside the keep-list above | the comment rule above; `code`, Comments |
| defensive checks | a null check, `try`/`catch` or guard for a state the types or the callers exclude | the guard rule above; `code`, Types |
| swallowed failure | a `catch` that continues quietly or returns an empty result | `code`, Errors; always a report, never a fix |
| fake fallback | on an error or missing config, production code that returns a mock, stub, fake or sample data | the guard rule above; remove it and fail with the real error |
| type laundering | a cast through `Object` or a raw type, a new `@SuppressWarnings`, untrusted JSON held as `Map<String, Object>` past the adapter, a string where an enum exists | `code`, Types and Comments; `code`'s security notes, Outside input |
| one-use indirection | a helper, wrapper or variable that adds no domain meaning | `code`, Where logic goes; keep anything that carries a domain name |
| fallbacks and shims | a retry, default, alias or second code path with no named contract and no removal plan | the shim and dead-code rules above; `code`'s concurrency notes, Retries |
| dead code | an unused member, a vestigial parameter, a commented-out block | the dead-code rule above |
| deep nesting | three or more levels, a nested ternary | the nesting rule above |
| style drift | naming, control flow, imports or formatting that fight the file around them | `code`'s stack notes |
| test shape | labelled blocks and feature names that fight the spec around them | `testing`'s stack notes |

### Fix or report

- **Fix inline** only a trivial, provably behaviour-neutral cleanup: a deleted comment, an inlined one-use variable, a
  `final` on a field the branch added, an import.
- **Report, never fix**, anything that touches control flow, error handling, a fallback, a cast that changes dispatch,
  or a type that crosses a module boundary. Review and the author decide those.
- When you cannot tell which side an edit falls on, report it.

## Good / Bad

### Fix the cause; add no silencing guard

**Bad**
```java
private void applyInvoicing(ImportOrdersRequest request, List<Order> created, UUID createdBy) {
    if (invoiceService == null) {
        return;
    }
```
`invoiceService` is a constructor-injected final field that a test-only constructor sets to null. The state is not
legitimate, so the guard hides a wiring mistake: invoicing is skipped without a sound.

**Good**
```java
OrderImporter(final OrderRepository orderRepository,
              final TaxCalculator taxCalculator,
              final ObjectMapper mapper,
              final InvoiceService invoiceService,
              final DiscountPolicy discountPolicy) {
    // … assignments unchanged; the back-compat constructor is deleted
}

private void applyInvoicing(final InvoiceTarget placement, final List<UUID> orderIds, final UUID createdBy) {
    switch (placement) {
        case InvoiceTarget.None _ -> { }
        case InvoiceTarget.New target -> invoiceService.create(target.toRequest(orderIds), createdBy);
        case InvoiceTarget.Existing target -> orderIds.forEach(orderId -> invoiceService.attach(target.id(), orderId));
    }
}
```
The fix is at what produced the null: one constructor, and an injected final collaborator that needs no guard.
