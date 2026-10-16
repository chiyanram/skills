# Brief — G9c candidates (#34), 2026-10-04

Produce candidate rules for ONE G9c sub-domain (named in your prompt). Nothing is approved; the operator approves on a review page.
Write ONLY your output file, incrementally. No commits, no tracker edits, never `cd`.

Inputs (worktree W = /Users/chiyanram/workspace/skills/.claude/worktrees/mattpocock-skills-wayfinder-2df0ab):
- W/research/14-disposition-table.md §G9c — the R12 rows for your files (target · action · reference excerpts · our learnings).
- W/research/00-decision-register.md — what is ALREADY decided (crq stages, runner, rebase, review shape G3, forge idea 1, …). Do not re-propose a decided item; list it under "already decided" with its ticket.
- W/research/19-approved-rules.md — approved rules; do not duplicate. W/research/00-reference-format.md — the 5 sections + SRC1/GB2.
- Our current text: agent-platform branch `chore/643-one-rulebook-skeleton` @71b5deb4 (`git -C /Users/chiyanram/workspace/agent-platform show 71b5deb4:<path>`, paths under .agents/skills/ and .claude/) and origin/master for code evidence.
- REFS = /Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/ (pstack = cursor-plugins, mattpocock-skills, addyosmani-agent-skills, openclaw-openclaw, kunchenguid-firstmate, humanlayer-*, rameezk-forge, jabrena-plinth, plinth-*); primary docs via WebFetch (PostgreSQL, Flyway, Git, GitLab, Gradle) cited URL + §.

SRC1 (binding): every candidate cites the reference text it comes from, READ at path:line (quote ≤15 words). Our code / CLAUDE.md / our skills are never a source — only evidence (a Bad, a count, a past incident #NNN). A rule no reference states → mark "project decision?" and cite the incident that motivates it; the operator decides.
G1b targets: directory MUSTs → `<dir>/AGENTS.md`; file-type MUSTs → root AGENTS.md blocks (≤3 each); `.claude/rules/` is deleted. Restate each R12 row's target under G1b.

Output shape:
1. **R12 rows** — one line per current file: target (G1b-corrected) · action · deletions · agree/change + why.
2. **Candidates** grouped by target reference: `ID — rule (imperative, ≤30 words) — source path:line "quote" — evidence (our Bad/incident) — ADOPT | ADAPT | project decision?`. Prefix IDs per your sub-domain.
3. **When X use Y** rows, **Decided edges** (Skip when / Do not skip when), **Review checks** per reference.
4. **Already decided** (item → ticket). 5. **Open questions** (≤6, each with facts + recommendation).
Keep the file ≤350 lines. Final message: counts + the open questions.
