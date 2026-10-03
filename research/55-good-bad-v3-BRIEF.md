# Brief — Good/Bad v3 (operator, 2026-10-03)

Replaces the "real code" parts of `31-good-bad-v2-BRIEF.md` and `00-reference-format.md` §Good/Bad rule 2.
Everything else in the v2 brief (house style, entry shape, ≤15 lines) still applies.

## Why

Our code does not follow the rules. A Good copied from it teaches the drift we are removing.
Rules come from reference projects and official docs, read in depth — never from our code.

## The rules

1. **A Good is never our code.** Write it to obey every approved rule in `19-approved-rules.md` (GB1a) and house style.
2. **Model the Good on a source.** Where a reference project or official doc has an example for the rule
   (pstack, mattpocock, addy, humanlayer, openclaw, plinth, Spring / Angular / OWASP docs), adapt that example
   to our domain and cite it: `modelled on <repo path:lines | doc URL §section>`. Open the source; never recall it.
   No source example exists → write it from the rule and label `written from rule <id>`.
3. **A Bad may be our code** (`agent-platform` `origin/master`, or a named past commit for a real past mistake),
   cited as `path:lines`. Prefer a real past mistake. A Bad that also breaks other rules says `also breaks: <ids>`.
4. **Domain names are ours** (workspace, agent, tool, session) so the example reads as our project, but the code shape
   comes from the rule and the source — not from our classes.
5. Every Good is marked `NEEDS COMPILE CHECK` until work item 1 compiles it.

## Entry shape

```
### <ruleId> — <rule ≤15 words>
**Good** (modelled on <source> | written from rule <id>)  ```lang … ```  — why it is right; what misreading it prevents
**Bad** (ours | adapted)  ```lang … ```  `path:lines` — what went wrong (#NNN if known)
```
