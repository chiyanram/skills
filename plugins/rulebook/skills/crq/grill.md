# Grill

**You own the questions the ticket leaves open, and the record of every answer.** The `grilling` skill runs the
rounds; this file adds what crq needs around them. Read it when the grill stage starts or a new session finds a
grill record.

## Rules

- **Facts.** Follow `grilling`'s rule on facts. Put each fact a command settled in the record, with the command and
  its result, because the next session must not run it again.
- **Domain challenge.** In each round, check the ticket's words against the project glossary that
  `docs/agents/domain.md` names: name a term used in another sense ("the glossary says a loan ends at return; here it
  ends at renewal: which?") and propose one word for a fuzzy one, because a wrong word settled here reaches every
  criterion. Check each stated behaviour against the code, and name where it disagrees. For each link between two
  domain terms the ticket names (a loan and its reservation), ask one question about a case the ticket does not
  cover, because an unasked case becomes a missing AC. Break scenarios stay in the spec stage (`planning`).
- **Grill record.** After the person answers a round, post one comment on the ticket with the "Comment on a ticket"
  command in `docs/agents/issue-tracker.md`, because answers given in a chat are lost to the next session. When that
  file names no such command, write the record to `docs/agents/grill/<ticket>.md`. Its shape:

  ```markdown
  **Grill record, round 2**
  Settled:
  - Q: may a reserved loan be renewed? A: "No, never." (the person, quoted)
  - Fact: a renewal keeps the fine; `./gradlew test --tests FineSpec` passed at 4f2c9e1
  Still open:
  - Q: does a renewal reset the due date? Decider: the product owner
  Glossary and ADR gaps:
  - "renewal" is not in the glossary
  ```

- **No re-asking.** Before a round, read every grill record on the ticket, and ask nothing it settled.
- **Gaps go to the spec.** List each missing term and each decision with no ADR. The spec defines each new noun by
  `planning`'s acceptance-criteria notes, and records an ADR by its spec-review notes' ADR rule.

Done when the latest record's Still open list is empty, or each item on it names a decider outside this session, and
the person has confirmed a shared understanding (`grilling`).

## Review

Walk the ticket's grill records. Each line is a finding.

- A round with no record, or a record with no Settled and Still open lists.
- An answer in a record that is not the person's words, quoted.
- A question a record had settled, asked again.
- A question a command could answer, put to the person.
- A ticket term that differs from the glossary with no challenge in the record.
