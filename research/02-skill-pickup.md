# R2 · Skill pickup — which skills fire, which never

Ticket: `../issues/02-research-skill-pickup.md` · Script: scratchpad `skill_pickup.py` + `context.py` (not committed).

**Evidence:** 483 transcript files (main + `subagents/`) across 14 `~/.claude/projects/*agent-platform*` dirs,
**2026-08-31 → 2026-10-01**. Records deduped by `uuid`, tool calls by `id`.

| count | meaning |
|---|---|
| slash | human typed `/x` (non-sidechain `<command-name>/x`) |
| model | assistant `Skill` tool_use with `input.skill = x` |
| preload | subagent `skills:` frontmatter injection (`<command-name>x`, no slash, sidechain) |

## Per skill

`DMI` = `disable-model-invocation: true` (description not even in context). `CMD` = named in a
`.claude/commands/*.md`; `CL` = in CLAUDE.md's skills row.

| skill | slash | model | preload | desc words | shape notes |
|---|---:|---:|---:|---:|---|
| crq *(cmd)* | 172 | 3 | – | – | no frontmatter; human-driven |
| show-me | 149 | 2 | – | 47 | "Applies wherever you report"; model calls only when user named it |
| resolving-merge-conflicts | 55 | 8 | – | 11 | "Use when…" first; concrete situation; 7/8 model calls user-named it |
| wayfinder | 24 | 0 | – | 41 | DMI |
| grill-with-docs | 20 | 0 | – | 19 | DMI |
| refine *(cmd)* | 18 | 1 | – | – | |
| grill-me | 17 | 0 | – | 9 | DMI; body says "Run a `/grilling` session" |
| teach | 13 | 0 | – | 11 | DMI |
| spec-review | 10 | 0 | 23 | 49 | "The rubric for…"; CL, CMD; fires by agent preload |
| triage | 9 | 0 | – | 22 | DMI |
| aruvii-cleanup | 8 | 2 | – | 57 | CL, CMD |
| code-review | 7 | 15 | – | 107 | CMD ("Run…"); 11/15 model calls inside `/crq` |
| research | 7 | 1 (sub) | – | 39 | `hasUse`; 0 model in main sessions |
| aruvii-git | 6 | 13 | – | 85 | "Use when…" first; CL, CMD; most model-initiated of any repo skill |
| i-have-adhd (repo) | 6 | 1 | – | 103 | "Invoke it yourself, unprompted…" — 1 call in 31 days |
| aruvii-standards | 1 | 3 | – | 82 | CL, CMD; 3/3 inside `/crq` |
| v1-status *(cmd)* | 2 | 0 | – | – | |
| issue *(cmd)* | 2 | 1 | – | – | |
| improve-codebase-architecture | 1 | 1 | – | 20 | DMI (1 model call came from inside `/teach`) |
| wait-what | 1 | 0 | – | 10 | DMI |
| architecture-review | 0 | 0 | 22 | 86 | rubric; preload only |
| grilling | 0 | 9 | – | 25 | 9/9 inside `/grill-me`/`/grill-with-docs` — delegated, not matched |
| flyway-migration | 0 | 8 | – | 26 | CL, CMD; concrete artefact; 1 call outside `/crq` without user naming it |
| dod *(cmd)* | 0 | 7 | – | – | CMD ("Run `/dod`") |
| standards-review | 0 | 0 | 6 | 58 | preload only |
| deslop | 0 | 5 | – | 50 | "Invoked at /crq stage 6a"; 5/5 inside `/crq` |
| smoke-spec | 0 | 4 | 2 | 50 | "Use when…" first; CL, CMD |
| it-testing | 0 | 1 | – | 36 | "Use when…" first; CL, CMD; 530 prompts mention IT/integration test |

## Never fired (0 slash · 0 model · 0 preload, 31 days)

| skill | desc words | DMI | named where | prompts that hit its trigger words |
|---|---:|---|---|---:|
| tdd | 20 | – | crq.md:260, descriptively ("carries…") | 15 msgs / 14 sessions |
| diagnosing-bugs | 19 | – | nowhere | 30 / 24 |
| codebase-design | 40 | – | nowhere | 42 / 24 ("seam", "deep module") |
| domain-modeling | 35 | – | crq.md:79, refine.md | 10 / 10 |
| prototype | 32 | – | refine.md, issue.md | 13 / 11 |
| hook-from-rule | 32 | – | CL | 4 / 4 |
| acceptance-criteria-writing | 69 | – | "Used from to-spec" | 7 / 4 |
| gherkin-to-test | 69 | – | nowhere | 0 |
| to-spec · to-tickets · to-questionnaire | 25 · 42 · 16 | DMI | — | n/a (slash only) |

Trigger-word counts are a regex heuristic (scratchpad `context.py`), not proof of relevance.

