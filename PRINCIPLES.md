# Principles

What this repo holds to, K1–K7. Each is guidance: a change that departs from one says which and why in its pull
request. `AGENTS.md` holds the hard rules; `CONTRIBUTING.md` holds the procedures.

- **K1** — What ships is knowledge only. The plugins hold instructions, data and the small check scripts a skill tells
  the agent to run, never engine code; the repo's own tests and design stay outside them. It works without the engine.
- **K2** — One rule, two readers. The writer follows a rule and the reviewer checks that same rule by its ID; no second
  copy for the reviewer.
- **K3** — A rule is short and says why. It enters only with its rulebook owner's yes; where it came from lives in the
  ledger, never in the rule.
- **K4** — A skill is a short entry that points to its references, and its description says when to use it.
- **K5** — Rules grow from our own failures: a lesson lands as a rule or a decided edge with its origin, and which rules
  runs actually read is measured.
- **K6** — Say only what the model wouldn't do anyway, and keep it short: prune and condense rules like code, and give
  the goal and the limits, not every step.
- **K7** — Where a check can run, ship a script or lint, not a prose rule.

## Formats and changes

- **This repo owns its formats:** the role cards, the lanes file and the findings it ships. Each format is versioned,
  and CI checks every file against it.
- **A change is measured:** a change to a card, rule or reference is kept only if it is no worse on what it must hold
  and better on what it aims at. Where no eval exists yet, its pull request says "untested by an eval".
