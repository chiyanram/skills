# R43 · Code + observability candidates vs the reference repos (2026-10-02)

For **#33** (G9b: approving the code + observability rules) under map **#9** (One rulebook: every rule decision cites what the reference repos do).
Checks `research/29-java-standards.md` §4 (Java G-A … G-J) and `research/30-ts-angular-standards.md` §5 (Angular G-A … G-F) against pstack, mattpocock, addy, humanlayer and Jeffallan. R25 and R26 cited none of these except addy (Angular only).

Path legend (all under `agent-platform/.claude/worktrees/crq-597-b837e3/.scratch/one-rulebook/refs/`):

| short | path |
|---|---|
| `ps/` | `cursor-plugins/pstack/` |
| `ctk/` | `cursor-plugins/cursor-team-kit/` (holds `/deslop`, which pstack's guide `ps/docs/guide/05-build-and-clean.md:59 @f713f14` points to) |
| `mp/` | `mattpocock-skills/` |
| `ad/` | `addyosmani-agent-skills/` |
| `jf/` | `Jeffallan-claude-skills/skills/` |
| `hl/` | `humanlayer-humanlayer/` |

Weight: ps and mp set the bar. ad is next. jf is generic and dated (it still says `*ngFor`), so it counts as corroboration only. humanlayer has almost no code-level rules. The one relevant line is `hl/hld/CLAUDE.md:54-55`.

---

## 0 · Contradictions (read first)

| # | candidate | reference says | cite | weight |
|---|---|---|---|---|
| **X1** | **CM3** "a kept comment states why" | Comment Sicko deletes every *why* comment about **our own** code and flags the symbol `MUST KILL` so a rename, extract or type can make the reason obvious instead. Only these survive: license headers, behaviour forced by an external dependency we cannot change, public-API doc comments, and issue or RFC links. A long justification "is a confession". | `ps/agents/comment-sicko.md:14-22,28`; `ps/skills/no-comments/SKILL.md:20-23`; `ps/skills/principle-fix-root-causes/SKILL.md:17` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] | **high**. Sides with CM3: `ps/skills/poteto-mode/SKILL.md:119 @f713f14` ("non-obvious *why* the code can't show") and `ad/skills/code-simplification/SKILL.md:145`. So pstack is two-tier: authors may write a why-comment, and the reviewer then deletes it unless it names an external constraint. |
| **X2** | G-H decided edge: **trace sampling 1.0** | Sample head-based at a low default rate. Keep 100% of errors through tail sampling. | `ad/references/observability-checklist.md:54`; `ad/skills/observability-and-instrumentation/SKILL.md:150` | med-high |
| **X3** | Angular **G-B5** "new components under 600 lines" (cites "addy :322") | addy's line 322 says **200**. pstack and addy's review skill use a **1000-line file** threshold. No reference says 600, so the citation is wrong. | `ad/skills/frontend-ui-engineering/SKILL.md:322`; `ps/skills/interrogate/references/code-quality-review.md:23,43`; `ad/skills/code-review-and-quality/SKILL.md:113` | high (citation error) |
| **X4** | **TY8** "wrap a primitive only when it carries an invariant" | Brand a semantic primitive whenever two values share a primitive type but mean different things (`UserId` vs `OrderId`), even with no invariant. Brand when values could be swapped, "not by reflex". | `ps/skills/principle-type-system-discipline/SKILL.md:17,27` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ps/skills/typescript-best-practices/references/patterns.md:84`; `mp/skills/engineering/code-review/SKILL.md:49` (Primitive Obsession) | high. TY8's test is wrong: the reason to wrap is that values can be swapped, not that they carry an invariant. |
| **X5** | G-C edge 8: best-effort catch-and-continue **logs at DEBUG** | `warn` = "degraded but handled (retry succeeded, fallback used)". DEBUG is off in production, so the degradation becomes invisible. | `ad/skills/observability-and-instrumentation/SKILL.md:75`; `ad/references/observability-checklist.md:30` | med |
| **X6** | Angular **G-A2** "a suppressed `any` needs a one-line reason" | A suppression of a rule that protects correctness or safety (`no-explicit-any` is one) is killed and the symbol is marked `MUST KILL`. A written reason does not save it. | `ps/agents/comment-sicko.md:24`; `ps/skills/no-comments/SKILL.md:20` | high |
| **X7** | **CM6** drop "comment length is a smell" | Length *is* the signal: "a long justification without a proven keep-list exception is a confession". | `ps/agents/comment-sicko.md:26-28`; `ps/skills/principle-fix-root-causes/SKILL.md:17` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] | med |
| **X8** | **LY2** "an interface only when something fakes it in a test …" | Mock only at system boundaries (external APIs, DB, time). Never mock your own modules. One adapter is a hypothetical seam; production plus test makes it real, but only for a boundary dependency. | `mp/skills/engineering/tdd/mocking.md:3-14`; `mp/skills/engineering/codebase-design/DEEPENING.md:29` | med. Narrow LY2's "fakes it in a test" to "a boundary dependency that a test fakes". |

Soft or low-weight disagreements (note them; they need no decision):

| candidate | ref | cite |
|---|---|---|
| G-H edge: Micrometer Tracing + Brave, not OTel | "Use OpenTelemetry" (the checklist adds "or equivalent") | `ad/skills/observability-and-instrumentation/SKILL.md:136`; `ad/references/observability-checklist.md:48` |
| G-C fix 9: errors are `ApiResponse`, not ProblemDetail | "return problem details, not stack traces" | `jf/spring-boot-engineer/SKILL.md:186 @be8783e` (low weight) |
| ER1: not-found is a sealed outcome | Interface example "returns a task or throws NotFoundError". "Don't mix" throw, null and `{error}`. | `ad/skills/api-and-interface-design/SKILL.md:50,86` |
| LG1: `action=<verb> key=value` inside the message | JSON log with a stable `event` field. Fields, not a message string. | `ad/skills/observability-and-instrumentation/SKILL.md:54-68`; `jf/monitoring-expert/SKILL.md:166,176 @be8783e` |
| SE4: path "resolved, normalised, then `startsWith(base)`" | Resolve **symlinks** first (`realpath`, which is `toRealPath` in Java; `normalize()` does not resolve them). Destructive operations also need a minimum depth and ownership evidence. | `ad/references/security-checklist.md:66,80-92`; `ad/skills/security-and-hardening/SKILL.md:117` |
| SE1: URL fetch allows only http/https | Allowlist the host too, resolve every DNS record and reject private or reserved IPs, and forbid redirects | `ad/skills/security-and-hardening/SKILL.md:111`; `ad/references/security-checklist.md:65` |
| Angular G-D1 control flow | "Use `trackBy` in `*ngFor`". This is stale (pre-v17), not a real disagreement. | `jf/angular-architect/SKILL.md:132 @be8783e` |
| Angular G-E3 `[style.color]` on the icon parent | "Inline styles or arbitrary pixel values" is a red flag. Use semantic tokens. | `ad/skills/frontend-ui-engineering/SKILL.md:172,323` |

---

## 1 · Per group: rows where a reference is not silent

### Java G-A · modern Java
| id | verdict | cite |
|---|---|---|
| JV3 streams compute, effects outside | agree (in spirit) | `mp/skills/engineering/codebase-design/SKILL.md:83-93` "return results, don't produce side effects" |
| JV9 braces via Checkstyle, not review | agree | `ps/skills/principle-encode-lessons-in-structure/SKILL.md:15-21` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (pick the strongest mechanism); `mp/skills/engineering/code-review/SKILL.md:41` "skip anything tooling already enforces" |
| edge: no JPMS, Gradle modules + AT | agree (analog) | `mp/skills/in-progress/setup-ts-deep-modules/SKILL.md:26-35`: tooling enforces the module boundary and forbids cycles |

silent: JV1, JV2, JV4, JV5, JV6, JV7, JV8

### Java G-B · types
| id | verdict | cite |
|---|---|---|
| TY1 no null decides a case | agree | `ps/skills/principle-type-system-discipline/SKILL.md:15` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (no optional-field bags); `ps/skills/typescript-best-practices/references/patterns.md:28-36` |
| TY2 sealed + switch without `default` | agree | `ps/skills/principle-type-system-discipline/SKILL.md:20` (the compiler checks exhaustiveness), `:29` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| TY3 compact constructor rejects forbidden combos | partial | `…type-system-discipline/SKILL.md:16` prefers *constructing* the type so the illegal value cannot exist over checking at runtime, and `:17` "validate once at creation". Use sealed variants first and keep the compact-constructor check for what is left. |
| TY6 closed set is an enum, not a string | agree | `…type-system-discipline/SKILL.md:15`; `mp/skills/engineering/code-review/SKILL.md:49` |
| TY8 wrap a primitive only for an invariant | **disagree** (X4) | `…type-system-discipline/SKILL.md:17,27`; `…typescript-best-practices/references/patterns.md:84` |

silent: TY4, TY5, TY7, edge 9 (no builders, no `Impl`)

### Java G-C · errors
| id | verdict | cite |
|---|---|---|
| ER1 foreseeable non-success is a sealed outcome | agree / soft disagree | agree: `ps/skills/principle-type-system-discipline/SKILL.md:9` ("define errors out of existence"), `:22` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (total functions). Soft disagree: `ad/skills/api-and-interface-design/SKILL.md:50,86` |
| ER2 one exception plus an `ErrorCode` catalogue | agree | `ad/skills/api-and-interface-design/SKILL.md:61-86` (one error shape, a machine-readable `code`) |
| ER3 chain the cause, never an empty catch | agree | `ps/skills/interrogate/references/rubric.md:10` ("silently swallowed?") |
| ER4 catch the narrowest type | agree | `ctk/skills/deslop/SKILL.md:13` (try/catch is abnormal on trusted paths) |
| ER6 validate at the boundary | agree; second clause partial | `ps/skills/principle-boundary-discipline/SKILL.md:9-24`; `ps/skills/interrogate/references/rubric.md:36`; `ad/skills/api-and-interface-design/SKILL.md:88-122`; `jf/spring-boot-engineer/SKILL.md:182 @be8783e`. Partial: `principle-boundary-discipline:24` and `principle-fix-root-causes:16` say no internal nil-guards at all, which is stricter than "`requireNonNull` for programming errors". |
| edge 8 best-effort catch logs DEBUG | **disagree** (X5) | `ad/skills/observability-and-instrumentation/SKILL.md:75` |
| fix 9 errors are ApiResponse, not ProblemDetail | soft disagree | `jf/spring-boot-engineer/SKILL.md:186 @be8783e` |

silent: ER5, ER7 (no Either)

### Java G-D · comments
| id | verdict | cite |
|---|---|---|
| CM1 no banners | agree | `ps/agents/comment-sicko.md:12` |
| CM2 no restating comments | agree | `ps/agents/comment-sicko.md:12`; `ctk/skills/deslop/SKILL.md:12`; `ad/skills/code-simplification/SKILL.md:144`; `ad/skills/code-review-and-quality/SKILL.md:46-47` |
| CM3 a kept comment states why | **contested** (X1) | for: `ps/skills/poteto-mode/SKILL.md:119 @f713f14`, `ad/skills/code-simplification/SKILL.md:145`. Against: `ps/agents/comment-sicko.md:17,22,28` |
| CM4 a factual claim is checked first | agree, and pstack goes further | `ps/agents/comment-sicko.md:26` (run `/how` and `/why` on the claim); `ps/skills/no-comments/SKILL.md:23` (encode a "do not remove" claim as a type, test or lint, then delete the comment) |
| CM5 Javadoc on the interface only when the contract is not obvious | agree | `ps/agents/comment-sicko.md:19` (keeps public-API contract docs); `mp/skills/engineering/codebase-design/SKILL.md:16` (the interface includes invariants and error modes) |
| CM6 drop "length is a smell" | **disagree** (X7) | `ps/agents/comment-sicko.md:26-28` |

silent: none

### Java G-E · services + layering
| id | verdict | cite |
|---|---|---|
| LY1 controllers bind and delegate | agree | `ps/skills/principle-boundary-discipline/SKILL.md:9,27` (thin shell, logic in pure functions); `ps/skills/interrogate/references/code-quality-review.md:33` (canonical layer) |
| LY2 interface only for a fake or a module boundary | agree; partial (X8) | agree: `mp/skills/engineering/codebase-design/SKILL.md:65`, `…/DEEPENING.md:29`, `ps/skills/principle-minimize-reader-load/SKILL.md:11 @f713f14`, `ps/skills/architect/references/design-red-flags.md:29-33`. Partial: `mp/skills/engineering/tdd/mocking.md:10-14` |
| LY3 two inseparable ops behind one method | agree | `ps/skills/interrogate/references/code-quality-review.md:35` (non-atomic updates); `ps/skills/architect/references/design-red-flags.md:13` ("callers coordinate several methods") |
| LY4 domain purity, gated by AT | agree | `ps/skills/principle-boundary-discipline/SKILL.md:23,27`; `ps/skills/architect/references/design-red-flags.md:21`; `ps/skills/principle-encode-lessons-in-structure/SKILL.md:19` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `mp/skills/in-progress/setup-ts-deep-modules/SKILL.md:26-35` |

silent: LY5 (fix the CM/SR "ungated" claim)

### Java G-F · concurrency
| id | verdict | cite |
|---|---|---|
| CC3 every remote call has a timeout that stops the work | agree | `ad/skills/api-and-interface-design/SKILL.md:213` (a timeout means *unknown*, so record intent before the call); `ad/skills/security-and-hardening/SKILL.md:35`; `ad/references/performance-checklist.md:116`; `hl/hld/CLAUDE.md:54-55` (pass cancellation, never store it) |
| CC4 bounded pool, bounded queue | agree (analog) | `ad/references/performance-checklist.md:181,232 @aeac41d` (unbounded means a leak); `ad/agents/code-reviewer.md:42` |
| CC5 shared mutable state has one owner | agree, and pstack goes further | `ps/skills/principle-separate-before-serializing-shared-state/SKILL.md:9-16` (remove the shared write target first; lock only if a real invariant needs it); `ps/skills/interrogate/references/rubric.md:15` |

silent: CC1, CC2, CC6

### Java G-G · logging
| id | verdict | cite |
|---|---|---|
| LG1 entry INFO `action=… key=value` with ids | partial (fields, not message) | `ad/references/observability-checklist.md:26-27`; `ad/skills/observability-and-instrumentation/SKILL.md:54-68`; `jf/monitoring-expert/SKILL.md:166-167 @be8783e` |
| LG3 WARN handled / ERROR investigate | agree | `ad/references/observability-checklist.md:30`; `ad/skills/observability-and-instrumentation/SKILL.md:72-77`. This also answers OQ4: a validation or auth failure is handled, so it is warn or info, not error. |
| LG4 no PII, prompts or secrets at INFO+ | agree | `ad/references/observability-checklist.md:31-32`; `ad/skills/security-and-hardening/SKILL.md:68`; `jf/monitoring-expert/SKILL.md:174 @be8783e`; `jf/secure-code-guardian/SKILL.md:62 @be8783e` |
| LG6 `{}` placeholders, no concatenation | agree, and the refs go further (structured fields) | `ad/skills/observability-and-instrumentation/SKILL.md:57-58,214`; `jf/monitoring-expert/SKILL.md:176 @be8783e` |
| LG7 long calls log their duration | agree | `ad/references/observability-checklist.md:33` (external calls: endpoint, status, latency, attempt count) |

silent: LG2, LG5, LG8

### Java G-H · metrics + tracing
| id | verdict | cite |
|---|---|---|
| MX1 tags are closed sets | agree | `ad/references/observability-checklist.md:41-43`; `ad/skills/observability-and-instrumentation/SKILL.md:125-130` |
| MX2 Timer / LongTaskTimer / Counter / Gauge | agree, and the refs go further | `ad/references/observability-checklist.md:40` and `…/SKILL.md:132` (latency as a histogram with p95/p99, "never an average"); `jf/monitoring-expert/SKILL.md:170 @be8783e` |
| MX4 a test asserts the meter name and tags | agree (in spirit) | `ad/references/observability-checklist.md:78`; `ad/skills/observability-and-instrumentation/SKILL.md:195` |
| TR1 traceId carried on the async message | agree | `ad/references/observability-checklist.md:28,51`; `ad/skills/observability-and-instrumentation/SKILL.md:150` |
| TR3 no PII in spans; spans end in `finally` | agree | `ad/references/observability-checklist.md:52-53` |
| edge: Brave, not OTel | soft disagree | `ad/skills/observability-and-instrumentation/SKILL.md:136` |
| edge: sampling 1.0 | **disagree** (X2) | `ad/references/observability-checklist.md:54` |

silent: MX3, TR2, edge "no Prometheus until #160"

### Java G-I · security
| id | verdict | cite |
|---|---|---|
| SE1 http/https only via the checked fetch | agree but too weak | `ad/skills/security-and-hardening/SKILL.md:111`; `ad/references/security-checklist.md:65` |
| SE2 decryption failure stops the call | agree (analog) | `ad/skills/security-and-hardening/SKILL.md:117` ("never fall back to a broader default") |
| SE3 bind SQL params; identifiers from an allowlist | agree | `ad/references/security-checklist.md:57,62`; `ad/skills/security-and-hardening/SKILL.md:47,81`; `jf/secure-code-guardian/SKILL.md:52 @be8783e` |
| SE4 path normalised plus `startsWith` | agree but too weak | `ad/references/security-checklist.md:66,80-92` (symlinks first) |
| SE5 untrusted JSON binds to a fixed DTO | agree | `ad/skills/security-and-hardening/SKILL.md:104`; `ad/skills/api-and-interface-design/SKILL.md:118` |
| SE6 `innerHTML` / `bypassSecurityTrust*` only for code-controlled content | agree | `ad/skills/security-and-hardening/SKILL.md:71,82` |

silent: none

### Java G-J · messaging
| id | verdict | cite |
|---|---|---|
| MS3 no second consumer until #162 settles ack mode and dedup | agree (in spirit) | `ps/skills/principle-make-operations-idempotent/SKILL.md:9-24` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ad/skills/api-and-interface-design/SKILL.md:156-215` [drift 2026-10-17: cited lines rewritten at aeac41d, see research/64d] (the initiator mints the key; key TTL must cover the longest retry or DLQ chain) |

