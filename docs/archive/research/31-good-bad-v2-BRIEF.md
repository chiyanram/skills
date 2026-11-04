# Brief — Good/Bad v2 rewrite (operator feedback, 2026-10-02)

Rewrite YOUR part's Good/Bad file into a v2 file (names in your prompt). Write ONLY that v2 file, INCREMENTALLY (create it
with a heading first, append each rule as you finish it). No commits, no GitHub/GitLab edits. Absolute paths, never `cd`.
AP=/Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3 (behind master): `git -C AP fetch -q origin master`
once, then read code only via `git -C AP show origin/master:<path>` / `git -C AP grep -n … origin/master -- <pathspec>`.

New rules every GOOD example must obey (in addition to all rules in /Users/chiyanram/workspace/skills/research/19-approved-rules.md):
- GB1a: a Good obeys EVERY approved rule and house style, not only its own. If the real master code breaks any rule, rewrite it
  minimally and label it `adapted from <path:lines>` + `NEEDS COMPILE CHECK`. Never present non-compliant code as Good.
- Spock-first: tests are Spock 2.4 specs. A JUnit Good becomes an adapted Spock version of the same real test.
- U2a: every test name starts with "should": Spock `def "should <behaviour>"()`; (JUnit only in Bad examples or legacy notes).
- U2/K20/GT2: labelled blocks `given: "…"`, `when: "…"`, `then: "…"` (`expect:`/`where:` as appropriate).
- ST1: Java → `final var` / `final` on every local; Groovy → `def` for locals, explicit type only when it documents something.
- ST2: a call or signature that does not fit one line → one argument per line, indented once, closing paren on the last
  argument's line. (Line length: check AP's .editorconfig / IDE config on master; Checkstyle does not enforce it.)
- K-rules (K1 plain-line closure checks, K2b real argument values in verified interactions, K3–K5, K19 bound thrown, etc.).
- Playwright Goods obey EA–ED (role locators, web-first matchers, test.step per Given/When/Then, issue annotation).

BAD examples: keep the real code where possible; a Bad should show its own rule's violation clearly. If a real Bad also
breaks unrelated rules, keep it but add one line "also breaks: <ids>" so the reader is not misled.

Entry shape (same as v1):
### <ruleId> — <rule ≤15 words>
**Good** (real|adapted) ```lang … ``` `path:lines` — why
**Bad** (real|adapted|n/a) ```lang … ``` `path:lines` — why
Keep ≤15 lines per snippet. Finish with counts (real Goods that already complied / rewritten Goods). Report a 4-line summary.