## What predicts pickup

1. **A human typing `/x` is most of it.** Slash ≈ 630 invocations vs model ≈ 100 (all skills incl. plugins, built-ins like `/exit` excluded). The top five skills by
   use (`crq`, `show-me`, `resolving-merge-conflicts`, `wayfinder`, `grill-with-docs`) are all slash-driven.
2. **Model calls are almost all *directed*, not *discovered*.** Of ~100 model `Skill` calls, the large
   majority sit inside a running `/crq`, `/grill-me` etc. whose body names the skill, or follow a user
   prompt naming it. Spontaneous description-matched calls: a handful — `flyway-migration`, `aruvii-git`,
   `untouched-and-risk`, `redis-*`, `artifact-design`.
3. **Imperative wording in the caller fires; descriptive mention does not.** `crq.md` "Run the
   **`deslop`** skill" → 5/5; "Run `/dod`" → 7. `crq.md:260` "The `tdd` skill carries what a good
   test is" → 0. "`it-testing` skill carries the pattern" → 1 in 530 IT-mentioning prompts.
4. **Rubric skills only ever run as subagent preload.** `spec-review`, `architecture-review`,
   `standards-review` (descriptions open "The rubric for…") — 51 preloads, 0 model calls (plus 2 `smoke-spec` preloads). Fine: that is
   their job; their descriptions cost listing budget for nothing.
5. **Description *shape* alone does not predict it.** "Use when…"-first skills split: `aruvii-git` 13,
   `resolving-merge-conflicts` 8 vs `it-testing` 1, `gherkin-to-test` 0, `acceptance-criteria-writing` 0.
   Generic-process skills (`tdd`, `diagnosing-bugs`, `codebase-design`, `prototype`) never fire even with
   quoted trigger phrases — Claude does those tasks natively and does not reach for a skill.
6. **"Invoke it yourself, unprompted" does not work.** `i-have-adhd` (repo, 103 words, the longest
   imperative) → 1 model call; `show-me` → 2, both user-named. Style is applied from CLAUDE.md
   instead; the skill call never happens.
7. **Concrete, repo-specific artefact + "whenever" verb = best spontaneous pickup.** `flyway-migration`
   ("Use whenever a change needs a schema migration") and `aruvii-git` (commit/MR message) are the two
   that fire without being told.
8. **Listing crowding is real here.** This session's skill listing carries ~200 entries; dozens of plugin
   skills appear with *no description at all* (budget overflow), and repo skills are duplicated by
   `mattpocock-skills:*` copies with identical text (`research`, `tdd`, `grilling`, `prototype`…) — see #587.
   DMI skills (11 of 34) at least cost nothing.

## Anthropic guidance

| claim | source |
|---|---|
| "The description is critical for skill selection" | [Best practices][bp] |
| Should include "both what the Skill does and when to use it" | [Best practices][bp] |
| "Always write in third person" — inconsistent POV "can cause discovery problems" | [Best practices][bp] |
| Description max 1,024 chars; SKILL.md body under 500 lines | [Best practices][bp] |
| Pick from "potentially 100+ available Skills" | [Best practices][bp] |
| Agent "pre-loads the `name` and `description` of every installed skill" | [Engineering blog][eng] |
| Loads full SKILL.md "If Claude thinks the skill is relevant" | [Engineering blog][eng] |
| Listing budget "scales at 1% of the model's context window" | [Claude Code skills][cc] |
| Overflow "drops descriptions starting with the skills you invoke least" | [Claude Code skills][cc] |
| Entry capped at 1,536 chars; "put the key use case first" | [Claude Code skills][cc] |
| Not triggering: include "keywords users would naturally say" | [Claude Code skills][cc] |
| DMI: "Description not in context" | [Claude Code skills][cc] |
| `paths:` glob — loads skill "only when working with files matching" | [Claude Code skills][cc] |
| Commands "have been merged into skills" | [Claude Code skills][cc] |

Implications for G1: the docs make the description the *only* discovery signal and warn it can be
dropped under budget pressure (least-used first — which is exactly our never-fired set). Two levers
the repo does not use: **`paths:` on skill frontmatter** (`it-testing` → `**/integrationTest/**`,
`flyway-migration` → `**/db/migration/**`, `smoke-spec` → `**/smoke-*.spec.ts`) and **`user-invocable: false`
/ moving rubrics out of the listing** (rubrics are preload-only). Evidence here says the reliable trigger
is an imperative "Run the X skill" at the right `/crq` stage — not description tuning.

[bp]: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
[eng]: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
[cc]: https://code.claude.com/docs/en/skills

## Caveats

- One user, 31 days; counts are not normalised for how often each skill *was* relevant.
- `active` command context = most recent slash in that session; long sessions may misattribute.
- `paths:` behaviour on skills is documented but not tested here.