silent: MS1, MS2, MS4, MS5

### Angular G-A · TS strictness
| id | verdict | cite |
|---|---|---|
| A1 keep strict flags | agree | `jf/angular-architect/SKILL.md:130 @be8783e`; `jf/typescript-pro/SKILL.md:117,130 @be8783e` |
| A2 no `any`; use `unknown` and narrow | agree; "suppress with reason" **disagree** (X6) | `ps/skills/typescript-best-practices/SKILL.md:18`, `…/references/patterns.md:110-128`; `ctk/skills/deslop/SKILL.md:14`; `ad/skills/code-review-and-quality/SKILL.md:62`; `jf/typescript-pro/SKILL.md:127 @be8783e`. Against the reason clause: `ps/agents/comment-sicko.md:24` |
| A3 no `!` or `as` | agree | `ps/skills/typescript-best-practices/SKILL.md:17,20`; `…/references/patterns.md:94-106,151-177` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ps/skills/principle-type-system-discipline/SKILL.md:19` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `jf/typescript-pro/SKILL.md:131 @be8783e` |
| A4 literal union, not `enum` | agree | `jf/typescript-pro/SKILL.md:134 @be8783e` |

silent: none

### Angular G-B · components & signals
| id | verdict | cite |
|---|---|---|
| B1 standalone only | agree | `jf/angular-architect/SKILL.md:127,137 @be8783e` |
| B2 OnPush | agree | `jf/angular-architect/SKILL.md:129 @be8783e` |
| B3 `computed()` for derived state; `effect()` never copies state | agree | `ps/skills/principle-minimize-reader-load/SKILL.md:14 @f713f14` ("derive instead of sync"); `jf/angular-architect/SKILL.md:128 @be8783e` |
| B5 component renders, logic in a service; < 600 lines | logic split agrees; **threshold disagrees** (X3) | agree: `ps/skills/principle-boundary-discipline/SKILL.md:27`. Threshold: `ad/skills/frontend-ui-engineering/SKILL.md:322` (200), `ps/skills/interrogate/references/code-quality-review.md:23` (1k) |

silent: B4

### Angular G-C · DI, services, async
| id | verdict | cite |
|---|---|---|
| C2 HTTP in a root service, unwrapped | agree | `mp/skills/engineering/tdd/mocking.md:37-53` (one SDK-style function per endpoint); `ps/skills/principle-boundary-discipline/SKILL.md:23` (don't leak wire types) |
| C3 `takeUntilDestroyed` | agree | `jf/angular-architect/SKILL.md:138 @be8783e`; `ad/references/performance-checklist.md:238 @aeac41d` |
| C4 never swallow an error | agree; the "one-line reason" form is contested (X1) | `ad/skills/frontend-ui-engineering/SKILL.md:324`; `ps/skills/interrogate/references/rubric.md:10`; `jf/angular-architect/SKILL.md:131,139 @be8783e` |

silent: C1

### Angular G-D · templates & a11y
| id | verdict | cite |
|---|---|---|
| D1 `@if/@for` | stale disagree | `jf/angular-architect/SKILL.md:132 @be8783e` |
| D2 clickable means `<button>` | agree | `ad/references/accessibility-checklist.md:57-67`; `ad/skills/frontend-ui-engineering/SKILL.md:180-196` |
| D3 icon-only button gets `aria-label` | agree | `ad/references/accessibility-checklist.md:28`; `ad/skills/frontend-ui-engineering/SKILL.md:198-202`; `jf/angular-architect/SKILL.md:140 @be8783e` |

silent: none

### Angular G-E · icons & select
| id | verdict | cite |
|---|---|---|
| E3 `[style.color]` on the parent | soft tension | `ad/skills/frontend-ui-engineering/SKILL.md:172,323` |

silent: E1, E2

### Angular G-F · lint config
| id | verdict | cite |
|---|---|---|
| F1 extend the recommended and a11y configs | agree | `ps/skills/principle-encode-lessons-in-structure/SKILL.md:19` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] |
| F3 `features/X` never imports `features/Y` | agree | `mp/skills/in-progress/setup-ts-deep-modules/SKILL.md:26-35`; `ad/agents/code-reviewer.md:29` |
| F4 a new rule lands at error, or warn with a count | agree (partial) | `ps/skills/principle-encode-lessons-in-structure/SKILL.md:19` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] (strongest mechanism = fails CI) |

silent: F2

---

## 2 · Rules the references have that our candidates lack

"Agnostic" means the rule applies to Java and TS alike.

### Code shape / deslop / code judo
| # | rule | cite | agnostic |
|---|---|---|---|
| M1 | Look for a "code judo" move: a restructure that deletes branches, modes or layers rather than moving them around. Treat kept incidental complexity as a presumptive blocker. | `ps/skills/interrogate/references/code-quality-review.md:21,27,43` | yes |
| M2 | A change that pushes a file from under 1k lines to over 1k is a presumptive blocker: decompose first. | `…/code-quality-review.md:23`; `ad/skills/code-review-and-quality/SKILL.md:113` | yes |
| M3 | No ad-hoc branching in an existing flow. Model the domain with a state machine, table or registry, or a sum type, not an if-chain one branch longer or a second boolean to keep in sync. | `…/code-quality-review.md:25`; `ps/skills/principle-model-the-domain/SKILL.md:9-26` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] | yes |
| M4 | Remove pass-through methods, single-caller wrappers and adapters with only one implementation. Apply the deletion test. | `ps/skills/architect/references/design-red-flags.md:29-33`; `ps/skills/principle-minimize-reader-load/SKILL.md:11-12 @f713f14`; `mp/skills/engineering/codebase-design/SKILL.md:63`; `mp/skills/engineering/code-review/SKILL.md:55` | yes |
| M5 | Migrate callers and delete the old API in the same change, with no dual paths when there are no external consumers. | `ps/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md:11-15` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ps/skills/interrogate/references/rubric.md:41,65` | yes |
| M6 | No speculative generality: no parameters, config or hooks for cases that don't exist. Three duplicated lines beat a premature abstraction. | `…/rubric.md:61-68` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `mp/skills/engineering/code-review/SKILL.md:53`; `ps/skills/principle-subtract-before-you-add/SKILL.md:15-16 @f713f14` | yes |
| M7 | Remove dead code, vestigial parameters, commented-out blocks and `// removed` shims. | `…/rubric.md:63`; `ad/skills/code-review-and-quality/SKILL.md:47,233-241 @aeac41d`; `ad/skills/code-simplification/SKILL.md:152` | yes |
| M8 | No symptom guards: no nil-check to silence a crash and no defensive try/catch on trusted paths. Fix the cause and grep for the same pattern elsewhere. | `ps/skills/principle-fix-root-causes/SKILL.md:16-18` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ctk/skills/deslop/SKILL.md:13`; `ps/skills/principle-boundary-discipline/SKILL.md:24` | yes |
| M9 | A suppression (`eslint-disable`, `@ts-expect-error`, Java `@SuppressWarnings`) of a correctness or safety rule is forbidden. Fix the type. | `ps/agents/comment-sicko.md:24` | yes |
| M10 | A constraint comment ("do not remove", "talk to X first") is encoded as a type, test or lint, and then the comment is deleted. | `ps/skills/no-comments/SKILL.md:23`; `ps/skills/principle-encode-lessons-in-structure/SKILL.md:13-21` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ps/skills/interrogate/references/rubric.md:30` | yes |
| M11 | Nesting of 3 or more levels becomes guard clauses or early returns. No nested ternaries. | `ad/skills/code-simplification/SKILL.md:131-133`; `ctk/skills/deslop/SKILL.md:15` | yes |
| M12 | Flat call hierarchy: if an answer needs tracing through more than 3 layers, flatten. Make each decision once, in one source of truth. | `ps/skills/principle-laziness-protocol/SKILL.md:12-13,16` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] | yes |
| M13 | Use the Fowler smell baseline as judgement calls (Feature Envy, Data Clumps, Repeated Switches, Shotgun Surgery, Middle Man, Refused Bequest). A documented repo standard overrides it. | `mp/skills/engineering/code-review/SKILL.md:38-56` | yes |

