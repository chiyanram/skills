# R16 · Spock best practices — verify the operator's skill against primary sources

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G9a

## Question

Check the installed spock-best-practices skill (operator-authored) and our Spock rules (rules/it-testing.md on master) against the official Spock 2.x docs (spockframework.org), Spock's own repo/examples, and high-star Spock users/guides. Per claim: confirmed · wrong · unsupported, with URL/path. List idioms we miss (data tables, @Unroll naming, Stub vs Mock vs Spy, interaction pitfalls, Spring integration @SpringBean, parallel execution).

## Resolution (2026-10-02)

`../research/20-spock-verification.md` (Spock docs @ tag spock-2.4 + a local probe spec, Spock 2.4-groovy-5.0). Our Spock
rule 1 (mock-argument closure checks only its LAST line) is WRONG since Spock 1.3 — every top-level line is an implicit
assertion (release_notes.adoc:946-993; probe failed on a false first line); only nested closures (.every{}) are unchecked →
SP1 stays parked, replaced by candidate K1. Rule 4's stated reason is wrong; rules 2, 3, 5b are process, not Spock; 5a
confirmed. Installed spock-best-practices skill: several outdated/wrong claims (Boot 4 + Spock, Stub returns empty values
not null, non-compiling examples, @Isolated is class-only). Repo gap: no SpockConfig.groovy → Spock specs run SEQUENTIALLY;
CLAUDE.md's "unit tests are class-parallel" applies to JUnit only. 20 candidate rules K1–K20, one by one.
