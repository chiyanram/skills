# 41 · planning domain — CANDIDATE rules (not decisions)

Ticket #35 G9d · map chiyanram/skills#9. Every rule below is a **proposal** for the operator's review page.
Target: agent-platform `.agents/skills/planning/references/` (branch `chore/643-one-rulebook-skeleton`).

Path prefixes:
`W/` = agent-platform worktree `crq-597-b837e3` · `R/` = `W/.scratch/one-rulebook/refs/` ·
`SR/` = `W/.agents/skills/spec-review/SKILL.md` · `AR/` = `W/.agents/skills/architecture-review/SKILL.md`

Ref pins (`git rev-parse --short HEAD`): ACE `f2bc7ae` · cursor-plugins/pstack `2eb7ed4` · mattpocock-skills `d81f3a1` ·
humanlayer-humanlayer `99abe67` · addyosmani-agent-skills `2686b62` · openclaw `b94e5177` · kunchenguid-firstmate `549e07f`.

Kinds: **MUST** (L2/always) · **reference rule** · **review check** · **mechanical** (→ named check).

---

## 1 · spec-review.md — is a REQ (or story) buildable, complete, consistent

Today: `SR/` (367 lines, A/B/C/D/T criteria, five-part REF/FIRES/CHECK/MET/EDGE) + `MEMORY.md` (one near-miss).
Candidates below are **gaps or changes**; the existing criteria move as-is unless listed under DROP.

### SR1 — All findings in one pass
Rule: Report every finding the rubric produces in one review round; a finding first raised in round N+1 on unchanged text is a reviewer miss.
Source: mattpocock `R/mattpocock-skills/skills/productivity/grilling/SKILL.md:8` ("Ask the whole frontier in one round"); ours: fleet self-reports `00-fleet-self-reports.md` spec-reviewer row — #576 took 3 rounds, analyst row #576 4 gaps one per round.
Kind: review check (output contract).
Recommend: adopt — the most-repeated fleet failure on this axis; cheap to state.

### SR2 — Every existing-behaviour claim is verified at HEAD
Rule: Each sentence in a REQ asserting how the system behaves today must cite `file:line` on `origin/master`; the reviewer opens each cite; an unverified claim is a finding.
Source: humanlayer `R/humanlayer-humanlayer/.claude/commands/create_plan.md:68-72` ("Cross-reference the ticket requirements with actual code"); `research_codebase.md:16` ("ONLY describe what exists"); ours: fleet analyst row #585 (build-cache claim unverified), spec-reviewer row "unverified existing-behaviour claims". Generalises `SR/:215-220` C-09, which today fires only on "no impact" claims.
Kind: review check (new criterion C-11, BLOCKER when the claim is false, GAP when uncited).
Recommend: adopt — C-09 already proves the pattern; this widens it to every factual claim.

### SR3 — Cites are re-checked against current master
Rule: A `file:NN` cite in a REQ or issue body that no longer points at the named symbol is a finding; the check is mechanical, not reviewer memory.
Source: ours #61 row 15 (#636 "`file:NN` cites in stories unchecked"); fleet spec-reviewer row "line drift vs HEAD"; `W/scripts/check-doc-drift.sh:94` §2 already checks file:line citations but only over AGENTS.md, CLAUDE.md, `docs/architecture`, `.claude/rules` (`W/Makefile:357`).
Kind: mechanical → extend `check-doc-drift.sh` §2 to `docs/spec/REQ-*.md` and (via `glab`) the issue body.
Recommend: adopt — the script exists; scope is a path list change. Note `SR/:321` (anchor findings to headings) stays.

### SR4 — No open question survives approval
Rule: Before `/approved`, the REQ's open-questions list is empty or each item names who decides it and why it does not block building.
Source: humanlayer `create_plan.md:338-343` ("Do NOT write the plan with unresolved questions"); keeps `SR/:39-41` rule 1 intact (reviewer surfaces, never answers).
Kind: review check (D-04).
Recommend: adopt — closes the gap between "surface it" and the gate.

