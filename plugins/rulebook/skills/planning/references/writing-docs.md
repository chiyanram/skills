# Writing docs

What a project doc may claim, where each fact lives, and which spec a change updates. Read it when you write or review
a design, a spec, a guide or a README.

Contents: Rules · When X, use Y · Good / Bad (WD1, WD2, WD4, WD5) · Decided edges · Review checks

## Rules

- **WD1** — Write no `[confirmed: …]` stamp or other in-text verification marker; give a claim that needs proof a cite
  that a check can run, because stamps decay, and a stamped claim tells readers not to check.
- **WD2** — Write no count that changes as a side effect of unrelated work; a stable, deliberate fact (a language
  version, a port, a time-to-live) may stay, because such counts go stale when unrelated work changes them.
- **WD4** — Write the operational fact even when it is unflattering, because a reassuring false line is the worst line
  a doc can carry: readers act on it and stop checking.
- **WD5** — For a bug, correct the spec it violates; for a chore, put problem, scope and criteria in its work item;
  write a new spec for new behaviour, because bug-fix specs split one policy in two.
- **WD7** — Keep each fact in one file and link to it; edit a generated doc's source, never the doc, because each
  restated copy must also change and the generator overwrites a hand edit.

## When X, use Y

| the doc line is | use | why |
|---|---|---|
| a claim about code, marked with a date, a tick or `[confirmed]` | drop the marker; cite the `path:line`, command or test that proves it (WD1) | a marker records one past check; a cite lets the next reader check again |
| a count of things that grow: files, tests, endpoints, modules, rules | delete it, or name the command that counts them (WD2) | copied state rots (firstmate :374); a one-command lookup belongs to the environment (writing-for-agents :79) |
| a value someone chose on purpose: a version, a port, a limit, a time-to-live | keep it (WD2) | it changes only by a deliberate edit |
| a limit, a failure mode or a gap that a reader will hit | state it plainly, where the reader looks (WD4) | say the unflattering thing where it is true (writing-docs :56); document known gotchas (documentation-and-adrs :134) |
| a fact that another file already holds | a link to that file (WD7) | one meaning, one source of truth (writing-for-agents :78); one file is the single owner (firstmate :55) |
| a file a tool generates | edit the source and run the generator again (WD7) | generated docs are never hand-edited (openclaw :38); generated output is read only (plinth :59) |
| a change that fixes a bug against a spec | correct that spec in place (WD5) | the spec is a living document, updated when decisions change (spec-driven :212-214) |
| a change that no spec owns: a chore | problem, scope and criteria in the work item (WD5) | no spec owns the behaviour, so no spec changes |
| a change that adds behaviour the product lacks | a new spec (WD5) | the new behaviour has no spec to correct |

`writing-for-agents` is mattpocock `skills/productivity/writing-for-agents/SKILL.md`, `writing-docs` is mattpocock
`.agents/writing-docs.md`, `firstmate` is kunchenguid-firstmate `AGENTS.md`, `openclaw` is openclaw-openclaw
`docs/AGENTS.md`, `plinth` is jabrena-plinth `skills/200-agents-md/references/200-agents-md.md`,
`documentation-and-adrs` is addy `skills/documentation-and-adrs/SKILL.md` and `spec-driven` is addy
`skills/spec-driven-development/SKILL.md`; `:N` is the line.

Operator preference, 2026-10-31 (SRC2), in whole or in part: WD1, WD4 and WD5.

## Good / Bad

### WD1 — A cite, not a stamp

**Bad** (neutral)
```markdown
A loan renews at most twice. [confirmed: 2026-03-14]
The overdue job runs every night. ✔ verified
```
The marker says someone looked once. When the limit changes, the stamp still reads as proof, so nobody looks again.

**Good** (neutral)
```markdown
A loan renews at most twice (`MAX_RENEWALS` in `src/loans/policy.py:12`).
The overdue job runs every night (`schedule` in `config/jobs.yaml:7`).
```
Each claim names where a check can open it. The cite check (SR3) fails when the symbol moves.

