# Project docs

What each file of a project's docs holds, and what it must not hold. Read it when you add, move or review a README,
an AGENTS.md, a CLAUDE.md, a glossary or a doc under `docs/`.

## Each file

| file | reader | holds | must not hold |
|---|---|---|---|
| `README.md` | people | what the project is, how to run it, how to test it, where to read next | rules for agents, history |
| `AGENTS.md` | coding agents | under 200 lines: one opening paragraph, then `## Check`, `## MUSTs`, `## Where things go` and `## Pointers` | a copy of a doc it can point at, history |
| `CLAUDE.md` | Claude Code | the one line `@AGENTS.md` | a second copy of the rules |
| `GLOSSARY.md` | everyone | terms only, one line each | how the code works, decisions |
| `docs/` | people and agents | docs split by mode, and a docs map | a doc that mixes two modes |

- Give `AGENTS.md` its four sections in that order. `## Check` holds the commands that prove a change. `## MUSTs`
  holds one rule in each list item, as "**Do X**, because Y". `## Where things go` says where new code and docs go.
  `## Pointers` names each doc an agent reads, and when. An agent reads every line on every run, so the file stays
  under 200 lines.
- Keep `CLAUDE.md` as the one line `@AGENTS.md`, because a second copy of the rules drifts from the first.
- Keep the glossary to terms, because a decision or an implementation note in it goes stale where no reader checks.
- Split `docs/` by the four modes in [modes.md](modes.md): tutorial, how-to, reference and explanation. A reader then
  finds a doc by what they want to do.

## The docs map

Keep one docs map in `docs/`. Give each doc or generated contract one row: the doc, its source of truth, the check
that catches drift, and where a new doc of that kind goes. A reader then knows which file to edit, and the writer
knows where to put a new doc.

## No history notes

Write what the code does and why, and leave out who decided it, when, and on which ticket. The git log, the pull
requests and the decision records keep that history. When a line is wrong, fix it or delete it, with no dated note
beside it, because a reader acts on the newest line and cannot tell which note is still true.

**Bad**
```markdown
The overdue job runs every hour. (Changed on 3 March after the review; it ran nightly before.)
```

**Good**
```markdown
The overdue job runs every hour.
```

## The Today marker

Write what the code does, and mark with **Today:** the design it does not meet yet. Without the marker, a reader takes
the design for the code, or the code for the design. Delete the marker in the change that closes the gap.

**Bad**
```markdown
The overdue job runs every hour.
```
The code still runs the job once a night. The doc states the design as fact, and a reader plans on the wrong time.

**Good**
```markdown
The overdue job runs once a night, at 02:00 (`schedule` in `config/jobs.yaml`).
**Today:** the decided design runs it every hour.
```

## Review

Walk each project doc that the change adds or edits. Each line is a blocker unless marked (warning).

- A README that holds rules for agents, or an AGENTS.md that holds what the README says.
- An AGENTS.md over 200 lines, without its four sections, or with a MUST that has no reason.
- A CLAUDE.md that holds more than `@AGENTS.md`.
- A glossary entry that holds a decision or an implementation note.
- A doc under `docs/` with no row in the docs map, or that mixes two modes.
- A who, when or ticket note, or a dated amendment, in a doc or a code comment.
- A design stated as what the code does, or a gap between code and design with no **Today:** marker.
- A **Today:** marker whose gap is closed.
