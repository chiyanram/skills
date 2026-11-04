# Writing references

Which rules a reference in this rulebook may hold, and where its examples come from. Read it when you write or review
a rule, a sources paragraph or a Good / Bad pair in any reference.

## Rules

- **SRC2** — Admit a rule only on two independent sources, each read at path:line or URL section, or on a stated
  operator preference, because one project's code teaches its own habits as industry practice.

## When X, use Y

| the rule has | use | why |
|---|---|---|
| two sources from different companies or projects, each read at `path:line` or URL §section | admit it; name both sources in the sources paragraph or the why cell (SRC2) | two independent sources show the practice is not one team's habit |
| two pages from one company or project | count them as one source; find a second source, or ask the operator (SRC2) | pages from one company or project count as one source |
| one source or none, and the operator states it as a preference | admit it; list its id on the Operator preference line under this table (SRC2) | the label tells a reader the rule is a choice, not industry practice |
| only part of it from two sources, and the rest from the operator | admit it; list its id on the same line, which says "in whole or in part" (SRC2) | one line covers a whole or a half preference |
| a mistake in the project's own code that shows the rule is needed | keep the project path in the project's own approval record as evidence, never in the reference (SRC2) | the project's code is evidence that a rule is needed, never the rule itself |
| a Good / Bad pair to write | adapt the pair from the rule's source into one neutral domain; with no source pair, write fresh neutral code (SRC2) | a pair that re-skins project code teaches that project's names and habits |

The format of a reference (its five sections, the rule line, the Operator preference line) is the rulebook's reference
format document. A source is a file read at `path:line`, or a web page read at its URL and section.

## Good / Bad

### SRC2 — A rule needs two independent sources or the operator preference line

**Bad**
```markdown
## Rules

- **RT1** — Add random jitter to every retry delay, because clients that retry
  in step overload a recovering server (source: `ops-blog`, one vendor blog post).

## When X, use Y
…
`ops-blog` is one post on a vendor's engineering blog.
```
One source admits the rule, and nothing marks it as a preference. The rule line also carries its source.

**Good**
```markdown
## Rules

- **RT1** — Add random jitter to every retry delay, because clients that retry
  in step overload a recovering server.

## When X, use Y
…
`client-guide` is library A's documentation, §Retries. `sre-notes` is
organisation B's operations handbook, §Overload.
```
Two independent sources state the rule, and the rule line holds the rule only. With one source, the reference instead
lists RT1 on the Operator preference line.

## Decided edges

- **Skip when** the two sources come from different companies or projects: they count as two. — **Do not skip when**
  the two pages come from one company or project: they count as one source (SRC2). — **Confidence** high
- **Skip when** the rule id is on the Operator preference line: one source or none is enough. — **Do not skip when**
  the operator stated only a different rule, or the line is missing: the rule needs two sources (SRC2). —
  **Confidence** high
- **Skip when** the project's code appears in its own approval record as evidence that a rule is needed. — **Do not
  skip when** a project name, path or business term appears in a rule, a sources paragraph or a Good / Bad pair
  (SRC2). — **Confidence** high
- **Skip when** no source has a pair: fresh neutral code is allowed. — **Do not skip when** the pair renames project
  code into a neutral domain: that re-skins it (SRC2). — **Confidence** high

## Review checks

Walk every rule line, sources paragraph, Operator preference line and Good / Bad pair that the change adds or edits.

- [ ] SRC2 — For each rule id, find two sources from different companies or projects, each named at `path:line` or
  URL §section in the sources paragraph or a why cell. A rule with fewer, and not on the Operator preference line,
  is a finding.
- [ ] SRC2 — A rule line that carries a source or a preference label is a finding.
- [ ] SRC2 — A project name, path or business term in a rule, a sources paragraph or a Good / Bad pair is a finding
  (`rg -n -i '<project names>'` over the changed references).
- [ ] SRC2 — Each Good / Bad pair is labelled with its source or `(neutral)`. A pair that renames project code is a
  finding.
