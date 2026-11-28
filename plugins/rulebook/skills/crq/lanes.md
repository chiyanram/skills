# Lanes

Which lane a change takes, by the kind of change, and what the one-way-door flag adds. Read it at intake, or when
the change turns out bigger or riskier than its lane.

## The lanes

| lane | grill | spec | design | red test | build | review lens | check rung | optional |
|---|---|---|---|---|---|---|---|---|
| feature | ✔ | ✔ | ✔ | – | ✔ | code + testing | full gate | break the design, deslop |
| bug | ✔ | – | – | ✔ | ✔ | code + testing | module | spec, design |
| tests only | short | – | – | – | ✔ | testing | changed tests | – |
| docs only | – | – | – | – | ✔ | writing | lint | – |
| config or command | short | – | – | – | ✔ | code | smoke | – |

A short grill asks only what blocks the build. The check rungs are the commands in `docs/agents/checks.md`.

## Picking the lane

- Take the kind from the ticket first, then check it against the diff. When they differ, such as a docs ticket that
  edits Java, move to the bigger lane and say so on the card, because a lane picked from the title under-reviews the
  change.
- When unsure between two lanes, take the bigger one, because a review too heavy costs time and a mistake in stored
  data cannot be undone.
- A patch-level dependency bump that changes no behaviour is config. A minor or major bump is a feature.
- A change to behaviour in a docs, tests or config ticket moves it to the bug or feature lane.
- In the bug lane, intake writes one criterion from the ticket: "<input> gives <expected>, today it gives <actual>".
  The person approves that line on the card, not a full spec. Write a spec when the bug changes what a spec promises.

## The one-way-door flag

Set the flag on any lane when the change touches stored data or a schema, a public API or event contract, or a
deploy, because a wrong step there cannot be undone. A migration that only adds a nullable column or a table nothing
reads yet does not set it; one that renames, retypes, drops or backfills does. The flag adds:

- each irreversible step listed for the person's yes;
- one more reviewer on the irreversible steps;
- the full gate as the check rung;
- a pre-mortem in the design (`planning`'s spec-review notes);
- the readiness items in the PR body ([pr-readiness.md](pr-readiness.md)).

## Optional stages

Skip an optional stage only on evidence, and write the skip on the card as `n/a: <why>`, because a skip is never a
pass. A feature spec, and any spec with the flag, ends with "How we will know it worked" (`planning`'s
acceptance-criteria notes).

## Review

Walk the ticket, the card, the PR and its diff. Each line is a finding.

- No lane on the card, or a lane lighter than what the diff touches.
- A docs, tests or config lane whose diff changes behaviour.
- A change to stored data, a schema, a public contract or a deploy with no flag.
- A flagged change with an irreversible step that has no yes, or no readiness items.
- A skipped stage with no `n/a: <why>` on the card.