### Naming
| # | rule | cite | agnostic |
|---|---|---|---|
| M14 | No generic names (`data`, `result`, `temp`, `item`) and no abbreviations beyond `id`, `url` and `api`. A name that hides a mutation is misleading. If no honest name comes, the design is murky. | `ad/skills/code-simplification/SKILL.md:141-143`; `ad/skills/code-review-and-quality/SKILL.md:40`; `mp/skills/engineering/code-review/SKILL.md:45` | yes. **We have no naming rule at all.** |

### Types (beyond TY*)
| # | rule | cite | agnostic |
|---|---|---|---|
| M15 | Brand an id whenever two same-primitive params could be swapped (fixes X4). | `ps/skills/principle-type-system-discipline/SKILL.md:17,27` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] | yes |
| M16 | Derive types from the authoritative schema (OpenAPI to TS DTOs) instead of hand-rolling a parallel type. | `…type-system-discipline/SKILL.md:21`; `ps/skills/typescript-best-practices/SKILL.md:19,26`, `…/references/patterns.md:278-299 @f713f14` | yes (big for Angular: DTOs are hand-written today) |
| M17 | TS: exhaustive `switch` with `const _exhaustive: never` in the default arm. | `ps/skills/typescript-best-practices/SKILL.md:23`, `…/references/patterns.md:219-255 @f713f14` | TS (Java's TY2 covers its side) |
| M18 | TS: narrowing hierarchy (discriminant, then `in`, then `typeof`, then guard, then `as`). Type guards must verify their claim and be named `isX`. `satisfies` over `as`. | `ps/skills/typescript-best-practices/SKILL.md:21-22,24` | TS |
| M19 | TS: object args, not positional (except hot paths). | `ps/skills/typescript-best-practices/SKILL.md:27` | mostly |
| M20 | Strengthen a type only where partiality appears (a `!`, a cast, a "should never happen" throw). Otherwise keep the plain type. | `…type-system-discipline/SKILL.md:22,31`; `…/references/patterns.md:86-108` | yes |

### Errors / resilience
| # | rule | cite | agnostic |
|---|---|---|---|
| M21 | Error bodies are generic: no exception message, stack or SQL. Internals go to server logs only. | `ad/references/security-checklist.md:202-216`; `ad/skills/security-and-hardening/SKILL.md:73,98`; `jf/secure-code-guardian/SKILL.md:62 @be8783e` | yes |
| M22 | Every state-mutating op answers "what if this runs twice, or the last run crashed halfway?". Add a reconciliation step if the answer depends on what was left behind. | `ps/skills/principle-make-operations-idempotent/SKILL.md:9-24` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a]; `ps/skills/interrogate/references/rubric.md:14` [drift 2026-10-17: cited lines rewritten at f713f14, see research/64a] | yes (Redis Streams consumers) |
| M23 | A remote call has three outcomes (success, failure, unknown). Record intent before the call. The idempotency key comes from the initiator, never from the retrying layer. | `ad/skills/api-and-interface-design/SKILL.md:156-215` [drift 2026-10-17: cited lines rewritten at aeac41d, see research/64d] | yes |
| M24 | Independent work serialized for no reason, or related updates that can half-apply, are design smells. | `ps/skills/interrogate/references/code-quality-review.md:35` | yes |
| M25 | Before locking shared state, remove the shared write target: give each actor its own key or file (sharpens CC5). | `ps/skills/principle-separate-before-serializing-shared-state/SKILL.md:15-16` | yes |

