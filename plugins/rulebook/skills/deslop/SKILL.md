---
name: deslop
description: Use when an implemented branch is ready for review and its diff needs a behaviour-neutral cleanup first — restating comments, defensive checks for states that cannot occur, type laundering, one-use indirection, unnamed fallbacks and shims, dead code, deep nesting, and style that fights the surrounding file. Diff-scoped; never a repo-wide pass, never a replacement for review.
---

# Deslop

Clean the branch diff after implementation and before review. Fix only what is provably behaviour-neutral; report the
rest.

```
implement ──▶ deslop ──▶ verify ──▶ review
               └── behaviour-neutral only, never a correctness pass
```

## Rules

- **DS13** — Run deslop on the branch diff only, before review and never instead of it; fix only behaviour-neutral
  cleanups and report the rest, because an unreviewed behaviour change ships untested.
- **DS5** — When an API has no external consumer, migrate every caller and delete the old path; leave no compatibility
  shim, because two live paths must both be maintained and drift apart.
- **DS7** — Remove dead code, vestigial parameters, commented-out blocks and `// removed` shims in the code you touch,
  because dead code confuses future readers and agents.
- **DS8** — Add no null check or try/catch to silence a failure on a trusted path; fix the cause and search for the
  same pattern elsewhere, because a silencing guard leaves the real bug in place.
- **DS9** — Turn nesting of three or more levels into guard clauses or early returns, and write no nested ternary,
  because deep nesting and nested ternaries hide the control flow.

## Steps

1. **Scope the pass.** Run `git diff $(git merge-base <default-branch> HEAD)...HEAD --stat`. That diff is the whole
   scope (DS13). Use the same base the review uses, so both look at one diff.
2. **Read the rules for each file kind** in the diff before you judge its hunks: the `code` references for the
   language, and the `testing` references for a test.
3. **Walk every hunk through every category** in the table below. The owner column names the rule that decides the
   case; the category is only where to look.
4. **Fix or report** each hit (see below).
5. **Verify.** Run the project's verify command for each module the pass edited; the project's `AGENTS.md` names it.
6. **Report** in one to three sentences on the merge request: what changed, what was left, and what the author must
   decide. Name the files. A clean diff still gets its line ("deslop: nothing to clean"), so a skipped pass and an
   empty one look different.

Done when every hunk of the diff has been checked against every category, every module the pass edited is green, and
the report line is posted.

| category | look for | owner |
|---|---|---|
| comment slop | a comment that restates the code, a banner, a divider | CM1, CM2, CM3 (`../code/references/comments.md`) |
| defensive checks | a null check, `try`/`catch` or guard for a state the types or the callers exclude | DS8 · TY1 (`../code/references/types.md`) |
| swallowed failure | a `catch` that continues quietly or returns an empty result | ER3 (`../code/references/errors.md`); always a report, never a fix |
| fake fallback | on an error or missing config, production code that returns a mock, stub, fake or sample data instead of failing | DS8; remove it and fail with the real error |
| type laundering | a cast through `Object` or a raw type, a new `@SuppressWarnings`, untrusted JSON held as `Map<String, Object>` past the adapter, a string where an enum exists | TY10, TY6 (`../code/references/types.md`) · CM7 (`../code/references/comments.md`) · SE5 (`../code/references/security.md`) |
| one-use indirection | a helper, wrapper or variable that adds no domain meaning | DS4 (`../code/references/smells.md`); keep anything that carries a domain name |
| fallbacks and shims | a retry, default, alias or second code path with no named contract and no removal plan | DS5 · DS7 · CC8 (`../code/references/concurrency.md`) |
| dead code | an unused member, a vestigial parameter, a commented-out block | DS7 |
| deep nesting | three or more levels, a nested ternary | DS9 |
| style drift | naming, control flow, imports or formatting that fight the file around them | the `code` reference for the file's language |
| test shape | labelled blocks and feature names that fight the spec around them | U2 ([`unit-tests.md`](../testing/references/unit-tests.md)) |

### Fix or report

- **Fix inline** only a trivial, provably behaviour-neutral cleanup: a deleted comment, an inlined one-use variable, a
  `final` on a field the branch added (TY4), an import.
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

## Decided edges

- **Skip when** callers sit outside the repo's control (a published API, stored data, a webhook URL): expand, migrate,
  then contract (ParallelChange): remove the old path only after every consumer has migrated (DS5). — **Do not skip
  when** every caller is in the repo. — **Confidence** high
- **Skip when** the value crosses a trust boundary, such as request input or a third-party response: validate it there
  (ER6, `../code/references/errors.md`). — **Do not skip when** the guarded value comes from an injected field or an
  in-repo caller (DS8). — **Confidence** high

## Review checks

Walk every hunk of the branch diff (`git diff $(git merge-base <default-branch> HEAD)...HEAD`) and the pass's report.

- [ ] DS13 — The pass touched only files in the branch diff, ran before review, and every edit it made is
  behaviour-neutral. An edit outside the diff, or one that changes control flow, error handling or a fallback, is a
  finding.
- [ ] DS5 — For each API the branch replaces with no external consumer, grep for callers of the old path
  (`grep -rn '<old name>'`). A caller left on it, or a kept compatibility shim, is a finding.
- [ ] DS7 — An unused member, a vestigial parameter, a commented-out block or a `// removed` note in a touched file is
  a finding.
- [ ] DS8 — A new null check or `try`/`catch` on a value from an injected field or an in-repo caller is a finding.
  So is a fallback to a mock, stub, fake or sample data outside test code.
- [ ] DS9 — Nesting of three or more levels that a guard clause or early return could flatten is a finding, and so is
  a nested ternary.
