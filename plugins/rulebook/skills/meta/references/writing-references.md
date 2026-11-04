# Writing references

Which rules a reference in this rulebook may hold, where its examples come from, and where a rule's provenance is kept.
Read it when you write or review a rule, a When X, use Y row or a Good / Bad pair in any reference.

## Rules

- **SRC2** — Admit a rule only with two independent sources or the operator's stated preference, recorded in its
  ledger row, never in the reference, because the reference is for the agent and provenance belongs in the ledger.

## When X, use Y

| the rule has | use | why |
|---|---|---|
| two sources from different companies or projects, each read at `path:line` or a URL and its section | admit it; name both sources in the rule's ledger row (SRC2) | two independent sources show the practice is not one team's habit |
| two pages from one company or project | count them as one source; find a second source, or ask the operator (SRC2) | pages from one company or project count as one source |
| one source or none, and the operator states it as a preference | admit it; the ledger row's status records the preference (SRC2) | a reader of the ledger can tell a choice from industry practice |
| only part of it from two sources, and the rest from the operator | admit it; the ledger row's status says the preference covers part of the rule (SRC2) | one status covers a whole or a partial preference |
| a mistake in the project's own code that shows the rule is needed | keep the project path in the ledger row as evidence, never in the reference (SRC2) | the project's code is evidence that a rule is needed, never the rule itself |
| a Good / Bad pair to write | adapt the pair from the rule's source into one neutral domain, with no label or credit; with no source pair, write fresh neutral code (SRC2) | a pair that re-skins project code teaches that project's names and habits |
| a why cell to write | the plain reason the choice is right, never a source name or line (SRC2) | an agent acts on the reason; the ledger keeps the source |

The format of a reference (its five sections and the rule line) is the rulebook's reference format document, and
`make lint` fails a reference that carries a source citation, a credit, a preference mark, an evidence note or a date.

## Good / Bad

### SRC2 — The reference holds the rule; the ledger holds where it came from

**Bad**
```markdown
## Rules

- **RT1** — Add random jitter to every retry delay, because clients that retry
  in step overload a recovering server (source: `ops-blog`, one vendor blog post).

## When X, use Y
…
`ops-blog` is one post on a vendor's engineering blog.
```
One source admits the rule, and the reference carries its source twice: on the rule line and in a legend.

**Good**
```markdown
## Rules

- **RT1** — Add random jitter to every retry delay, because clients that retry
  in step overload a recovering server.

## When X, use Y

| the call | use | why |
|---|---|---|
| a client retries a failed call | a delay with random jitter (RT1) | retries in step overload a recovering server |
```
The reference holds the rule and its reason only. The ledger row for RT1 names library A's documentation (its Retries section)
and organisation B's operations handbook (its Overload section).

## Decided edges

- **Skip when** the two sources come from different companies or projects: they count as two. — **Do not skip when**
  the two pages come from one company or project: they count as one source (SRC2). — **Confidence** high
- **Skip when** the rule's ledger row records the operator's preference: one source or none is enough. — **Do not
  skip when** the operator stated only a different rule, or the row records none: the rule needs two sources (SRC2).
  — **Confidence** high
- **Skip when** a tool's name is the action itself, such as a Checkstyle check to turn on: it stays in the
  reference. — **Do not skip when** a name only credits where the rule came from: it moves to the ledger (SRC2). —
  **Confidence** high
- **Skip when** no source has a pair: fresh neutral code is allowed. — **Do not skip when** the pair renames project
  code into a neutral domain: that re-skins it (SRC2). — **Confidence** high

## Review checks

Walk every rule line, When X, use Y row, Good / Bad pair and ledger row that the change adds or edits.

- [ ] SRC2 — For each rule id, open its ledger row and find two sources from different companies or projects, each at
  `path:line` or a URL and its section, or a status recording the operator's preference. A row with neither is a finding.
- [ ] SRC2 — Any source citation, credit, label, preference mark, evidence note or date in a reference, or a name
  that only credits a source, is a finding (`make lint` runs `check_provenance.py`).
- [ ] SRC2 — A project name, path or business term in a rule, a why cell or a Good / Bad pair is a finding
  (`rg -n -i '<project names>'` over the changed references).
- [ ] SRC2 — A Good / Bad pair that renames project code is a finding.
