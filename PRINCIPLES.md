# Principles

Changed only by a pull request the operator merges.

What this repo holds to. Each principle is guidance: a change that departs from one says which and why in its pull
request. `AGENTS.md` holds the hard rules; `CONTRIBUTING.md` holds the procedures.

## Index

- [K1](#k1) — Knowledge only, and it works on its own.
- [K2](#k2) — One rule, two readers.
- [K3](#k3) — A rule is short, says why, and enters with its owner's yes.
- [K4](#k4) — A skill is a short procedure for one job.
- [K5](#k5) — Rules grow from our own failures.
- [K6](#k6) — Say only what the model wouldn't do, and keep it short.
- [K7](#k7) — A script or lint beats a prose rule.
- [K8](#k8) — A skill change ships with eval proof, sized by its tier.

## K1

What ships is knowledge only. The plugins hold instructions, data and the small check scripts a skill tells the agent
to run, never engine code; the repo's own tests and design stay outside them. It works without the engine.

**Why.** Plain files can be read by any agent, and `/crq` runs on a laptop with no engine installed. Small check
scripts may ship so that K7 can hold.

The `toolbox` plugin follows the same rule and adds two: every tool is typed-only (`disable-model-invocation: true`),
with no push or merge, because a person chooses when a tool runs; and it versions and releases on its own line, so a
tool change never bumps the rulebook.

**How it's checked.** `check_plugin.py` fails a plugin that is not in its own folder under `plugins/`, and only those
folders ship. That no engine code enters them is review only.

## K2

One rule, two readers. The writer follows a rule and the reviewer checks that same text; there is no second
copy for the reviewer. A finding cites the skill and its section, or the rule's ID where the rule still has one.

**Why.** When the writer and the reviewer read different text, the review blocks on rules the writer was never shown.

**How it's checked.** Review only.

## K3

A rule is short and says why: the instruction, then the failure it prevents. It enters only with its rulebook
owner's yes; where it came from lives in the pull request that added it, never in the rule.

**Why.** The reason lets the model apply a rule to cases it does not name; a bare rule is followed to the letter or
not at all. The agent needs the rule and its reason, not its history. "Owner" rather than one named person, so a
team's own rulebook works the same way.

**How it's checked.** `check_provenance.py` fails a source in a shipped file. The reason and the owner's yes are review
only: the owner's yes is the merge.

## K4

A skill is a short procedure for one job, and its description says when to use it. `SKILL.md` holds the steps
and the rules, and is read whole. A file beside it holds what only some runs need, such as one stack's traps. A skill
that does two jobs becomes two skills.

**Why.** A short skill can be read, audited and edited whole. A library of references collects sediment that nobody
dares to delete, and an agent picks a skill by its description.

**How it's checked.** `check_skills.py` fails a skill with no description or one over 1024 characters, and
`check_routing.py` fails a skill that does not win its own requests.

## K5

Rules grow from our own failures: a lesson lands as a rule in the skill, with its reason, and its origin goes in
the pull request that adds it.

**Why.** Our own failures show where a rule is missing; a rule the model already follows is waste (K6).

**How it's checked.** Review only.

## K6

Say only what the model wouldn't do anyway, and keep it short: prune and condense rules like code, and give the goal
and the limits, not every step. Give a Good / Bad pair only where the model's default is wrong, such as a framework
trap; elsewhere the rule and its reason are enough.

**Why.** Every line costs context on every run, so text the model would follow anyway is waste. A run given the goal
and the limits is not railroaded. An example teaches best where the model would otherwise write the trap.

**How it's checked.** `check_sizes.py` fails a rule in a reference over 35 words and an instruction chain over its
budget. Pruning is review only.

## K7

Where a check can run, ship a script or lint, not a prose rule.

**Why.** A script beats prose: a check that runs fails every time, and a prose rule can be missed.

**How it's checked.** Review only.

## K8

A skill change ships with eval proof that it is no worse, sized by the skill's tier. The steps and the rules for a
run you can trust are in [CONTRIBUTING.md, Prove a skill change](CONTRIBUTING.md#prove-a-skill-change).

**Why.** A verdict from a run that did not load the skill, that errored, or that a changed grader scored, proves
nothing. Committed proof lets anyone check the claim on any machine.

**How it's checked.** `check_eval_proof.py` checks the committed cases, summaries and baseline against each skill's
tier, with no model call. The operator approves each case, grader and baseline.
