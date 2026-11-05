# Brief — Good/Bad v3 (operator, 2026-10-03) — follows ledger rows SRC1 and GB2

Replaces the "real code" parts of `31-good-bad-v2-BRIEF.md` and `00-reference-format.md` §Good/Bad rule 2.
Everything else in the v2 brief (house style, entry shape, ≤15 lines) still applies.
The ledger rows SRC1, GB2 and SEAM1 are written by the G10 session (#37); this brief applies them to #33.

## Why

Our code does not follow the rules, so it is never a Good and never a rule's source (SRC1).

## The rules (GB2)

1. **Bad = our real code**, copied from `agent-platform` at a pinned commit, cited `path:lines`.
   Prefer a real past mistake (a ticket, an MR round, a QA finding). If it also breaks other rules: `also breaks: <ids>`.
2. **Good = that same Bad, rewritten** to obey its rule, every other approved rule in `19-approved-rules.md`, and house
   style. Label it `rewritten from path:lines`. Same domain, same intent — only the violation (and anything else that
   breaks a rule) changes, so the reader sees exactly what the rule asks for.
3. **No Bad in our code for the rule** → both sides are `adapted from <source:line>`: an example from a reference project
   or official doc that you OPEN and cite (never recalled), moved into our domain names.
4. **≤15 lines per side.** The Good must compile against master → mark `NEEDS COMPILE CHECK` until work item 1 compiles it.
5. **Seams** in a Good follow SEAM1 (SOLID via ADR-0017 S-1..S-7: one job, record in / sealed out, decide or do,
   seams chain by exhaustive switch, no complex logic) and avoid the Fowler smells baseline
   (rameezk/skills `skills/code-review/martin-fowler-code-smells.md`).

## Entry shape

```
### <ruleId> — <rule ≤15 words>
**Bad** (ours)  ```lang … ```  `path:lines` @ <commit> — what went wrong (#NNN if known); also breaks: …
**Good** (rewritten from path:lines | adapted from source:line)  ```lang … ```  — what changed; what misreading it prevents
```
