# 10. Plugins may ship small check scripts

Status: accepted (operator, 2026-11-11, #304)

Supersedes in part [ADR-0001](0001-one-plugin-one-folder-ships.md): its consequence that scripts never reach an
agent's plugin cache.

## Context

ADR-0001 keeps design work, scripts and tests out of what ships. Principle K7 says that where a check can run, the
plugin ships a script or lint, not a prose rule. Under ADR-0001 a skill could only describe a check in prose, so the
two disagree. K1 now says the plugins hold instructions, data and the small check scripts a skill tells the agent to
run, never engine code.

## Decision

A plugin may ship a small check script that one of its skills tells the agent to run. It sits in that skill's folder.

- It checks; it does not run the work. Engine code never ships: no runner, loop, dispatch or model call.
- The repo's own `scripts/`, `tests/` and design stay outside `plugins/`, as before.
- Only the plugin folders ship, as ADR-0001 and ADR-0009 decide.
- A script that turns a rule into a check says nothing new: the rule still has its ledger row and the operator's yes.

## Alternatives

- **Keep ADR-0001 as it is.** Rejected. Every check stays prose, and K7 cannot be met inside a plugin.
- **Ship scripts in a separate package.** Rejected. A project would install and pin two things for one skill, and the
  skill could not name a path that is sure to exist.

## Consequences

- A skill can say "run this script" and point to a file beside it.
- The first pull request that ships a script adds a test that runs it, and decides how the checks cover it:
  `check_provenance.py` reads only markdown today.
- ADR-0001 points here.
