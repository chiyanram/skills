# P1 Spec axis report (round 1, head 70b84c0b) — verbatim gist
1 [critical] AgentEntity.java:77 `currentVersion = 1` (untouched) → JPA inserts 1, DB DEFAULT 0 never applies; IT inserts via raw SQL and hides it. AC-6.
2 [warning] agent_run_checkpoints.agent_version has no entity field (RunCheckpointEntity, aruvii-tools) — plan step 2 partial.
3 [warning] AC-6 / S1-a proved on rows inserted after V106, not pre-existing; no EVALUATING/VERIFIED/CERTIFIED seed; no configFormat check; S1-a nullability only.
4 [nit] scope: new AgentRunContext record component changes Redis wire shape; compat tested one direction only.
5 [nit] judge_samples test uses "Scored"/"Abstained", no `passed` key vs spec.
6 [nit] RunModeSpec table "three resolutions" has two rows.
AC table: AC-6 cv=0 partial · DRAFT partial · no configFormat NONE · S1-a partial · S1-b NONE (relies on verify/smoke).
