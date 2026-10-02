# Brief — Good/Bad pass (shared by the 4 parallel parts)

Write ONLY your own output file (named in your prompt). No commits, no GitHub/GitLab edits. Absolute paths, never `cd`.
AP=/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3 — behind master: run `git -C AP fetch -q origin master`
once, then read code ONLY via `git -C AP show origin/master:<path>` and search via `git -C AP grep -n … origin/master -- <pathspec>`.

Rules to cover: rows in /Users/chiyanram/workspace/skills/research/19-approved-rules.md whose id is in YOUR id list and whose
status starts with APPROVED. Reuse sample lists in research/15-testing-content-audit.md, 21-mutation-and-property.md,
25-gherkin-to-every-tier.md, 28-smoke-e2e-disposition.md (same folder).

Format (rule GB1): each Good and Bad is REAL code copied from agent-platform origin/master, ≤15 lines, with `path:start-end`
underneath and one line on why it is good/bad against THIS rule. If master has no real example, write a minimal ADAPTED one in our
stack (Spock 2.4/Groovy, Java 25, Playwright TS, real class names only) labelled `adapted from <source>` and marked
`NEEDS COMPILE CHECK`. Verify every path + line range by printing it before using it. Bad may be "n/a" with a reason.

WRITE INCREMENTALLY: create your file first with a heading, then append each rule's entry as soon as it is done (so a stall
keeps the work). Keep each tool call small; do not batch huge greps.

Entry shape:
### <ruleId> — <rule ≤15 words>
**Good** (real|adapted) ```lang … ``` `path:lines` — why
**Bad** (real|adapted|n/a) ```lang … ``` `path:lines` — why

End your file with: counts (real / adapted / missing), rules with no real Good on master, rules the codebase widely breaks (with a
count). Report a 4-line summary.