### SR5 — A spec does not contradict decided work
Rule: Grep closed issues, accepted ADRs and merged REQs on the same subject; a REQ reversing a decision without naming it is a BLOCKER.
Source: ours fleet analyst row (D-F8 vs #533 — contradicted decided work); extends `SR/:130-135` A-03 (ADRs only) to decided issues/REQs.
Kind: review check (widen A-03).
Recommend: hold — needs one agreed place where "decided" lives (issue label or decision log) before it is checkable.

### SR6 — Story pre-check lives here too
Rule: A story is checked for actor/action/benefit, checkable scenarios, an out-of-scope list, and an Escalation answer (migration, security, cross-module → full REQ).
Source: ours `W/docs/agents/personas/spec-reviewer.md:20-24`, `analyst.md:46-47`; fleet spec-reviewer row "missing Escalation sections"; disposition `14-disposition-table.md:177` (checklists → spec-review.md).
Kind: review check (new short group S, story tier).
Recommend: adopt — the persona split deletes its only home.

### SR7 — One change-class gate, stated positively
Rule: Decide the review tier from what the diff **is** (code · operability · authority doc · process/docs); an unplaceable path is code.
Source: `AR/:49-60` rule 4 (positive class table, "When you cannot place a path, it is code"); replaces `SR/:52-66` rule 5, which is stated as what the diff is not.
Kind: reference rule.
Recommend: adopt — two tier gates with different wording drift; AR's form is the safer one.

### SR8 — ND-7: architecture-review A–E at stage 5
Rule (option A, recommended): Merge AR groups A–E into `spec-review.md` as one stage-5 rubric, deduplicating the eight overlapping criterion pairs; F-01 moves to the review Spec verdict.
Rule (option B): Keep AR A–E as a separate `planning/references/design-review.md`, both read at stage 5 by the spec-reviewer role.
Source: `14-disposition-table.md:117,258` (ND-7); overlap pairs checked this run:
```
SR A-02 :123 ~ AR A-06 :156  shared contract     SR T-05 :289 ~ AR C-03 :245  flag off path
SR A-03 :130 ~ AR A-07 :163  ADR contradicted    SR C-03 :173 ~ AR D-07 :319  roles / RBAC
SR T-01 :261 ~ AR A-01 :121  module edge         SR C-05 :187 ~ AR D-01 :277  failure path
SR T-02 :268 ~ AR A-03 :135  Spring AI confined  SR C-06 :194 ~ AR D-08 :326  logging
```
Kind: reference rule (structure).
Recommend: **A, merge** — one reader at stage 5 (G3/G2), 8 duplicate pairs vanish, ~9.1k words → one file; B keeps two rubrics that already disagree on the tier gate (SR7).

**DROP from today's spec-review**
- `SR/:60-66` and `AR/:72-78` — the #540 token-cost narrative: history, belongs in the commit/ADR, not the rubric.
- `SR/:83` — authority row `.agents/skills/code/SKILL.md/` (trailing slash, a skill is not an authority for a REQ); and `:82` "CLAUDE.md §Critical Architecture Rules" — section names no longer exist after the AGENTS.md flip.
- `SR/:305-315` "Does not own" rows naming `spec-design-reviewer` / `architecture-review` — both agents are deleted (disposition :118-119).
- `MEMORY.md` as a separate file — merge its one entry into C-09's EDGE (disposition :116).

---

## 2 · acceptance-criteria.md — gaps only

Already approved, **not re-proposed**: GA1–GA6 (`19-approved-rules.md:60-64,128`), CV1–CV6 (`31e-conventions.md`).

### AC7 — Scenarios cover state that existed before the change
Rule: When a change alters stored data or a default, at least one scenario's Given is state created before the change (old row, unseeded key).
Source: ours `14-disposition-table.md:114` (P1:9 "AC-6 proved only on new rows"); fleet qa row "ACs asserting defaults not behaviour"; `SR/MEMORY.md:9-13` (un-defaulted reader).
Kind: reference rule + review check.
Recommend: adopt — the one AC gap with two independent fleet incidents.

### AC8 — Prune columns that never vary
Rule: An Examples column whose value is identical on every row moves to Background or the Given; it is not a placeholder.
Source: today `W/.agents/skills/planning/references/acceptance-criteria.md:56-72` (rule 3); not covered by GA4 (which fixes header↔placeholder match only).
Kind: reference rule.
Recommend: adopt — the only one of today's four rules GA1–GA6 do not already carry.

### AC9 — Domain words only
Rule: Scenario text uses terms from the glossary and sibling REQs; a new noun is declared in the REQ before a scenario uses it.
Source: mattpocock `R/mattpocock-skills/skills/engineering/to-spec/SKILL.md:13` ("Use the project's domain glossary vocabulary"); `SR/:137-142` A-04.
Kind: reference rule (author side of A-04).
Recommend: adopt — GT1 makes the title the test name, so a bad word lands in code.

### AC10 — Changing an approved AC re-opens approval
Rule: Editing the text of an AC after `/approved` (not only its id) is a spec change: record it on the MR and get a fresh `/approved`.
Source: ours `W/.agents/skills/crq/SKILL.md:250` (approval covers the design as it stood); extends GA2 (ids only).
Kind: reference rule.
Recommend: adopt — GA2 freezes the id, nothing freezes the meaning.

### AC11 — Manual-only checks are labelled
Rule: A criterion no IT or smoke can assert is marked `# manual` with the exact human step; it never sits unmarked among automated scenarios.
Source: humanlayer `create_plan.md:345-359` (automated vs manual verification); AT1 (`19-approved-rules.md:31`).
Kind: reference rule.
Recommend: hold — AT1 says every AC is proven by IT or smoke; operator should decide whether manual ACs are allowed at all.

**DROP from today's acceptance-criteria.md**
- `:13-18` Gherkin-runtime history paragraph — superseded by GA1 (fenced gherkin, no runtime).
- `:26-54`, `:74-88` rules 1, 2, 4 — restated by GA5 (one checkable Then), GA4 (Outline + Background).
- `:13`, `:95` pointers to `mattpocock-skills:to-spec` "calls for it" — to-spec never names this file (disposition :114, R2:60).
- frontmatter `name: acceptance-criteria-writing` (`:2-3`) — it is a reference now, not a skill.

---

## 3 · program-design.md — NEW, stage-5 design content

Today: nothing (disposition `14-disposition-table.md:121`, "Not yet specified"). Evidence for need: !230 took 3 QA rounds;
ACE `R/humanlayer-advanced-context-engineering-for-coding-agents/ace-fca.md:322-323` ("a bad line of a plan could lead to hundreds of bad lines of code").

### PD1 — Call-tree diff for control-flow changes
Rule: A design that adds or reroutes a call path shows the call tree as a fenced `diff`, `+` for new calls, `-` for removed.
Source: ACE `wsff.md:491` ("Call-stack trees, for any orchestration or control-flow change"); `:536` (cheaper than deciding in code review).
Kind: reference rule + review check (stage 5).
Recommend: adopt.

### PD2 — File-tree diff with test files
Rule: The design shows a file-tree diff marking every new, modified and deleted file, test files included, each with a one-line purpose.
Source: ACE `wsff.md:507-515` (`# NEW` / `# MODIFIED` annotations); humanlayer `create_plan.md:215-219` (File / Changes per component).
Kind: reference rule + review check.
Recommend: adopt — also the input F-01 grades against.

### PD3 — Types and signatures, bodies left out
Rule: New records, sealed interfaces, ports and public method signatures are written in Java with no bodies; usage by the caller is written first.
Source: ACE `wsff.md:517` ("too internal for an architecture doc but that an agent might still get wrong"); pstack `R/cursor-plugins/pstack/skills/architect/SKILL.md:9,83` ("caller's usage is written first").
Kind: reference rule.
Recommend: adopt.

### PD4 — Thin end-to-end slices, not stack order
Rule: The build order is slices that each run end-to-end and can be poked (curl, UI, IT); never migration → service → API → UI as separate steps.
Source: ACE `wsff.md:542-566` ("Models love what I call 'horizontal plans'"); mattpocock `to-tickets/SKILL.md:31-34`; addy `planning-and-task-breakdown/SKILL.md:57-77`.
Kind: reference rule + review check.
Recommend: adopt — direct fix for review-time discovery (!230).

### PD5 — Each slice names its check as a make command
Rule: Every slice states the `make` target (and `TEST=` filter) that proves it, plus any manual step.
Source: humanlayer `create_plan.md:225-232,325` ("automated steps should use `make` whenever possible"); ours AGENTS.md make-front-door block.
Kind: reference rule.
Recommend: adopt.

### PD6 — Program design lives beside the REQ, not in it
Rule: Paths, signatures and trees go in the draft MR's design section (or `docs/design/`), never in the REQ, which stays behaviour-only.
Source: mattpocock `to-spec/SKILL.md:55` ("Do NOT include specific file paths or code snippets"); ours SR3 (cites rot).
Kind: reference rule.
Recommend: adopt — keeps the REQ stable after merge while the design is disposable.

### PD7 — Deviation from the sketch is surfaced
Rule: During stage 6, a needed change to an approved type, signature or file placement is posted on the MR before coding past it.
Source: pstack `architect/SKILL.md:57` ("Deviations from the sketch are signal worth surfacing"); `AR/:348-353` F-01.
Kind: reference rule (stage 6 side).
Recommend: adopt — gives F-01 a recorded baseline instead of a guess.

### PD8 — Two shapes before one, for a new seam
Rule: A new module, port or cross-module contract is sketched in two structurally different shapes before one is chosen; the rejected shape gets one line.
Source: pstack `architect/SKILL.md:35` ("Design it twice"); mattpocock `codebase-design/DESIGN-IT-TWICE.md:3`.
Kind: reference rule.
Recommend: hold — real cost per design; limit to new seams only if adopted.

**DROP** — nothing (new file). Reject: pstack `architect/SKILL.md:33-45` multi-model arena and opt-out human checkpoint — our stage 5 is a mandatory human gate.

---

## 4 · diagrams.md

Today: `W/.agents/skills/planning/references/diagrams.md` (34 lines).

### DG1 — Mermaid in committed docs, ASCII in replies
Rule: A diagram committed to a `.md` file is a ```` ```mermaid ```` fence; a diagram in chat, Discord or an MR comment is plain fenced ASCII.
Source: today `diagrams.md:3-12`; ND-10 default (`14-disposition-table.md:261`); R1:90 contradiction noted at `:120`.
Kind: reference rule.
Recommend: adopt — settles the recorded contradiction.

### DG2 — Program-design trees are `diff` fences, not Mermaid
Rule: Call trees and file trees in a design use fenced `diff` text; Mermaid is for component, sequence, state, ER and class diagrams.
Source: ACE `wsff.md:479` ("Mermaid ... lure you into a false sense that you are aligned"), `:487-489`.
Kind: reference rule.
Recommend: adopt — keeps DG1 and PD1–PD2 consistent.

### DG3 — Node labels are real, greppable names
Rule: Every node label is a class, module, table or endpoint name that `grep` finds on master.
Source: today `diagrams.md:31-32`.
Kind: mechanical → add Mermaid node labels to `check-doc-drift.sh` §4 named symbols (`:147`).
Recommend: adopt as reference rule now; mechanical check hold until §4 scope is widened (SR3 same change).

### DG4 — One diagram, one question
Rule: Each diagram answers one question from the type table; a second question gets a second diagram.
Source: today `diagrams.md:16-25,29-30`.
Kind: reference rule.
Recommend: adopt (keep).

### DG5 — A diagram that needs a paragraph is redrawn
Rule: If understanding the diagram requires prose beyond a one-line caption, redraw it smaller rather than adding text.
Source: mattpocock `R/mattpocock-skills/skills/engineering/improve-codebase-architecture/HTML-REPORT.md:55` ("If the diagram needs a paragraph to be understood, redraw the diagram").
Kind: reference rule.
Recommend: adopt — matches the operator's show-me style.

### DG6 — A diagram lives in the doc it explains
Rule: Put the diagram in the ADR, REQ or design doc it illustrates; no standalone diagrams file.
Source: today `diagrams.md:33-34`.
Kind: reference rule.
Recommend: adopt (keep).

**DROP from today's diagrams.md**
- `:5-8` GitLab/Artifact rendering facts and the PlantUML aside — environment facts (a cache, per writing-for-agents `SKILL.md:79`).
- `:10-12` pointer to `show-me` for chat sketches — show-me moves to the humanlayer plugin (disposition :136); DG1 replaces it.

---

## 5 · writing-docs.md — NEW (ND-8)

Today: only `W/AGENTS.md:430-454` («documentation» block). Disposition `:127,241,259` routes REQ numbering to crq stage 3, the rest to this file.

### WD1 — No trust stamps
Rule: Do not write `[confirmed: …]` or any in-text verification marker; a claim that needs proof gets a cite the drift check can run.
Source: `W/AGENTS.md:432-437`; ours #335 (65 stamps, 3 sampled all defective), REQ-069.
Kind: MUST (L2) — short enough to stay always-on.
Recommend: adopt.

### WD2 — Name the thing, not the tally
Rule: Do not write counts that change as a side effect of unrelated work; stable deliberate facts (Java 25, port 8080, a TTL) are fine.
Source: `W/AGENTS.md:439-441`; `W/scripts/check-doc-drift.sh:3-7` (PUBLIC_PATHS 17→20, 57→58 controllers).
Kind: mechanical → `check-doc-drift.sh` §1 + `--tallies`; plus reference rule.
Recommend: adopt — and wire `make doc-drift` into `make lint` (today it runs only on its own target, `W/Makefile:359-360`, not in `verify` `:379`).

### WD3 — Known-stale claims go in Doc drift
Rule: A claim known to disagree with the code is recorded in `ARCHITECTURE.md` §9 Doc drift, never fixed with a bracket or left silent.
Source: `W/AGENTS.md:444`; `W/docs/architecture/ARCHITECTURE.md:609`.
Kind: reference rule.
Recommend: adopt.

### WD4 — Uncomfortable operational truths go in
Rule: Write the operational fact even when it is unflattering; a reassuring false line is the worst line a doc can carry.
Source: `W/AGENTS.md:442-443` (only-the-api-runs-migrations line).
Kind: reference rule.
Recommend: adopt.

### WD5 — REQ only for new behaviour
Rule: A bug corrects the REQ it violates, in place; a chore with no owning REQ carries problem, scope and ACs in the issue; a new REQ is for behaviour the product lacks.
Source: `W/AGENTS.md:446-449`.
Kind: reference rule (crq stage 3 points here).
Recommend: adopt.

### WD6 — REQ number = issue number; ADR number cross-branch
Rule: A new REQ is `REQ-<issue>-slug`; a new ADR takes the next number free on master and every in-flight branch, per `docs/adr/README.md`.
Source: `W/AGENTS.md:449-453`; `W/docs/adr/README.md:26,59`; evidence: two `REQ-073-*` files exist on this branch (`docs/spec/REQ-073-jacoco-integration-coverage.md`, `REQ-073-tool-rename-name-uniqueness.md`). Rejects mattpocock `domain-modeling/ADR-FORMAT.md:27` ("Scan `docs/adr/` for the highest existing number") — that is the collision we hit.
Kind: mechanical → extend `check-migration-version.sh`-style cross-branch hook to `docs/adr/`; REQ side is a reference rule.
Recommend: adopt — and note the vendored ADR-FORMAT must carry our override (disposition :125).

### WD7 — One owner per fact
Rule: Each fact lives in one file; other docs link to it rather than restate it, and generated docs are never hand-edited.
Source: mattpocock `writing-for-agents/SKILL.md:78` (single source of truth); kunchenguid-firstmate `AGENTS.md:55` ("single owner of the top-level ... layout"); openclaw `docs/AGENTS.md:38` ("Generated docs, never hand-edit").
Kind: reference rule.
Recommend: adopt — it is the principle the whole one-rulebook move rests on.

### WD8 — Do not restate what the environment answers
Rule: Do not copy into docs what one command or file answers (make targets, versions in build files); write the why and the gotcha instead.
Source: mattpocock `writing-for-agents/SKILL.md:79` ("a document that restates it is a cache").
Kind: reference rule.
Recommend: hold — overlaps WD2/WD7; adopt only if the operator wants the "cache" word as a leading term.

**DROP from today's AGENTS.md block** (once writing-docs.md exists)
- `W/AGENTS.md:430-454` whole block → this file plus one L2 line for WD1; REQ-numbering table stays in crq stage 3 (disposition :127).
- `:451` "`REQ-001`–`REQ-073` keep their sequential numbers" — history; keep only the rule.
