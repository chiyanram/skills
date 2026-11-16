---
name: deslop
description: Use when an implemented branch is ready for review and its diff needs a behaviour-neutral cleanup first — restating comments, defensive checks for states that cannot occur, type laundering, one-use indirection, unnamed fallbacks and shims, dead code, deep nesting, and style that fights the surrounding file. Diff-scoped; never a repo-wide pass, never a replacement for review.
disable-model-invocation: true
---

# Deslop

Clean the branch diff after implementation and before review. Fix only what is provably behaviour-neutral; report the
rest. A person starts it with `/rulebook:deslop`; no crq lane runs it, until hand runs show it finds real things.

```
implement ──▶ deslop ──▶ verify ──▶ review
               └── behaviour-neutral only, never a correctness pass
```

## Rules

- **DS13** — Run deslop on the branch diff only, before review and never instead of it; fix only behaviour-neutral
  cleanups and report the rest, because an unreviewed behaviour change ships untested.
- **DS5** — When an API has no external consumer, migrate every caller and delete the old path; leave no compatibility
  shim, because two live paths must both be maintained and drift apart. When a caller sits outside the repo (a
  published API, stored data, a webhook URL), expand, migrate, then contract: remove the old path only after every
  consumer has moved.
- **DS7** — Remove dead code, vestigial parameters, commented-out blocks and `// removed` shims in the code you touch,
  because dead code confuses future readers and agents.
- **DS8** — Add no null check or try/catch to silence a failure on a trusted path; fix the cause and search for the
  same pattern elsewhere, because a silencing guard leaves the real bug in place.
- **DS9** — Turn nesting of three or more levels into guard clauses or early returns, and write no nested ternary,
  because deep nesting and nested ternaries hide the control flow.

## Steps

1. **Scope the pass.** Run `git diff $(git merge-base <default-branch> HEAD)...HEAD --stat`. That diff is the whole
   scope (DS13). Use the same base the review uses, so both look at one diff. Note its `--shortstat` line count.
2. **Read the rules for each file kind** in the diff before you judge its hunks: the `code` references for the
   language, and the `testing` references for a test.
3. **Walk every hunk through every category** in the table below. The owner column names the rule that decides the
   case; the category is only where to look.
4. **Fix or report** each hit (see below).
5. **Verify.** Run the project's verify command for each module the pass edited; the project's `AGENTS.md` names it.
6. **Report** in one to three sentences on the merge request: what changed, what was left, and what the author must
   decide. Name the files. A clean diff still gets its line ("deslop: nothing to clean"), so a skipped pass and an
   empty one look different. On the ticket, record the diff's line count before and after, and whether every
   evidence row still passes; after review, add how many style findings it raised. A person reads these numbers to
   decide whether cleanup goes back into the lanes.

Done when every hunk of the diff has been checked against every category, every module the pass edited is green, and
the report line is posted.

| category | look for | owner |
|---|---|---|
| comment slop | a comment that restates the code, a banner, a divider | `code` [Comments](../code/SKILL.md#comments) |
| defensive checks | a null check, `try`/`catch` or guard for a state the types or the callers exclude | DS8 · `code` [Types](../code/SKILL.md#types) |
| swallowed failure | a `catch` that continues quietly or returns an empty result | `code` [Errors](../code/SKILL.md#errors); always a report, never a fix |
| fake fallback | on an error or missing config, production code that returns a mock, stub, fake or sample data instead of failing | DS8; remove it and fail with the real error |
| type laundering | a cast through `Object` or a raw type, a new `@SuppressWarnings`, untrusted JSON held as `Map<String, Object>` past the adapter, a string where an enum exists | `code` [Types](../code/SKILL.md#types) and [Comments](../code/SKILL.md#comments) · [security.md](../code/security.md), Outside input |
| one-use indirection | a helper, wrapper or variable that adds no domain meaning | `code` [Where logic goes](../code/SKILL.md#where-logic-goes); keep anything that carries a domain name |
| fallbacks and shims | a retry, default, alias or second code path with no named contract and no removal plan | DS5 · DS7 · [concurrency.md](../code/concurrency.md), Retries |
| dead code | an unused member, a vestigial parameter, a commented-out block | DS7 |
| deep nesting | three or more levels, a nested ternary | DS9 |
| style drift | naming, control flow, imports or formatting that fight the file around them | the `code` skill's [stack.md](../code/stack.md) |
| test shape | labelled blocks and feature names that fight the spec around them | the `testing` skill's Spock notes |

### Fix or report

- **Fix inline** only a trivial, provably behaviour-neutral cleanup: a deleted comment, an inlined one-use variable, a
  `final` on a field the branch added (`code` Types), an import.
- **Report, never fix**, anything that touches control flow, error handling, a fallback, a cast that changes dispatch,
  or a type that crosses a module boundary. Review and the author decide those (DS13).
- When you cannot tell which side an edit falls on, report it.

## Good / Bad

### DS8 — Fix the cause; add no silencing guard

**Bad**
```java
private void applyInvoicing(ImportOrdersRequest request, List<Order> created, UUID createdBy) {
    if (invoiceService == null) {
        return;
    }
```
`invoiceService` is a constructor-injected final field that a test-only constructor sets to null. The trusted path
grows a null guard, and a wiring mistake skips invoicing without a sound.

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
One constructor and an injected final collaborator need no null guard. The request decodes to a sealed target at the
boundary.
