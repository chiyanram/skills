# Setup

The first `/crq` in a repo writes three short files under `docs/agents/`, so every later run knows the tracker, the
checks and the words of the domain. Read it when `docs/agents/checks.md` is missing.

## Steps

1. Look first: read `docs/agents/`, `AGENTS.md` or `CLAUDE.md`, the build file and the CI config, `GLOSSARY.md` and
   `docs/adr/`. When `issue-tracker.md` and `domain.md` already exist, as another setup writes them, reuse them and
   ask only for `checks.md`.
2. Ask one question at a time, each with the answer you found as the recommendation, because a person answers a
   guess they can correct faster than a blank:
   1. Where do tickets live: GitHub, GitLab, Jira or local Markdown files?
   2. Which commands run the unit tests, one module, the smoke test and the full gate?
   3. Where do the glossary, the decision records and the coding standards live?
3. Run the tracker's read command on one real ticket. When it fails (not logged in, no CLI, no access), stop and
   give the cause, because every later stage reads the ticket.
4. Write the three files in the shapes below, and one line, "Agent setup for this repo: `docs/agents/`.", in
   `AGENTS.md`. When only `CLAUDE.md` exists, move its rules into a new `AGENTS.md` with that line, and leave
   `@AGENTS.md` as the one line of `CLAUDE.md`, because a second copy of the rules drifts. When neither exists,
   create `AGENTS.md` with that line. Show them, and commit only on the person's yes.

## Shapes

`docs/agents/issue-tracker.md`:

```markdown
# Issue tracker: GitHub
- Read a ticket: gh issue view <n> --comments
- Who am I: gh api user -q .login
- Assign a ticket: gh issue edit <n> --add-assignee @me
- Comment on a ticket: gh issue comment <n> --body "..."
- List open tickets: gh issue list --state open --json number,title,labels,assignees,createdAt,blockedBy
- List open PRs with checks: gh pr list --state open --json number,title,headRefName,isDraft,reviewRequests,statusCheckRollup
- Search tickets and PRs: gh search issues "<words>" --repo <owner>/<repo> --state all; gh search prs "<words>" --repo <owner>/<repo> --state all
- Create a ticket: gh issue create --title "..." --body "..."
- Link a PR to a ticket: "Closes #<n>" in the PR body
- Priority labels: none (or: p1, p2, p3, highest first)
- Map labels: map, decision
```

`docs/agents/checks.md`:

```markdown
# Checks
| rung          | command                         |
|---------------|---------------------------------|
| lint          | make lint                       |
| changed tests | ./gradlew test --tests '<name>' |
| module        | ./gradlew :<module>:check       |
| smoke         | make smoke                      |
| full gate     | make verify                     |
```

`docs/agents/domain.md`:

```markdown
# Domain docs
- Glossary: GLOSSARY.md at the root (a GLOSSARY-MAP.md points at one per context)
- Decision records: docs/adr/
- Standards: CONTRIBUTING.md, docs/architecture/
- Review rubrics: none (or: spec → docs/agents/spec-checks.md, code → docs/agents/code-checks.md)

Before you explore, read the glossary and the decision records that touch the area. If a file here does not
exist, proceed silently; do not suggest creating it.
Use the glossary's words. Do not drift to a synonym the glossary avoids.
If your work contradicts a decision record, say so: "Contradicts ADR-0007 (event-sourced orders), but worth
reopening because …". Never override one silently.
A documented standard here wins over a rulebook rule that says otherwise.
```

A review rubric file is the project's own: a table of its sources of authority, highest first (for example its ADRs,
then `CONTRIBUTING.md`, then this rulebook), and the checks only this project needs. A
review walks its rulebook criteria first, then that file.

A rung the project does not have says `none`. The lane that needs it then runs the next rung up and says so on the
card.
