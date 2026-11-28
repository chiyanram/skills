# Maps

How you chart a goal that is too big for one ticket, while the way to it is not clear yet. A map plans: it builds
nothing.

## The map

The map is one ticket. Its body has five parts:

```markdown
## Destination
<one or two lines: the decision, spec or change this effort reaches>

## Decisions so far
- #<n> (<2 to 6 words>): <the gist of its answer>

## Not yet clear
<questions you cannot state sharply yet>

## Out of scope
<work ruled out of this effort, each with why>
```

- Write the destination first, because it sets what is in scope and what is not.
- Keep a decision only in its own ticket. The map gives one line per closed decision ticket, its gist and its link,
  because a second copy of a decision drifts from the first.
- Leave the open tickets off the map. Find them by query: the map's open children, because a list in the body goes
  stale as soon as a ticket closes.
- Move a question from **Not yet clear** into a ticket once you can state it sharply, even if you cannot answer it yet.

## Decision tickets

Each child of the map is a decision ticket: one question, sized to one session. It has one type:

- **research**: a fact to find, from docs or code.
- **prototype**: something rough for the person to react to.
- **grill**: a talk with the person, run with the `grilling` skill. The person gives each answer, never the agent.
- **task**: manual work that must happen before a decision can be made.

When a ticket is decided, post its answer as a comment and close the ticket. Then add its line to **Decisions so
far**.

## The tracker

- Set the blockers by `program-design.md`, its rule on `Blocked by:`.
- Give each `#N` 2 to 6 words of context in every text the person reads, because a bare number tells them nothing.
- Use the labels that `docs/agents/issue-tracker.md` names for maps, such as `map` and `decision`.
- Run the tracker commands from `docs/agents/issue-tracker.md`. When it has no line for a step, such as create a
  child ticket or link a blocker, name the missing line.

## The way out

When every question on the map is decided, cut the build into tickets by `program-design.md`. `crq` builds each one.

## Review

Walk the map and its decision tickets. Each line is a blocker unless marked (warning).

- A decision restated on the map beyond its one-line gist.
- A map that lists its open tickets.
- A grill ticket the agent answered itself.
- A `#N` with no context in text the person reads. (warning)
