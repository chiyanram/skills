# R18 · Playwright / E2E and frontend (Angular + Jest) testing rules from high-star sources

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Blocks: G9a

## Question

Find high-star TypeScript/Angular/Playwright sources with written testing rules (e.g. microsoft/playwright docs + best practices, Angular testing guide, testing-library guiding principles, addy agent-skills e2e/frontend skills, ECC rules, cursor rules collections, awesome-cursorrules, Kent C. Dodds testing trophy) — verify star counts with gh api. Compare with ours: smoke-spec skill (K-* rubric), rules/smoke.md, rules/angular-ui.md, aruvii-ui jest setup, playwright configs (core + full), check-antipatterns.sh. Candidate rules for testing/references/{smoke-specs.md (→ e2e), frontend-unit.md}, each with source path:line.

## Resolution (2026-10-02)

`../research/22-playwright-frontend-testing.md`. Playwright docs back our core K-rules (isolation, condition waits, real
landmarks, serial only with reason). Missing: web-first matchers, `.first()` dodging strictness (105 uses), storageState
login reuse (0 uses — verified), no-floating-promises lint on playwright/, raised timeouts hiding flakes (29). Verified false
facts: the smoke anti-pattern scanner runs nowhere (no Makefile target calls smoke:lint / check-antipatterns); CORE_SPECS no
longer exists — core = `@core` tag (playwright.core.config.ts:15-20). Two Playwright rubrics cover the same files
(smoke-spec K-* + docs/guides/playwright-rubric.md). Frontend unit: Jest 30 zoneless, 81 specs, one CLAUDE.md line of rules;
specs call component methods 197× vs read the DOM 131×. Candidates E1–E11 (e2e), F1–F10 (frontend unit), 8 open questions —
put to the operator one by one. Rejected sources: awesome-cursorrules (weak); ECC contradicts Playwright docs
(networkidle, data-cy, fakeAsync).