### Observability
| # | rule | cite | agnostic |
|---|---|---|---|
| M26 | Start from 2–4 on-call questions. Every signal maps to one: metrics say *that*, traces say *where*, logs say *why*. | `ad/references/observability-checklist.md:18-22`; `ad/skills/observability-and-instrumentation/SKILL.md:27-50` | yes |
| M27 | A log stream with several entry points (scheduler, replay, API) carries an `entryPoint` field next to the correlation id, propagated the same way. | `ad/references/observability-checklist.md:29`; `ad/skills/observability-and-instrumentation/SKILL.md:91-104` | yes |
| M28 | Allowlist log fields: no whole request or response bodies and no auth headers. | `ad/references/observability-checklist.md:32` | yes |
| M29 | RED (rate, errors, duration) for every endpoint and external dependency. USE (utilization, saturation, errors) for every pool and queue. Track queue depth and processing duration per worker. | `ad/references/observability-checklist.md:38-39,44` | yes |
| M30 | Latency is a histogram with queryable percentiles, never an average. Status is a tag by class (`5xx`). | `ad/references/observability-checklist.md:40,43` | yes (Micrometer: `publishPercentileHistogram`) |
| M31 | Verify the telemetry: force an error and find it by correlation id. Diagnose one induced failure from telemetry alone. | `ad/references/observability-checklist.md:73-80` | yes |
| M32 | Tag temporary debug logs (`[DEBUG-a4f2]`) and grep them out before merge. | `mp/skills/engineering/diagnosing-bugs/SKILL.md:110,136` | yes |
| M33 | TS: no `console.log` in shipped code. Use a structured logger that carries an id. | `ps/skills/typescript-best-practices/SKILL.md:29` | TS (Angular) |

