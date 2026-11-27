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
   3. Where do the glossary and the decision records live?
3. Run the tracker's read command on one real ticket. When it fails (not logged in, no CLI, no access), stop and
   give the cause, because every later stage reads the ticket.
4. Write the three files in the shapes below, show them, and commit only on the person's yes.

## Shapes

`docs/agents/issue-tracker.md`:

```markdown
# Issue tracker: GitHub
- Read a ticket: gh issue view <n> --comments
- Comment on a ticket: gh issue comment <n> --body "..."
- Create a ticket: gh issue create --title "..." --body "..."
- Link a PR to a ticket: "Closes #<n>" in the PR body
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
- Glossary: GLOSSARY.md at the root
- Decision records: docs/adr/
```

A rung the project does not have says `none`. The lane that needs it then runs the next rung up and says so on the
card.
