# Writing docs

What a project doc may claim, where each fact lives, and which spec a change updates. Read it when you write or review
a design, a spec, a guide or a README, or decide which spec a change updates.

## Rules

- Give a claim that needs proof a cite a check can run (`path:line`, a command or a test), and write no
  `[confirmed: …]` stamp, tick or dated "checked" note, because a stamp records one past check and tells readers not to
  check again. A date that is part of the fact, such as a decision record's date, stays. In a spec, state the
  behaviour and put the cite in the design.
- Leave out counts that change as a side effect of other work (files, tests, endpoints, modules, rules), or name the
  command that counts them, because such counts go stale. A value someone chose on purpose, such as a version, a port,
  a limit or a time-to-live, stays.
- Write the operational fact even when it is unflattering, where the reader looks, because a reassuring false line is
  the worst line a doc can carry: readers act on it and stop checking.
- Keep each fact in one file and link to it, because every restated copy must change too. A copy of an expensive
  lookup (several files, a slow command) may stay if it names its owner. Edit a generated doc's source and run the
  generator again, because the generator overwrites a hand edit.
- For a bug, correct the spec it violates, in place. For a chore, or a bug in behaviour no spec owns, put problem,
  scope and criteria in its work item. Write a new spec only for new behaviour, because bug-fix specs split one policy
  in two.

## Good / Bad

### A cite, not a stamp

**Bad**
```markdown
A loan renews at most twice. [confirmed: 2026-03-14]
The overdue job runs every night. ✔ verified
```
The marker says someone looked once. When the limit changes, the stamp still reads as proof, so nobody looks again.

**Good**
```markdown
A loan renews at most twice (`MAX_RENEWALS` in `src/loans/policy.py:12`).
The overdue job runs every night (`schedule` in `config/jobs.yaml:7`).
```
Each claim names where a check can open it. The cite check fails when the symbol moves.

### Counts that grow go; chosen values stay

**Bad**
```markdown
## Catalog service
The service has 14 endpoints, 9 modules and 212 tests.
It listens on port 8081 and caches title lookups for 10 minutes.
```
The next unrelated change adds an endpoint or a test, and the first line is false.

**Good**
```markdown
## Catalog service
It listens on port 8081 and caches title lookups for 10 minutes,
so a new title can take 10 minutes to appear in search.
The [API description](api/catalog.yaml) lists every endpoint.
```
The port and the cache time are chosen values. The endpoint list has one owner, and the doc links to it.

### State the limit the reader will hit

**Bad**
```markdown
Reservations are always filled in queue order.
```
A reader promises this to a member. It is false across branches.

**Good**
```markdown
Reservations are filled in queue order within one branch.
Across branches, the first branch to scan a returned book fills its own
reservation, so a later reservation at that branch can be filled first.
```
The line is less reassuring and true, so the reader can plan for the gap.

### A bug corrects the spec it violates

**Bad**
```text
specs/loan-renewal.md        A loan renews at most twice.
specs/fix-ebook-renewal.md   E-book loans ignored the renewal limit.
                             E-book loans also renew at most twice.
```
The renewal policy now lives in two specs. The next change to the limit updates one and misses the other.

**Good**
```text
specs/loan-renewal.md        A loan renews at most twice, in every format,
                             e-books included.
```
The bug fix corrects the one spec that owns the policy. The work item links to it.

## Review

Walk every doc file the change adds or edits: designs, specs, guides, READMEs and decision records.

Each line is a finding, a blocker unless marked (warning).

- `[confirmed`, `[verified`, `verified on`, `✔` or a dated "checked" note in the diff, other than a date that is part of
  the fact.
- A number in an added line that counts files, tests, endpoints, modules or rules.
- An added "always", "never", "only" or "guaranteed" that the code or config it describes does not hold.
- A second copy of a fact with no link to its owner, or an edit to a generated file with no edit to its source.
- A new spec whose subject is a bug fix, or a chore with no problem, scope or criteria in its work item.