### Security / performance
| # | rule | cite | agnostic |
|---|---|---|---|
| M34 | Model output and tool arguments are untrusted input: never into SQL, shell, `innerHTML` or a file path. Validate against a schema. Enforce permissions in code, not in the prompt. | `ad/skills/security-and-hardening/SKILL.md:158-160`; `ad/references/security-checklist.md:194-200,239-248` | yes. **The most relevant gap for an agent platform.** |
| M35 | Third-party API responses are untrusted. Validate their shape before use. | `ad/skills/api-and-interface-design/SKILL.md:118` | yes |
| M36 | No N+1 queries. Every list endpoint is paginated or has a `LIMIT`. | `ad/references/performance-checklist.md:90-92,225-226 @aeac41d`; `ad/agents/code-reviewer.md:41-45` | yes |
| M37 | A cache has an eviction policy and a memory ceiling. One connection pool per process, with a connection timeout that fails fast. | `ad/references/performance-checklist.md:114-117,181,230-232 @aeac41d` | yes |

### Testing seams (may belong to another group)
| # | rule | cite | agnostic |
|---|---|---|---|
| M38 | Mock only at system boundaries, never your own modules. Test through the interface. Delete shallow-module tests once interface tests exist. | `mp/skills/engineering/tdd/mocking.md:3-14`; `mp/skills/engineering/codebase-design/DEEPENING.md:32-37` | yes |