### WD2 — Counts that grow go; chosen values stay

**Bad** (neutral)
```markdown
## Catalog service
The service has 14 endpoints, 9 modules and 212 tests.
It listens on port 8081 and caches title lookups for 10 minutes.
```
The next unrelated change adds an endpoint or a test, and the first line is false.

**Good** (neutral)
```markdown
## Catalog service
It listens on port 8081 and caches title lookups for 10 minutes,
so a new title can take 10 minutes to appear in search.
The [API description](api/catalog.yaml) lists every endpoint.
```
The port and the cache time are chosen values. The endpoint list has one owner, and the doc links to it.

### WD4 — State the limit the reader will hit

**Bad** (neutral)
```markdown
Reservations are always filled in queue order.
```
A reader promises this to a member. It is false across branches.

**Good** (neutral)
```markdown
Reservations are filled in queue order within one branch.
Across branches, the first branch to scan a returned book fills its own
reservation, so a later reservation at that branch can be filled first.
```
The line is less reassuring and true, so the reader can plan for the gap.

### WD5 — A bug corrects the spec it violates

**Bad** (neutral)
```text
specs/loan-renewal.md        A loan renews at most twice.
specs/fix-ebook-renewal.md   E-book loans ignored the renewal limit.
                             E-book loans also renew at most twice.
```
The renewal policy now lives in two specs. The next change to the limit updates one and misses the other.

**Good** (neutral)
```text
specs/loan-renewal.md        A loan renews at most twice, in every format,
                             e-books included.
```
The bug fix corrects the one spec that owns the policy. The work item links to it.

## Decided edges

- **Skip when** the claim is in a spec: a spec names no paths, so state the behaviour there and put the cite in the
  design (PD6). — **Do not skip when** the claim is in a design, guide or README: cite it (WD1). — **Confidence** high
- **Skip when** a date is part of the fact itself: the decision date of a decision record, a release date. — **Do not
  skip when** a date, tick or name only says that someone checked a claim (WD1). — **Confidence** high
- **Skip when** the number is a value someone chose: a version, a port, a limit, a time-to-live. — **Do not skip
  when** the number counts things that other work adds or removes: files, tests, endpoints, modules, rules (WD2). —
  **Confidence** high
- **Skip when** the doc that owns the weakness already states it: link to it (WD7). — **Do not skip when** any doc
  states the reassuring opposite: correct that line (WD4). — **Confidence** high
- **Skip when** a fact costs an expensive lookup (several files, a slow command) and the copy names its owner
  (writing-for-agents :79). — **Do not skip when** the lookup is one file or one command: link it (WD7). —
  **Confidence** medium
- **Skip when** the bug is in behaviour no spec owns: treat it as a chore, and the work item holds problem, scope and
  criteria. — **Do not skip when** the fix changes what a spec promises, or shows the spec was wrong: correct that
  spec in place (WD5). — **Confidence** medium

## Review checks

Walk every doc file that the change adds or edits: designs, specs, guides, READMEs and decision records.

- [ ] WD1 — Search the diff for `[confirmed`, `[verified`, `verified on`, `✔` and dated "checked" notes. Each one is a
  finding; ask for a cite that a check can run.
- [ ] WD2 — Each number in an added line either is a chosen value or is a finding. A count of files, tests,
  endpoints, modules or rules is a finding.
- [ ] WD4 — For each added claim of "always", "never", "only" or "guaranteed", open the code or config it describes.
  A claim the code does not hold is a finding.
- [ ] WD5 — A new spec whose subject is a bug fix is a finding: name the spec it should correct. A chore with no
  problem, scope or criteria in its work item is a finding.
- [ ] WD7 — For each added fact, search the docs for the same fact. A second copy without a link to its owner is a
  finding. An edit to a generated file with no matching edit to its source is a finding.
