# Brief for every per-repo deep report (one-rulebook map, 2026-10-01)

The operator's complaint: earlier passes were comparative summaries; nobody wrote a detailed, file-grounded report
PER REPO on its actual approach. This report fixes that for your repo(s). Read the ACTUAL FILES — no summarising from
READMEs alone. Read-only everywhere; write ONLY your report file. No commits, no GitLab. Absolute paths; never `cd`.

Context to read first (under /Users/chiyanram/workspace/agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/):
map.md (Decisions so far), requirements.md, design-overview.md. Our problem in one line: one rulebook (rules, roles,
review) shared by a laptop /crq pipeline and an agent fleet (coordinator + briefed worker sessions), clean code and
low review cost, a future AG-UI web app as coordinator.

Report shape (markdown, tables and trees over prose, quotes < 15 words, every claim with path:line):
1. What it is · maturity · stars if known · the one idea it is built around.
2. File tree of what matters (2–3 levels), with one line per important file.
3. Its approach, section by section, each with path:line evidence:
   a. Rules / standards: where they live, how kept single-source, what loads always vs on demand.
   b. Process / workflow: stages, routing (playbooks/commands), human gates, handoffs, state on disk.
   c. Roles / personas / souls / agents: what they are made of, who writes them, can they change.
   d. Review & verification: shape, inputs, criteria selection, output format, caps, cost control.
   e. Context engineering: compaction, subagents, briefs, artifacts.
   f. Packaging & distribution: plugin/npm/CLI/symlinks, per-machine config, multi-harness support.
   g. Hosting / UI (if any): headless, daemon, protocol, approvals.
4. Three best concrete prompts/text excerpts worth studying (path:line ranges, why each is good).
5. Against our decisions (G1 rules layers · G2 one crq + role labels · G3 Standards‖Spec review · G5 5-section
   references · G6 coordinator + briefed workers · G4 plugins everywhere / coordinator-as-contract / tiers):
   confirms / contradicts / new idea — one row each.
6. What we should ADOPT, ADAPT, or REJECT from this repo — ranked, with the file that shows it.
7. Files actually read (full list of paths) — required.
Length: as long as the repo deserves, typically 1500–3000 words.
