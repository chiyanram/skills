# P1 lead judgment + comparison with the real QA round 1 (2026-10-01)

Verified by the lead at 70b84c0b: AgentEntity.java:77 `= 1`; V106 VARCHAR(20)/(40); V106 header never mentions the
UPDATE; CHECK added in a separate ALTER; AlertTriggerTypeSpec `valueOf(..) != null`; RunCheckpointEntity has no
agent_version (still absent at merged head c18cef8f); AlertTriggerTypeSpec junk still present at c18cef8f.

## Act on (≤5)
1. JPA writes current_version = 1 (Std 1 + Spec 1) — = real F1
2. AC-6 proved only on rows inserted after V106; no pre-existing seed; no configFormat check (Spec 3) — = real F2 (+ configFormat new)
3. V106 UPDATE needs its rationale; header comment is false (Std 3 + 4) — = real F3 (+ false comment new)
4. RunModeSpec "exhaustive" test proves nothing (Std 6 + Spec 6) — = real F5
5. AlertTriggerTypeSpec is a junk test (Std 7) — NEW; shipped in the merged MR
## Consider
- verdictReason String → enum (Std 5) — = real F4
- VARCHAR vs TEXT (Std 2): REQ-075 prescribes VARCHAR → standard-vs-spec, route to analyst — real N2 (resolved only in round 3)
- agent_run_checkpoints.agent_version unmapped (Spec 2) — NEW; plan omitted aruvii-tools → analyst; still unmapped at merge
- serialization spec uses its own mapper (Std 8) — NEW
- judge_samples test values vs spec shape (Spec 5) — NEW
## Noted
- AgentRunContext wire-shape compat tested one direction (Spec 4); AgentRuntimeConfig null→empty (Std 9)
## Dismissed
- NOT VALID + VALIDATE (Std 4, lock part): the header gives the reason (per-agent-scale tables) — consistent with migrations.md's own exception.

## Missed vs the real round 1
- F6 `final` on new parameters (java-standards in packet) — missed
- F7 boundaries not tried (boundaries-correct in packet) — missed
- N2 OptionalInt spec-vs-standard; N3 architecture group A (no architecture axis by design)

## Cost (same "subagent tokens" figure the fleet QA quoted)
new round 1: Standards 114,632 + Spec 131,278 = 245,910 · 21 tool calls · 130 s + 81 s, parallel
real round 1: 135k + 167k ≈ 302k (fleet QA self-report) + the lead's 15–25 tool calls
caveat: one run, one MR; today's references (no Review checks yet); metric is the harness figure, not billed tokens.
