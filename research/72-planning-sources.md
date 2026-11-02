# 72 — Sources for the planning and meta rules (T3, agent-factory#33)

Step 1 of T3 under SRC2 (`00-reference-format.md` §"Good / Bad rules" item 4): each of the 36 ledger rows that T3 writes, read against
reference projects and primary docs at `path:line@sha`, with a verdict (TWO / ONE / NONE), a wording that matches what the sources
say, and what stays operator preference. Our own projects are evidence only, never a source. Read 2026-11-02; sites this session
could not open are marked NOT OPENED, and nothing is cited from them. The operator decides on agent-factory#33.

- Part A: `planning/references/acceptance-criteria.md` and `spec-review.md` (17 rows)
- Part B: `planning/references/program-design.md`, `diagrams.md`, `writing-docs.md` and `meta/references/writing-references.md` (19 rows)

---

## Part A: acceptance-criteria.md and spec-review.md (SRC2 audit)

Read 2026-11-02. Clones under `scratchpad/t3/refs/`, shallow, HEAD at:

| tag | repo · file | commit |
|---|---|---|
| `pl058` | jabrena/plinth `skills/058-design-bdd/references/058-design-bdd.md` | e0b6fb1d96232b58a700e0f8b639a33920daba89 |
| `plBA` | jabrena/plinth `.cursor/agents/plinth-business-analyst.md` | same |
| `pl014` | jabrena/plinth `skills/014-agile-user-story/references/014-agile-user-story.md` | same |
| `cuke` | cucumber/docs `content/docs/gherkin/reference.md` (source of cucumber.io/docs/gherkin/reference) | 3c93e6cee4c6164f40ed69dfe84ac440c2983120 |
| `cuke-api` | cucumber/docs `content/docs/cucumber/api.md` (#tags) | same |
| `cuke-bg` | cucumber/docs `content/docs/bdd/better-gherkin.md` | same |
| `mp-spec` / `mp-tix` / `mp-grill` / `mp-cr` | mattpocock/skills `skills/engineering/to-spec/SKILL.md`, `to-tickets/SKILL.md`, `skills/productivity/grilling/SKILL.md`, `engineering/code-review/SKILL.md` | 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d |
| `ps-why` / `ps-plan` / `ps-babysit` / `ps-lesson` | cursor/plugins `pstack/skills/why/references/synthesizer-prompt.md`, `poteto-mode/playbooks/multi-phase-plan.md`, `poteto-mode/playbooks/babysit.md`, `principle-encode-lessons-in-structure/SKILL.md` | ae5650febf4320793844c12c4adaa937f417f8da |
| `ao-sdd` / `ao-plan` / `ao-doubt` / `ao-ci` | addyosmani/agent-skills `skills/spec-driven-development/SKILL.md`, `planning-and-task-breakdown/SKILL.md`, `doubt-driven-development/SKILL.md`, `ci-cd-and-automation/SKILL.md` | 301b02b12bff98e4688e6984af6556802322bbde |
| `hl-plan` / `hl-dd` | humanlayer/humanlayer `apps/riptide-rpi-claude-plugin/skills/create-plan/references/plan_template.md`, `create-design-discussion/SKILL.md` | 316e74ef9af0b7b3d64ac45b5eb93415b3ed2204 |
| `jf-ac` / `jf-tpl` / `jf-miner` / `jf-scr` | Jeffallan/claude-skills `skills/feature-forge/references/acceptance-criteria.md`, `feature-forge/references/specification-template.md`, `spec-miner/SKILL.md`, `code-reviewer/references/spec-compliance-review.md` | 078a25cc5bfd8011459be7b91d004e900c1d02d3 |
| `goog` | google/eng-practices `review/reviewer/looking-for.md`, `navigate.md` | 3bb3ec25b3b0199f4940b1aa75f0ac5c5753301c |

**NOT OPENED:** cucumber.io, martinfowler.com (session DNS blocks both; cucumber.io text read from its repo `cucumber/docs` instead, which is the same source). Dan North, Atlassian, Scrum guide not opened (web blocked).
**Not at HEAD:** humanlayer `.claude/commands/create_plan.md` / `validate_plan.md` no longer exist; the current equivalent is the riptide plugin `create-plan` skill (used above). The classic "no open questions in final plan" text is gone.
**Ledger drift:** GA3's ledger cite `plinth 058:256-266` no longer matches; plinth 058 now says the tier tag needs a "trusted project convention" (:251), and :36 forbids inferring it.

Independence: plinth (all pages) = 1 source; cucumber docs = 1; mattpocock = 1; cursor/pstack = 1; addyosmani = 1; humanlayer = 1; Jeffallan = 1; Google = 1.

---

## acceptance-criteria.md

### GA1: scenarios as one fenced gherkin block in the spec; no .feature files, no runtime
- **Verdict: TWO** (for the core; "fenced block" is house format)
- A `plBA :41-42`: "Assemble one self-contained Gherkin Feature under a `# Acceptance Criteria` heading … Post … on the source issue (not a repository file)".
- B `jf-tpl :36-41` (AC-001 Given/When/Then inside the spec template's `## Acceptance Criteria`). Runtime-free: `pl058 :38` "Do not claim … every example requires Cucumber automation".
- Independent: plinth vs Jeffallan, different authors. Counter: `cuke :96` assumes `.feature` files. Say so in Decided edges.
- **Wording:** reword (drop "REQ", "analyst"): "Write a work item's scenarios as one Gherkin block under the spec's Acceptance criteria heading, not in a .feature file, because two copies of the criteria drift apart."
- **Project-specific:** "REQ", "analyst" (plan note says "discovery"). Use "spec" in the rulebook.

### GA2: stable scenario ids (AC-1…), unchanged once approved
- **Verdict: ONE**
- A `jf-ac :6`, `jf-tpl :38`: "### AC-001: [Scenario Name]". Weak support from addyosmani: `ao-sdd :223` "Link back to the spec section that each PR implements" is traceability, not ids.
- No source says ids are frozen, or that renumbering counts as a spec change.
- **Recommend PREFERENCE.** Ledger evidence REQ-500:303-307 shows a title-only scenario reference that broke. It is cheap, and GT4/CV2 depend on it.

### GA3: tags name domain/concern, never the tier
- **Verdict: TWO for "tags name domain/concern"; NONE for "never tier"** (sources disagree)
- A `cuke-api #tags :785-788`: `@billing Feature` and `@important Scenario`, both domain or concern tags.
- B `pl058 :251`: "behavioral tags such as `@happy-path`, `@business-rule`, `@idempotency`, `@authorization`, or `@error`".
- Against the ban: `pl058 :251` allows `@integration-test` under a "trusted project convention", and `pl133 :53` selects scenarios by `@acceptance`. Only `pl058 :36` ("do not infer `@integration-test` from alternative or error behavior") leans our way.
- **Wording:** "Tag scenarios by domain or concern (@billing, @authorization)". The "never a tier tag" clause is **PREFERENCE**: evidence REQ-500:352-357, and a tier tag makes the test-tier decision before the developer can (S1).
- **Project-specific:** "developer's call (S1)" cross-ref is fine; no Aruvii term.

### GA4: Examples header = exactly the placeholders; shared preconditions in Background
- **Verdict: TWO**
- A `pl058 :149`: "`Examples` tables provide a header matching those placeholders"; Bad example at :169-177. `pl058 :113-114` covers Background.
- B `cuke :426`: "`<>` delimited *parameters* that reference headers in the examples table". `cuke :302-306` says Given steps repeated in every scenario "are not *essential* … move such `Given` steps to the background".
- **Wording:** KEEP. Optional: add cuke's "keep Background short" (`cuke :373-374`, ≤4 lines) as a Decided edge.

### GA5: one checkable Then; every AC has a failure/refusal scenario
- **Verdict: TWO** (both halves)
- Then part, A `cuke :235`: "An outcome *should* be on an **observable** output … not a behaviour deeply buried inside the system". B `pl058 :32`: "`Then` for an observable outcome".
- Failure part, A `plBA :39`: "develop supported main, alternative, boundary, and error examples". B `jf-ac :32-45, :101` (Error Cases, "Error | Invalid state/input | Action | Error message").
- Neither says "one Then" or "every AC". `pl058 :88` names "one event", not one Then.
- **Wording:** reword: "Every scenario's Then states an outcome observable from outside the system, and each criterion has at least one error or refusal scenario, because an unobservable Then proves nothing." Keep "one Then" only as preference if wanted.

### GA6: scenario titles start "should …"
- **Verdict: ONE** (for "title states behaviour"); **NONE** for "should"
- `pl058 :93` "Scenario: Declined payment leaves the order unpaid" is a behaviour sentence. `cuke-bg :10` "scenarios should describe the intended behaviour … not the implementation" is about content, not titles. Also `jf-ac :17` uses noun titles ("Successful Login"), which is counter-evidence.
- **Recommend PREFERENCE.** Per the plan note, reword to "title = plain behaviour sentence" (U2a drop). The rule exists so that GT1 (title = test name) holds; evidence REQ-500:454-455.

### CV1: AC id as "# AC-n" comment above Scenario:
- **Verdict: NONE**
- `cuke :11` only allows `#` comments at line start; it does not prescribe ids. `jf-ac :6` puts the id in the title, which contradicts CV1.
- **Recommend PREFERENCE.** It follows from GA2+GA3+GT1 (house choices). Consider folding it into GA2's Good example rather than a standalone rule.

### AC7: changed stored data/default → a Given with pre-change state
- **Verdict: NONE** (as an acceptance rule)
- Nearest: `ao-doubt :22` flags "data migration" as high blast radius. `addyosmani deprecation-and-migration/SKILL.md :184` says to "Backfill … existing rows". Both cover migration practice; neither is a scenario rule.
- **Recommend PREFERENCE.** It is strong evidence (!230 QA F2): a scenario on new rows only tests the default.

### AC8: constant Examples column → Background/Given
- **Verdict: ONE (derived)**
- `cuke :302-306`: repeated context is "incidental details" → Background. No source addresses a constant Examples column.
- **Recommend PREFERENCE**, or **merge into GA4** as a Decided edge ("a column equal on every row is shared context"). The ledger itself records no real Bad (scan found none). Low value as a standalone rule.

### AC9: glossary/sibling terms; new noun declared before use
- **Verdict: TWO** (for "use glossary terms"); ONE for "declare a new noun first"
- A `mp-spec :13`: "Use the project's domain glossary vocabulary throughout the spec". `mp-tix :21` says the same, from the same source.
- B `cuke :519-521`: "the same language your users and domain experts use when they talk about the domain".
- Declare-first: `plBA :39` "confirm actors, outcomes, business rules, terminology … already supported by it … without inventing behavior" (plinth only).
- **Wording:** "Write scenarios in the glossary's terms; a term not in the glossary is defined in the spec before a scenario uses it, because the title becomes the test name." Declare-first clause = preference (or count plBA as its single source).
- **Project-specific:** "sibling REQs". Use "related specs".

### AC10: editing AC text after /approved is a spec change → fresh /approved
- **Verdict: TWO** (for the generic core)
- A `plBA :41-42`: "require explicit, unambiguous user confirmation before posting … never edit … a prior acceptance-criteria comment".
- B `ao-sdd :174`: "Planning starts only after the human approves the spec". `ao-sdd :220`: "Update when decisions change … update the spec first, then implement".
- **Wording:** "A change to an approved criterion's text is a new revision of the spec and needs a new approval, because an approval covers only the text it saw."
- **Project-specific:** `/approved`, "MR". Move the mechanics (MR note + `/approved` command) to agent-platform docs.

## spec-review.md

### SR1: report every finding in one round; a finding first raised in round N+1 on unchanged text is a miss
- **Verdict: TWO** (for "cover the whole artifact and report every finding"); NONE for the "reviewer miss" classification
- A `mp-cr :66`: "Report … every place the diff violates a documented standard". `mp-grill :8`: "Ask the whole frontier in one round".
- B `goog looking-for.md :155`: "look at *every* line of code that you have been assigned to review".
- Edge: `goog navigate.md :50-52` says to send major design comments "immediately, even if you don't have time to review the rest". That is a Decided edge: an early stop on a design flaw is allowed.
- **Wording:** "Review the whole spec and report every finding in one round, because findings raised one per round stretch a review to several rounds." The "N+1 = miss" metric is preference (evidence #576).

### SR2: present-tense claims about the system cite file:line; reviewer opens each
- **Verdict: TWO** (three sources)
- A `ps-why :32`: "Every Direct/Supported claim must have a citation (… file:line)".
- B `hl-plan :16-20`: "Current State Analysis … Important finding with file:line reference".
- C `jf-miner :86,:90`: "Ground all observations in actual code evidence … Include code locations". `jf-scr :53`: "Verify claims independently".
- Counter: `mp-tix :105` says not to put file paths in tickets ("they go stale fast"). That is a ticket rule, not a spec rule; note it as a Decided edge.
- **Wording:** KEEP, but replace "REQ" and "origin/master" with "spec" and "the default branch".

### SR3: a drifted file:NN cite is a finding; check is mechanical
- **Verdict: ONE (partial)**
- `mp-tix :105` / `mp triage/AGENT-BRIEF.md :204` show the failure: paths and line numbers "go stale". The cure prescribed there is avoidance, not a check.
- `ps-lesson :3`: "Encode the rule as a lint, metadata flag, runtime check, or script instead of more text". This is generic and does not cover cites.
- **Recommend PREFERENCE.** It is the twin of SR2 (cites are required, so drift must be caught), and the evidence is #636 (3 drifted cites). It is mechanical, so the Review check should name the script.

### SR4: before approval, open questions empty or each names a decider and why non-blocking
- **Verdict: TWO** (for "resolve open questions before approval; the human decides"); NONE for the "named decider + non-blocking" exception
- A `ps-plan :6`: "Settle open questions by prototype before you write … Ask the operator only about a product or preference call".
- B `hl-dd :80-81`: "you must NOT resolve or close a question yourself … Only the user can resolve a design question". `ao-sdd :172-173` lists Open Questions, then asks the human to approve.
- **Wording:** "Before approval, every open question is answered or names who decides it and why building can start without it, because an ownerless question stays open after the build." The deferral clause = preference (evidence DESIGN-S6:617-644).
- **Project-specific:** `/approved`, "REQ".

### SR6: story check: actor/action/benefit, checkable scenarios, out-of-scope, Escalation answer
- **Verdict: TWO for three parts; ONE for Escalation**
- Actor/action/benefit: `pl014 :119` "MUST include user story title, role, goal, and benefit"; `mp-spec :35` "As an <actor>, I want a <feature>, so that <benefit>".
- Checkable: `pl014 :133` "completion can be objectively verified through acceptance criteria"; `ao-plan :89` "[Specific, testable condition]".
- Out of scope: `mp-spec :67-69`; `hl-plan :28-30` "What We're NOT Doing … to prevent scope creep".
- Escalation: only `ao-doubt :19,:22` ("crosses a module or service boundary", "data migration") marks these as needing heavier scrutiny.
- **Wording:** KEEP the three parts. The Escalation clause = **PREFERENCE**, reworded generically: "migration, security or cross-module work gets a full spec".
- **Project-specific:** the "Escalation" section name and "full REQ" are Aruvii story-template terms. Keep the template field name in agent-platform docs.

### SR7: decide review tier from what the diff is; unplaceable path = code
- **Verdict: TWO** (for "classify docs-only positively; lighter path only then"); NONE for the four named tiers
- A `ps-babysit :7`: "Small or docs-only PRs get `check`, not `drive`".
- B `ao-ci :323`: "Use path filters to skip unrelated jobs (e.g., skip e2e for docs-only PRs)".
- Both pick the light path by a positive match on what the diff *is*. Falling back to the full path is implied, not stated.
- **Wording:** "Choose the lighter review only when every changed path matches a named non-code kind; any other path is reviewed as code, because a negative gate lets build files into the cheap tier." The four tiers (operability, authority doc) = preference.
- **Project-specific:** "authority doc" is an Aruvii/rulebook term; keep it in the Decided edges or the agent-platform docs.

---

## Suggested line under the When X, use Y table (T2 style)

`Operator preference, 2026-11-02 (SRC2), in whole or in part: GA2, GA3, GA5, GA6, CV1, AC7, AC8, AC9, SR1, SR3, SR4, SR6, SR7.`
(Whole: GA2, GA6, CV1, AC7, AC8, SR3. Part: GA3 never-tier, GA5 one-Then, AC9 declare-first, SR1 miss-metric, SR4 deferral clause, SR6 Escalation, SR7 tier names.)

Move to agent-platform docs: `/approved` + MR mechanics (AC10, SR4), "REQ"/"analyst"/"discovery" naming (GA1, GA2, AC9), and the Escalation field (SR6).

## Summary

| id | verdict | recommendation |
|---|---|---|
| GA1 | TWO (plBA, jf-tpl; runtime-free pl058) | KEEP core; drop REQ/analyst, say "spec" |
| GA2 | ONE (jf) | PREFERENCE |
| GA3 | TWO concern tags (cuke-api, pl058); NONE never-tier (plinth contradicts) | reword; never-tier = PREFERENCE |
| GA4 | TWO (pl058, cuke) | KEEP |
| GA5 | TWO (cuke+pl058 Then; plBA+jf failure) | reword "observable Then"; "one Then" = PREFERENCE |
| GA6 | ONE weak (pl058 example) | PREFERENCE, reword to plain behaviour sentence |
| CV1 | NONE (jf contradicts) | PREFERENCE, fold into GA2 example |
| AC7 | NONE | PREFERENCE (strong evidence !230) |
| AC8 | ONE derived (cuke Background) | PREFERENCE or merge into GA4 edge |
| AC9 | TWO glossary (mp, cuke); ONE declare-first (plBA) | reword; drop "sibling REQs" |
| AC10 | TWO (plBA, ao-sdd) | reword generic; `/approved`+MR to agent-platform |
| SR1 | TWO whole-review (mp, goog); NONE miss-metric | reword; goog navigate early-stop = Decided edge |
| SR2 | TWO+ (ps, hl, jf) | KEEP, de-Aruvii "origin/master"/REQ |
| SR3 | ONE partial (mp stale, ps lint) | PREFERENCE (twin of SR2) |
| SR4 | TWO resolve-before-approval (ps, hl; ao) | reword; deferral clause PREFERENCE; `/approved` project-specific |
| SR6 | TWO for actor/benefit, checkable, out-of-scope; ONE Escalation (ao) | KEEP 3 parts; Escalation PREFERENCE, field name to agent-platform |
| SR7 | TWO positive docs-only gate (ps, ao) | reword; four tier names PREFERENCE |

---

## T3 source audit (SRC2): program-design, diagrams, writing-docs, writing-references

Date 2026-11-02. Read-only. Clones: `/tmp/claude-0/-home-user/1db0da3b-3ba2-53f3-a8f2-7fff5488961d/scratchpad/t3/refs-b/`.

## Source key

| tag | repo@commit | file |
|---|---|---|
| `pst-arch` | cursor/plugins@ae5650febf | `pstack/skills/architect/SKILL.md` |
| `pst-rf` | same | `pstack/skills/architect/references/design-red-flags.md` |
| `mp-tospec` | mattpocock/skills@4ae2317ddb | `skills/engineering/to-spec/SKILL.md` |
| `mp-dit` | same | `skills/engineering/codebase-design/DESIGN-IT-TWICE.md` |
| `mp-wfa` | same | `skills/productivity/writing-for-agents/SKILL.md` |
| `mp-wd` | same | `.agents/writing-docs.md` |
| `mp-teach` | same | `skills/productivity/teach/SKILL.md` |
| `ad-plan` | addyosmani/agent-skills@301b02b12b | `skills/planning-and-task-breakdown/SKILL.md` |
| `ad-doc` / `ad-spec` / `ad-src` | same | `skills/documentation-and-adrs/`, `spec-driven-development/`, `source-driven-development/` `SKILL.md` |
| `hl-show` | humanlayer/humanlayer@316e74ef9a | `apps/riptide-rpi-claude-plugin/skills/create-structure-outline/references/show-me.md` |
| `hl-out` / `hl-plan` / `hl-impl` / `hl-prd` | same | `apps/riptide-rpi-claude-plugin/skills/{create-structure-outline,create-plan,implement-plan,create-prd}/SKILL.md` |
| `ja-arch` | Jeffallan/claude-skills@078a25cc5b | `skills/architecture-designer/SKILL.md` |
| `pl-cls` / `pl-dep` / `pl-033` | jabrena/plinth@e0b6fb1d96 | `skills/033-architecture-diagrams/references/033-architecture-diagrams-{uml-class,deployment}.md`, `skills/033-architecture-diagrams/SKILL.md` |
| `gh-dia` | github/docs@ab7258a037 | `content/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams.md` |
| `mm` | mermaid-js/mermaid@370c4af57f | `docs/intro/index.md` |
| `wtd` | writethedocs/www@7533c2cbc9 | `docs/guide/writing/docs-principles.rst` |

Independence notes:
- **mattpocock `skills/engineering/pr/SKILL.md` is not independent of `hl-show`.** Its `CREDITS.md:3` says the visuals menu (call trees, file trees, Mermaid, diffs) is "reproduced almost word for word" from humanlayer `show-me`. It is never counted as a second source next to humanlayer.
- `pst-arch` and `mp-dit` both cite Ousterhout's "design it twice". They are still two projects, written separately.
- humanlayer `.claude/commands/create_plan.md` is gone at HEAD. The current planning skills are under `apps/riptide-rpi-claude-plugin/skills/`.
- **NOT OPENED** (DNS blocked in this session): c4model.com, developers.google.com (Google style guide), docs.github.com, diataxis.fr, Nygard's cognitect.com post. I read the GitHub docs and Mermaid docs from their source repos instead. Diátaxis (evildmp@957c09ca40) and adr.github.io (@4f9bd9eada) were cloned and searched, but neither states any of these rules. **None of them is cited below.**

---

## program-design.md

**PD1**: a design that changes call paths shows the call tree as a fenced `diff` (+ new, − removed).
- Verdict: **ONE.**
- A: `hl-show :84-95`, "For a call-tree or call-stack change:" followed by a ```` ```diff ```` tree with `+`/`-` lines. Also `hl-out :46` "Use `diff` blocks for focused changes to existing shapes".
- B: none. mattpocock `pr/SKILL.md :97-134` is a copy of humanlayer (see above). pstack, addy, plinth and Jeffallan have no call-tree diff.
- Recommendation: **PREFERENCE.** The ledger evidence (!238 call change decided in review) shows the need.

**PD2**: a file-tree diff marks every new, modified and deleted file, tests included, each with a one-line purpose.
- Verdict: **TWO** for "list every file touched, tests included". **ONE** for the diff form and the purpose line.
- A: `ad-plan :99-101`, "**Files likely touched:** `src/path/to/file.ts` `tests/path/to/test.ts`". Also `ad-spec :209` "Files: [Which files will be touched]".
- B: `hl-out :80`, "a compact change outline that shows the relevant file tree, key data structures, … and tests". The diff form with purpose comments is `hl-show :71-82` (`+│   └── show-me.ts  # expands the slash command`).
- A and B are independent (addyosmani vs humanlayer).
- Wording: "List every file the design adds, changes or deletes, test files included, because a plan with no test file gives the reviewer nothing to grade."
- The `diff` form and the purpose line are a preference (humanlayer only).

**PD3**: new records, sealed interfaces, ports and public signatures are written in Java with no bodies, and the caller's usage comes first.
- Verdict: **TWO.**
- A: `pst-arch :9`, "Sketch types, function signatures, class shapes, and module boundaries with `not implemented` bodies". `pst-arch :79`, "The caller's usage is written first and the type sketch derived from it."
- B: `mp-dit :34-35`, "Interface (types, methods, params, plus invariants, ordering, error modes)" and "Usage example showing how callers use it".
- Supporting (third project): `hl-out :160`, "prefer highlighting signature changes … The structure outline is our 'c header files'".
- Wording, made language-neutral (the "Java" part is house style): "Write the caller's usage first, then the new types and public signatures with no bodies, because a type left out of the design gets settled ad hoc in code."

**PD4**: build order is end-to-end slices that can be poked, never migration → service → API → UI.
- Verdict: **TWO.**
- A: `ad-plan :59`, "Instead of building all the database, then all the API, then all the UI — build one complete feature path at a time". Also `:77`.
- B: `hl-out :55`, "Avoid horizontal phases like 'add all types', 'add API endpoints', 'implement UI'". `hl-out :66`: "That creates handoff problems and partially finished work."
- Wording: **KEEP.** Optionally drop "(curl, UI, IT)" as examples.

**PD5**: every slice states the `make` target (and `TEST=` filter) that proves it, plus any manual step.
- Verdict: **TWO.**
- A: `ad-plan :92-95`, "Tests pass: [the repository's focused-test command] … Manual check: [description of what to verify]".
- B: `hl-out :166-167`, "`#### Automated Verification`: runnable commands (typecheck, tests, lint) / `#### Manual Verification`". Also `hl-plan :37`.
- Wording: "Every slice names the command that proves it, plus any manual step, because a check with no named command is never run."
- **Project-specific:** `make` and `TEST=` are our tooling. Move them to agent-platform docs.

**PD6**: paths, signatures and trees go in the design section, never in the REQ, which stays behaviour-only.
- Verdict: **TWO.**
- A: `mp-tospec :55`, "Do NOT include specific file paths or code snippets. They may end up being outdated very quickly."
- B: `hl-prd :8`, "It answers WHAT we're building and WHY … Leave technical implementation to the downstream TDD." Also `hl-prd :26`.
- Counter-source: `ad-spec :96-106` puts project structure and code style inside the spec.
- Wording: "Keep the spec behaviour-only; put file paths, signatures and trees in the design document, because paths and code in a spec go stale quickly."
- **Project-specific:** "draft MR", "REQ" and `docs/design/` are our terms. Use spec and design document.

**PD7**: during stage 6, a needed change to an approved type, signature or placement is posted on the MR before coding past it.
- Verdict: **TWO.**
- A: `pst-arch :53`, "Deviations from it are signal to surface, not friction to absorb silently."
- B: `hl-impl :81-83`, "If the implementer agent reports a mismatch … Present the issue clearly to the human / Wait for guidance before proceeding".
- Wording: "When the build needs to change an approved type, signature or file placement, record the change where the design is reviewed before coding past it, because an unrecorded deviation leaves the design check judging against a guess."
- **Project-specific:** "stage 6" and "MR" are ours. The L1 plan already maps them to phase names.

## diagrams.md

**DG1**: a diagram in a `.md` file is a ```` ```mermaid ```` fence; a diagram in chat, Discord or an MR comment is plain fenced ASCII.
- Verdict: **TWO** for the first half. **NONE** for the second half.
- A: `gh-dia :22`, "add Mermaid syntax inside a fenced code block with the `mermaid` language identifier". Also `mm :36`, "uses Markdown-inspired text definitions".
- B: `ja-arch :75`, "High-level architecture diagram (Mermaid preferred …)". Also `hl-show :46-48`.
- GitHub Docs, Mermaid, Jeffallan and humanlayer are four independent projects.
- Counter-sources:
  - `gh-dia :16` says Mermaid also renders in issues and pull requests, which weakens the ASCII-in-comments half.
  - `pl-033 :11` uses PlantUML.
- Wording: "Commit a diagram to Markdown as a ```` ```mermaid ```` fence, because text diagrams are reviewed and updated with the code."
- The chat/comment ASCII half is a preference. **Project-specific:** Discord.

**DG2**: call trees and file trees use fenced `diff` text; Mermaid is for component, sequence, state, ER and class diagrams.
- Verdict: **ONE.**
- A: `hl-show :18-26` (call tree as text), `:37-44` (file tree as text), `:46` "Show component interaction, control flow, or data flow with Mermaid", `:58` "Use `diff` when the point is what changes".
- B: none independent. mattpocock `pr` copies humanlayer. mattpocock `improve-codebase-architecture/SKILL.md :41` says the opposite: "use Mermaid when relationships are graph-shaped (call graphs, …)".
- Recommendation: **PREFERENCE.** The ledger evidence (boxes cannot mark new or removed calls) is the reason.

**DG3**: every node label is a class, module, table or endpoint that `grep` finds on master, except `+` lines in a design diff.
- Verdict: **TWO** for "labels name real code elements". **NONE** for the grep/master test and the `+` exception.
- A: `pl-cls :417`, "Class diagrams must reflect actual type names, relationships, package boundaries". Also `pl-cls :305`, "Include actual class names, methods, and attributes from codebase".
- B: `hl-show :117`, "use real labels and data". This is said of HTML artifacts, so it is weaker.
- Plinth and humanlayer are independent.
- Wording: "Label each node with the name the code uses, because a node naming deleted or invented code teaches behaviour that is not there."
- The grep check and the `+` exception are a preference tied to PD1.

**DG4**: each diagram answers one question; a second question gets a second diagram.
- Verdict: **TWO** (partial).
- A: `pl-cls :417`, "Prefer several focused diagrams over one unreadable diagram when the scope is large." Also `pl-dep :106`, "service-level details can be split into a second deployment detail diagram".
- B: `hl-show :6`, "Pick the smallest view that makes the key point clear." Also `hl-out :40`, "Use the smallest set of visual views needed".
- The sources say "focused / one key point". Neither says "one question from a type table".
- Wording: "Give each diagram one point; split a second point into a second diagram, because a diagram that answers several questions serves none of its readers."
- The "type table" link is ours.

**DG5**: if the diagram needs prose beyond a one-line caption, redraw it smaller.
- Verdict: **ONE** (partial).
- A: `hl-show :6`, "Skip the preamble and keep prose brief. Pick the smallest view". Also `hl-out :44`, "Place a short description between visual views".
- Plinth offers "comprehensive explanations for each diagram" (`pl-033 :211`), so it does not support DG5.
- Recommendation: **PREFERENCE.** The ledger reason is "NO-REASON", so the operator should supply one.

**DG6**: put the diagram in the ADR, REQ or design doc it illustrates; no standalone diagrams file.
- Verdict: **TWO** for the first half. **NONE** for the ban.
- A: `ja-arch :73-76`. The one architecture output holds "High-level architecture diagram" next to "Key decisions with trade-offs (ADR format)".
- B: `hl-out :40-46`. Visual views sit inside the outline, with "a short description between visual views".
- Counter-source: `pl-033 :191-194` offers a "/diagrams folder" and "separate folders". It also offers "Integrated with existing documentation".
- Wording: "Put a diagram in the document whose decision it illustrates, because a separate diagrams file is not read with that decision."
- "No standalone diagrams file" is a preference.

## writing-docs.md

**WD1**: no `[confirmed: …]` or in-text verification markers; a claim that needs proof gets a cite the drift check can run.
- Verdict: **ONE** (for "cite so readers can verify"). **NONE** for the ban on markers.
- A: `ad-src :143`, "Every framework-specific pattern gets a citation. The user must be able to verify every decision."
- No source discusses verification stamps. "Drift check" is our tool (project-specific).
- Recommendation: **PREFERENCE.**

**WD2**: do not write counts that change as a side effect of unrelated work; stable deliberate facts are fine.
- Verdict: **TWO** (partial).
- A: `mp-wfa :79`, "Leave the one-file, one-command lookups to the environment, where they cannot go stale." Also `:80`, a line loses relevance "by going stale".
- B: `wtd :156-157`, "write content that is version-agnostic and thus in less need of maintenance".
- The sources say "avoid facts that will go stale / are cheaply looked up". Neither names counts.
- Wording: "Leave out facts that change as a side effect of other work, such as counts, because they go stale without anyone editing the doc."
- Google's "future/time-sensitive" page would likely be a third source. **NOT OPENED.**

**WD4**: write the operational fact even when unflattering; a reassuring false line is the worst a doc can carry.
- Verdict: **TWO.** This upgrades the 2026-10-04 "PROJECT DECISION: no reference found" note.
- A: `wtd :150`, "Consider incorrect documentation to be worse than missing documentation."
- B: `mp-wd :56`, "say the unflattering thing where it is true".
- Supporting (third): `ad-doc :265`, "Do not replace an unsupported claim with an invented example or a stronger guarantee."
- Wording: **KEEP.**

**WD5**: a bug corrects the REQ it violates, in place; a chore carries scope and ACs in the issue; a new REQ is for missing behaviour.
- Verdict: **ONE** (partial).
- A: `ad-spec :218-220`, "The spec is a living document … update the spec first, then implement."
- No second source. The bug/chore/new-REQ split is our process.
- Recommendation: **PREFERENCE.** **Project-specific:** REQ, chore and AC routing look like agent-platform process. Consider moving it next to WD6 in agent-platform docs.

**WD7**: each fact lives in one file, others link to it; generated docs are never hand-edited.
- Verdict: **TWO** for single source of truth. **ONE** for the generated-docs clause.
- A: `mp-wfa :78`, "Keep each meaning in a **single source of truth** … **Duplication** … costs maintenance and tokens".
- B: `wtd :194-199`, "Eliminate content overlap between separate sources … prevent any parallel maintenance".
- Supporting for the derive half: `pst-rf :92`, "Keep one list and derive the others from it."
- Wording: **KEEP** the first clause. The "never hand-edit generated docs" clause is a preference unless a reader accepts `pst-rf :92`.
- Note: `wtd :77` (ARID, "Accept (some) Repetition") softens the rule.

## meta/references/writing-references.md

**SRC1**: every rule cites the reference text it comes from, read at path:line; our code is never a source; an unsourced rule is tagged "project decision".
- How SRC1 and SRC2 relate:
  - SRC2 (`00-reference-format.md:51-56`, ledger row 671) keeps SRC1's citation requirement and its ban on our own code as a source.
  - SRC2 raises the bar from one cited source to two independent sources, with one company counting as one source.
  - SRC2 replaces the "project decision" tag with the single "Operator preference, DATE (SRC2)" line under the When X, use Y table.
  - The ledger already marks SRC1 "AMENDED by SRC2".
  - writing-references.md should state the merged rule under both ids (or SRC2 alone, with SRC1 noted as superseded), never two rules that disagree.
- Verdict: **TWO** for "cite a checkable source for every rule".
- A: `ad-src :143`, "The user must be able to verify every decision." Also `ad-src :76-81`, "never cite as primary sources: … Your own training data".
- B: `mp-teach :95`, "Lessons should be littered with citations - links to external resources to back up any claim made."
- The "two independent sources" threshold and "our code is never a source" have no external source. They stay **operator preference** (ledger: operator 2026-10-03 and 2026-10-31).
- Wording: "Cite every rule's source at path:line@commit or URL#section, because an uncited rule cannot be checked."

---

## Summary

| id | verdict | recommendation |
|---|---|---|
| PD1 | ONE (hl-show; mattpocock `pr` is a copy) | PREFERENCE |
| PD2 | TWO (file list incl. tests); diff form ONE | reword; diff form = preference |
| PD3 | TWO (pst-arch, mp-dit) | reword language-neutral (drop "Java") |
| PD4 | TWO (ad-plan, hl-out) | KEEP |
| PD5 | TWO (ad-plan, hl-out) | reword; `make`/`TEST=` → agent-platform |
| PD6 | TWO (mp-tospec, hl-prd) | reword spec/design; "MR/REQ" project-specific |
| PD7 | TWO (pst-arch, hl-impl) | reword; drop "stage 6"/"MR" |
| DG1 | TWO (Mermaid in .md); ASCII half NONE | reword; ASCII half = preference; Discord project-specific |
| DG2 | ONE (hl-show; counter-source mattpocock) | PREFERENCE |
| DG3 | TWO (real names: pl-cls, hl-show); grep/`+` NONE | reword; check/exception = preference |
| DG4 | TWO partial (pl-cls, hl-show) | reword "one point per diagram" |
| DG5 | ONE partial (hl-show) | PREFERENCE (needs a reason) |
| DG6 | TWO partial (ja-arch, hl-out); ban NONE | reword; ban = preference |
| WD1 | ONE partial (ad-src) | PREFERENCE; "drift check" project-specific |
| WD2 | TWO partial (mp-wfa, wtd) | reword |
| WD4 | TWO (wtd, mp-wd; + ad-doc) | KEEP (upgrade from project decision) |
| WD5 | ONE partial (ad-spec) | PREFERENCE or move to agent-platform docs |
| WD7 | TWO (mp-wfa, wtd); generated clause ONE | KEEP clause 1; clause 2 = preference |
| SRC1 | TWO (ad-src, mp-teach) for citing; threshold/own-code NONE | merge with SRC2; rest = preference |

Suggested preference line for program-design.md: `Operator preference, 2026-11-02 (SRC2), in whole or in part: PD1, PD2.`
For diagrams.md: `DG1, DG2, DG3, DG5, DG6`.
For writing-docs.md: `WD1, WD5, WD7`.
For writing-references.md: `SRC1`.
