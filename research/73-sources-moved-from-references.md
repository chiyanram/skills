# 73 · Sources moved out of the reference files (agent-factory#59)

On 2026-11-04 the operator decided that a rule file holds only what an agent needs to act; provenance lives in the
ledger (`19-approved-rules.md`) and the research files. The strip removed citations from every reference. Most of them
were already in each rule's ledger row. The ones below were not, so they are kept here, as they stood in the
references on main at `52ae5e8`, with each file's short source names written out in full. A ledger row whose source cell ends "see research/73" points here.

## Planning and meta (spec-review, diagrams, program-design, writing-docs, acceptance-criteria)

- spec-review: SR1 circleci eng-practices §Avoid Ad-Hoc Comments; SR2 humanlayer create_plan.md:69,79 @77c7fe99, pstack skills/why/references/sources/notion.md:42, mattpocock to-spec/SKILL.md:55; SR4 create_plan:341 @77c7fe99, github/spec-kit templates/commands/specify.md:164, firstmate captain-hold-lifecycle/SKILL.md:19, addy spec-driven-development:146; SR6 to-spec:35,:67, jvm-skills .claude/skills/spec/SKILL.md:36, spec-kit:165,:170, spec-driven:144, addy interview-me:111, create_plan:331 @77c7fe99. Pref line: SR1, SR3.
- diagrams: DG2 humanlayer-skills plugins/show-me/skills/show-me/SKILL.md:47,:59,:85 (Good pair from :85), mattpocock improve-codebase-architecture/HTML-REPORT.md:63; DG1 GitHub Docs "Creating diagrams" §About creating diagrams, mattpocock docs/engineering/pr.md:47, pstack skills/how/references/explainer-prompt.md:40; DG6 show-me:126; DG4 show-me:126 + pstack skills/teach/SKILL.md:17; DG5 HTML-REPORT.md:55 + show-me:126. Pref line: DG1, DG2, DG3, DG6.
- program-design: HumanLayer advanced-context-engineering-for-coding-agents/wsff.md:491-501 (PD1; Good pair :493-501), :507-515 (PD2; Good pair), :517 (PD3), :542-551 (PD4); HumanLayer .claude/commands/create_plan.md:226-234,:325 @77c7fe99 (PD5; Good pair :226-234); pstack skills/architect/SKILL.md:9,:83 (PD3; Good pair), :57 (PD7); mattpocock to-tickets/SKILL.md:31 (PD4), :40 (PD4 edge), to-spec:55 (PD6); addy planning-and-task-breakdown/SKILL.md:93-95 (PD2), :61-77 (PD4; Bad :61-67, Good :69-75), :86-89 (PD5); addy spec-driven-development:214 (PD7), :96 (PD6 counter-source note). Pref line: PD1, PD2, PD3, PD6.
- writing-docs: WD2 kunchenguid-firstmate AGENTS.md:374, mattpocock skills/productivity/writing-for-agents/SKILL.md:79; WD4 mattpocock .agents/writing-docs.md:56, addy documentation-and-adrs/SKILL.md:134; WD7 writing-for-agents:78,:79 (edge), firstmate AGENTS.md:55, openclaw docs/AGENTS.md:38, jabrena-plinth skills/200-agents-md/references/200-agents-md.md:59; WD5 addy spec-driven-development:212-214. Pref line: WD1, WD4, WD5.
- acceptance-criteria: GA1 addyosmani spec-driven-development:143, github/spec-kit templates/spec-template.md §User Scenarios & Testing, humanlayer create_plan.md:225 @77c7fe99; GA2/CV1 spec-kit §Functional Requirements, OMG issue SYSML16-204 (SysML 1.6 "The unique Id of the requirement"), cucumber.io/docs/gherkin/reference §Comments; GA3 cucumber-ref §Tags, jabrena plinth skills/058-design-bdd/references/058-design-bdd.md:266 (counter-source; Bad pair :266-270); GA4 cucumber-ref §Background, §Scenario Outline, plinth-bdd:149; GA5 cucumber-ref §Steps, plinth-bdd:32, spec-kit §Edge Cases, plinth 131-java-testing-unit-testing.md:25, plinth-bdd:93-99 (edge); GA6 Dan North "Introducing BDD" §agiledox, cucumber.io/docs/bdd/better-gherkin §Declarative; AC7 addyosmani deprecation-and-migration/SKILL.md:179; AC9 mattpocock to-spec:13, North §BDD for analysis; AC10 addy-sdd:214; GA4 pair adapted from plinth-bdd:169-176 (Bad), :154-164 (Good); GA5 pair from plinth-bdd:104-107 (Bad), :93-99 (Good). Pref line: GA2, GA3, GA6, CV1, AC7, AC8, AC9, AC10.

## Migrations and observability

- MIGRATIONS: MG5 cited r47 :863-868 (PG SET "outside of a transaction block ... no effect"; PG explicit locking) — ledger MG5 row names only r47 :160-163 (PG ALTER TABLE, client config; squawk; strong_migrations; GitLab). Review check cited r47 :863.
- OBS levels.md: no ledger row names its sources (it has no rule ids; ledger rows for levels are FL14/FL25/OQ4, none pointing at r47). Its table cited r47 :456-465, :467 (OpenTelemetry exceptions in logs, logs data model, recording errors, HTTP spans; Log4j Level; OWASP Logging and Logging Vocabulary).
- OBS logging: LG6 cited r47 :869-875 (SLF4J manual fluent API "pass arguments with a Supplier"; SLF4J LoggingEventBuilder) — ledger LG6 names r47 :517-519 only. LG3 edge cited r47 :873-875 (SLF4J LoggingEventBuilder setCause) — ledger LG3 names :494-495 only. LG8 edge cited r47 :527 (SLF4J static/instance "left to the user") — ledger LG8 names :524-525. LG4 cited r47 :504 (OpenTelemetry HTTP url.full scrubbed) — ledger LG4 :502-504 ok.
- OBS metrics: MX1 edge cited r47 :634 (Micrometer Observation "High cardinality key values are not included in meters") — ledger MX1 names :548-550 only (the :634 line sits under TR3).
- OBS tracing: TRN1/TR3 cited r47 :634 (OpenTelemetry Trace API "account_id=42 would make a nice Span attribute"; Micrometer Observation) — ledger TRN1 names :639-641, TR3 :630-632, neither :634. TR5 edge cited r47 :664 (OTel SDK sampling as a cost choice) — ledger TR5 names :661-662. Bridge note cited r47 :666-672 (TR4/TR4a notes; ledger TR4 is a project decision row). TR1 thread hand-off cited :614 (Micrometer Tracing "continue a span in a new thread") — ledger TR1 :611-614 ok.

## Testing

- U1: mattpocock `tdd/mocking.md` :7 (unit-tests.md).
- U2: spock-best-practices `SKILL.md` :52, :55, :56, :79, :80 (unit-tests.md); :52 and :55 source U2's reason.
- U3: addyosmani `test-driven-development/SKILL.md` :240-243 ("ladder") (unit-tests.md).
- S3: agent-factory `research/31:19`, the source of S3's reason (strategy.md).
- M1: agent-factory `research/31:23`, the source of M1's reason (mutation.md).
- S4: agent-factory ADR-0007, cited in the S4 decided edge (mutation.md).
- GT6: agent-factory `research/31:22`, the source of GT6's reason (scenario-to-tests.md).
- TM4: agent-factory `research/31:20`, the source of TM4's reason (integration-tests.md).
- K20: agent-factory `research/31:21`, the source of K20's reason (examples/spock.md).
- B1: plinth `130-java-testing-strategies-correct.md` :42, :67, :119, :149, :176, :211 (boundaries.md, CORRECT table).
- C1: plinth `130-java-testing-strategies-right-bicep.md` :79, :102-103, :134, :167-168, :193 (coverage-design.md,
  RIGHT-BICEP table).
- V2, V3, V5: openclaw test-audit :31-33, :33, :71-73, :105-106, :108-109 (value-bar.md).
- K3: Spock `interaction_based_testing.adoc` :788-797 (spock.md).
- U3: mattpocock `tdd/mocking.md` :10-14 (unit-tests.md).
- SP10, SP11: agent-factory-era neutral pair sources `68b` :602, :636 (integration-tests.md).

## Migrations, line pointers

- MG36: r47 :143 (postgres-design.md).

## Code and deslop

Every line of the code references and `deslop/SKILL.md` on main at `52ae5e8` that carried a source, a citation, a
credit, a sources paragraph or an operator-preference mark, with its line number in that file. The T17 code re-check
(agent-factory research/48) then reworded or replaced some of these rules; the ledger rows hold the current sources,
and this section keeps what the old text cited.

### code/references/angular-ui.md

- :45 | a value whose type the code cannot know | `unknown`, then narrow it (NGA2) | `any` switches off the check on every property access · angular.dev best practices "use `unknown` when type is uncertain"; Google TypeScript Style Guide §Using unknown over any; pstack typescript-best-practices "External data is `unknown`" |
- :46 | an untyped library that forces `any` | a `no-explicit-any` suppression with a one-line reason naming the library (NGA2) | Google TypeScript Style Guide §Suppressing any lint warnings "document why it is legitimate" |
- :47 | a value that must match a type | `satisfies`, not `as` (NGA6) | `as` hides a crash the compiler could catch (NGA3) · TypeScript 4.9 release notes §satisfies; pstack typescript-best-practices "`satisfies` over `as`"; Jeffallan typescript-pro |
- :48 | a `switch` over a union | `const _exhaustive: never = x` in the default arm (NGA5) | a new variant fails to compile · TypeScript handbook §Exhaustiveness checking; pstack typescript-best-practices; Jeffallan typescript-pro |
- :49 | a frontend type for a backend DTO | a type derived from the OpenAPI schema (NGA7) | a hand-written copy drifts · operator preference; pstack `references/patterns.md` "derive from the generated types instead of duplicating" |
- :52 | a dependency in a component or service | `inject()` in a field initialiser (NGC1) | operator preference · angular.dev style guide §Prefer the inject function over constructor parameter injection |
- :55 | a list in a template | `@for` with `track` (NGD1) | `track` maps items to DOM nodes and speeds rendering · angular.dev control flow §Why is track in @for blocks important; Jeffallan angular-architect `references/components.md` |
- :59 Operator preference, 2026-10-31 (SRC2), in whole or in part: NGA7 and NGC1.
- :65 **Bad** (neutral)
- :81 **Good** (neutral)
- :102 reason that names the untyped library (NGA2; Google TypeScript Style Guide §Suppressing any lint warnings).

### code/references/comments.md

- :29 | a banner or divider | delete it (CM1) | banners are on the kill list (sicko :12) |
- :30 | narration of what the code, a dependency or a config value does | delete it (CM2) | narration is on the kill list (sicko :12); a comment that explains "what" goes (simplification :144) |
- :31 | a legal or license header | keep it (CM3) | sicko :16 |
- :32 | behaviour forced by an external dependency, platform, vendor or protocol | keep it (CM3) | sicko :17 |
- :33 | a surprise in our own code | delete it; rename, extract or type the symbol until the behaviour is obvious (CM3) | sicko :17 |
- :34 | a doc comment that defines a public API contract | keep it when the signature does not show the contract (CM3, CM5) | sicko :19; an interface is also its invariants, ordering constraints and error modes (codebase-design :16) |
- :35 | an issue or RFC link for a constraint the code cannot express | keep it (CM3) | sicko :20 |
- :36 | a constraint note: `do not remove`, `do not change wording`, `talk to X before changing` | check the claim; encode it as a type, test or lint, then delete it (CM4) | sicko :26; no-comments :23 |
- :37 | a lint or compiler suppression | fix the type when the rule protects correctness or safety; keep it when the rule is style-only (CM7) | sicko :18, :24 |
- :39 `sicko` is pstack `agents/comment-sicko.md`, `no-comments` is pstack `skills/no-comments/SKILL.md`, `simplification`
- :40 is addy `skills/code-simplification/SKILL.md` and `codebase-design` is mattpocock
- :41 `skills/engineering/codebase-design/SKILL.md`; `:N` is the line.
- :43 Operator preference, 2026-10-31 (SRC2), in whole or in part: CM4 and CM5.
- :49 **Bad** (neutral)
- :62 **Good** (neutral)
- :75 **Bad** (neutral)
- :85 **Good** (neutral)
- :102 **Bad** (neutral)
- :111 **Good** (neutral)
- :132 - **Skip when** the comment fits a keep clause of CM3 that is proven true today on a live path (sicko :26). — **Do not
- :133 skip when** you are not sure a keep clause applies: the comment goes (sicko :22). — **Confidence** high
- :135 code, even though addy keeps such comments (simplification :145): delete it and ask for a reshape (operator
- :136 preference, 2026-10-31). — **Confidence** high
- :137 - **Skip when** a member's contract is obvious from its signature: write no Javadoc (Google Java Style §7.3.1 makes it
- :138 optional for a simple, obvious member, and §7.3.2 for an override). — **Do not skip when** the interface has an
- :139 invariant, ordering constraint or error mode the signature cannot show (codebase-design :16). — **Confidence** high

### code/references/concurrency.md

- :40 | many blocking I/O calls to run at once | `Executors.newVirtualThreadPerTaskExecutor()`, one virtual thread per task, never a pool of them (CC1) | avoid pooling virtual threads (pl125 :31) · there is never a need to pool them (JEP 444 §Do not pool virtual threads). The `synchronized` and pinning clauses are operator preference, read in JEP 491 (§Future Work, §Diagnosing remaining cases of pinning) |
- :41 | blocking work to run async | `supplyAsync(task, executor)` with a dedicated executor (CC2) | operator preference; avoid blocking I/O in the common pool; use a dedicated executor (pl125 :37) · the two-argument form (pl142 :854) |
- :42 | CPU-bound, short, side-effect-free work | ForkJoin or a parallel stream, outside request- or queue-serving code (CC2; JV2, `java.md`) | the common pool is reserved for that work (pl125 :37) |
- :43 | a client for a remote service | a connect and a read timeout on the client itself (CC3) | always bound remote calls with timeouts (pl125 :40) · cancel ongoing work on timeout (pl126 :34) · set a timeout on any remote call (AWS timeouts) |
- :44 | a remote call with a side effect | an intent record before the call, and three outcomes: success, failure, unknown (CC9) | operator preference; a timeout tells you nothing about whether the effect applied (addy api :213) |
- :45 | an idempotency key | one key per intent, minted by the initiator and reused on every retry (CC9) | never from the layer doing the retrying (addy api :163, :171) · the client generates the idempotency key (Stripe idempotent requests) |
- :46 | a failed remote call to retry | the timeout first, then bounded attempts with jitter, for transient failures of idempotent calls only (CC8) | bounded attempts and jitter (pl123cc :42-43) · retry only transient failures (pl123cc :95) · limit retries, add jitter, retry side effects only when idempotent (AWS timeouts) |
- :47 | a dependency that can exhaust shared threads, connections or queue capacity | a bulkhead: a bounded pool, a bounded queue and a rejection policy (CC4) | bounded queues and rejection policies (pl125 :35) · an unbounded work queue can grow without limit (JDK `ThreadPoolExecutor`) · a bounded queue and a fixed thread pool (Resilience4j bulkhead) |
- :48 | two actors that write the same state | each actor its own key or file, merged where it is read (CC5) | operator preference; eliminate the shared write target first (ps separate :15) |
- :49 | two locks held at once | one global acquisition order (CC5) | operator preference; establish global lock ordering (pl125 :36) |
- :50 | a `CompletableFuture` pipeline | `thenApply`/`thenCompose`/`allOf`; block only at the outer boundary (CC6) | operator preference; avoid premature `join()`/`get()` mid-flow (pl142 :839) |
- :51 | context that async tasks read | a `ScopedValue` (CC7) | `ScopedValue` over `ThreadLocal` across tasks (pl125 :33, :39) · scoped values may be a better alternative (JEP 444 §Thread-local variables; JEP 487 §Expensive inheritance) |
- :52 | a cache | an eviction policy and a memory ceiling (CC10) | eviction policy and memory ceiling set (addy perf :181) · size-based eviction with `maximumSize` (Caffeine Eviction §Size-based) |
- :54 Sources, all read at a pinned commit or at the URL named; `:N` is a line:
- :56 - pl125, pl126, pl142: jabrena/plinth `skills/<n>-<name>/references/<n>-<name>.md` for 125-java-concurrency,
- :57 126-java-exception-handling and 142-java-functional-programming, @a46375a.
- :58 - pl123cc: jabrena/plinth `skills/123-java-design-patterns/references/123-cross-cutting-integration-patterns.md`,
- :59 @a46375a.
- :60 - addy api, addy perf: addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md` and
- :61 `references/performance-checklist.md`, @aeac41d.
- :62 - ps separate: pstack `skills/principle-separate-before-serializing-shared-state/SKILL.md`, @f713f14.
- :63 - JEP 444, JEP 487, JEP 491: OpenJDK, https://openjdk.org/jeps/444, /487 and /491 (§Future Work, §Diagnosing remaining
- :64 cases of pinning).
- :65 - AWS timeouts: Amazon Builders' Library, "Timeouts, retries, and backoff with jitter",
- :66 https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/.
- :67 - JDK `ThreadPoolExecutor`: Java SE 25 Javadoc, `java.util.concurrent.ThreadPoolExecutor` §Queuing, §Rejected tasks.
- :68 - Resilience4j bulkhead: https://resilience4j.readme.io/docs/bulkhead.
- :69 - Stripe idempotent requests: https://docs.stripe.com/api/idempotent_requests.
- :70 - Caffeine Eviction: https://github.com/ben-manes/caffeine/wiki/Eviction §Size-based.
- :72 Operator preference, 2026-10-31 (SRC2), in whole or in part: CC1, CC2, CC9, CC5 and CC6.
- :78 **Bad** (neutral)
- :89 **Good** (neutral)
- :104 **Bad** (from jabrena/plinth `skills/125-java-concurrency/references/125-java-concurrency.md`:1596)
- :117 **Good** (from jabrena/plinth `skills/125-java-concurrency/references/125-java-concurrency.md`:1562)
- :138 **Bad** (from addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md`:163)
- :156 **Good** (from addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md`:167, :213)
- :179 pl125 :38, which says otherwise, is stale (CC1). — **Do not skip when** the blocking call runs inside a class
- :185 :95). — **Do not skip when** the key is minted per attempt: every retry is then a new effect (addy api :163). —
- :188 single-writer actor or a compare-and-swap (CC5; ps separate :16). — **Do not skip when** the actors publish
- :189 independent facts: give each its own target (ps separate :15). — **Confidence** high
- :190 - **Skip when** the `join()` sits at the outer boundary of the flow, such as a batch entry point (CC6; pl142 :839). —

### code/references/design.md

- :15 | more than one job | one seam per job (SEAM1) | a class has one job, one reason to change (pl121p Example 2); operator preference |
- :16 | an input | one record (SEAM1) | operator preference |
- :17 | an outcome to return | a sealed result (SEAM1); its caller switches over it with no `default` arm (TY2, `types.md`) | the compiler must fail when a new variant is not handled (pstack :20); the compiler confirms every permitted subclass is covered (JEP 409) |
- :18 | a decision to make | a pure function that calls no I/O (SEAM1) | isolate side effects at the edges (pl142 :740); return results, do not produce side effects (mattpocock `codebase-design/SKILL.md` :83) |
- :19 | I/O to do | a method that does the I/O and chooses no outcome (SEAM1) | isolate side effects at the edges (pl142 :740) |
- :20 | a choice among several cases | a rule list, not an if-ladder; each method at cyclomatic complexity ≤5 (SEAM1) | operator preference |
- :21 | a value that may be absent | `Optional`, a sealed type or an enum (TY1, `types.md`) | a bag of optional fields lets contradictory combinations compile (pstack :15) |
- :24 `pstack` is cursor-plugins pstack `skills/principle-type-system-discipline/SKILL.md`. `pl121p` is plinth
- :25 `121-java-object-oriented-design-principles.md` and `pl142` is plinth `142-java-functional-programming.md`. `:N` is
- :26 the line. The sealed result and the pure decision are industry rules; the other SEAM1 parts are operator preference.
- :28 Operator preference, 2026-10-31 (SRC2), in whole or in part: SEAM1.

### code/references/errors.md

- :39 | a case the caller can foresee: not found, already exists, over limit | a sealed outcome in the return type (ER1), never an `Either` (ER7) | operator preference; a case the types let you ignore becomes a runtime failure the compiler could have stopped (types :9) |
- :40 | a fault: a non-success the caller cannot foresee | throw the one base exception type with a machine-readable error code (ER2) | operator preference; every error response follows one shape with a machine-readable code (api :61-86) |
- :41 | an exception that must become an HTTP response | the one central exception handler (ER11), with the error code's generic message as the body (ER10) | translate at the boundary with centralized handlers (exc :32, :2184) · define a global error handler (OWASP) · never expose stack traces or internal error details (sec :73, :98) · log the detail, give users a generic message (exc :26) |
- :42 | a caught exception that is rethrown | the caught exception passed as the cause (ER3) | operator preference; chaining keeps the full error context (exc :27) |
- :43 | a caught exception that is not rethrown | handle it or log it, never an empty block (ER3) | an empty catch block hides the problem (exc :1948) · errors silently swallowed (rubric :10) |
- :44 | an `InterruptedException` | `Thread.currentThread().interrupt()`, or a rethrow (ER5) | operator preference; restore the interrupted status (exc :28) |
- :45 | a `catch` clause | the narrowest type the `try` can raise (ER4) | operator preference for the narrowest type and the must-not-fail boundary; specific types, not generic `Exception` (exc :23) · `Throwable` or `Error` can mask `OutOfMemoryError` (exc :2374); an `Error` is a problem a reasonable application should not try to catch (JDK `Error`) |
- :46 | a best-effort metric or audit call that fails | catch, log at WARN with the exception (LG3, `../../obs/references/logging.md`), continue (ER8) | WARN means degraded but handled (obs :75) · an empty catch block hides the problem (exc :1948) |
- :47 | request input | Bean Validation at the boundary, no second check inside (ER6) | validate at the boundary, trust the types inside (boundary :14-15, :24) · validate at system edges (api :90) · Bean Validation of web input (Spring Framework, Validation) |
- :49 `types` is pstack `skills/principle-type-system-discipline/SKILL.md`, `boundary` is pstack
- :50 `skills/principle-boundary-discipline/SKILL.md`, `rubric` is pstack `skills/interrogate/references/rubric.md`, `exc` is
- :51 plinth `126-java-exception-handling.md`, `api` is addy `skills/api-and-interface-design/SKILL.md`, `sec` is addy
- :52 `skills/security-and-hardening/SKILL.md` and `obs` is addy `skills/observability-and-instrumentation/SKILL.md`; `:N`
- :53 is the line. OWASP is the Error Handling Cheat Sheet,
- :54 https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html. JDK `Error` is the Java SE Javadoc of
- :55 `java.lang.Error`. Spring Framework, Validation is
- :56 https://docs.spring.io/spring-framework/reference/core/validation/beanvalidation.html.
- :58 Operator preference, 2026-10-31 (SRC2), in whole or in part: ER1, ER2, ER7, ER3, ER4 and ER5.
- :67 **Bad** (neutral)
- :81 **Good** (neutral)
- :104 **Bad** (from plinth 126:2387-2395)
- :114 **Good** (from plinth 126:2376-2384)
- :126 **Bad** (from plinth 126:1944-1950)
- :138 **Good** (from plinth 126:1910-1919)
- :154 **Bad** (from plinth 126:2220-2230)
- :167 **Good** (from plinth 126:2189-2215 and 126:410-415)
- :188 that continues is allowed there, with a comment (ER4, ER8; WARN means degraded but handled, obs :75). — **Do not
- :190 `Throwable` or `Error` (ER4; exc :2374). —
- :209 comment (operator preference).

### code/references/examples/security.md

- :10 **Bad** (from addyosmani/agent-skills skills/security-and-hardening/references/hardening-patterns.md:126)
- :22 **Good** (from addyosmani/agent-skills skills/security-and-hardening/references/hardening-patterns.md:129-147)
- :46 **Bad** (neutral)
- :59 **Good** (from addyosmani/agent-skills references/security-checklist.md:80-92)
- :82 **Bad** (from jabrena/plinth skills/124-java-secure-coding/references/124-java-secure-coding.md:737-756)
- :98 **Good** (from jabrena/plinth skills/124-java-secure-coding/references/124-java-secure-coding.md:716-733)
- :116 **Bad** (neutral)
- :131 **Good** (encoder from jabrena/plinth skills/304-frameworks-spring-boot-security/references/304-frameworks-spring-boot-security.md:184-203; HMAC half neutral)

### code/references/examples/smells.md

- :11 **Bad** (neutral)
- :28 **Good** (neutral)
- :49 **Bad** (from martinfowler.com bliki FlagArgument, adapted)
- :65 **Good** (neutral)
- :85 **Bad** (from refactoring.com catalog Remove Middle Man, adapted)
- :99 **Good** (from refactoring.com catalog Remove Middle Man, adapted)
- :110 **Bad** (neutral)
- :123 **Good** (neutral)
- :140 **Bad** (neutral)
- :153 **Good** (neutral)

### code/references/examples/spring.md

- :14 **Bad** (from plinth 301 :791, Example 7)
- :32 With no `LoyaltyService` bean, `loyalty` stays null, so every order fails after it is saved. SF §Constructor-based or
- :35 **Good** (neutral)
- :58 **Bad** (from plinth 301 :486, Example 4)
- :78 **Good** (from plinth 301 :462, Example 4)
- :100 **Bad** (from SF §Using the @Bean Annotation, Declaring a Bean)
- :110 **Good** (from SF §Using the @Bean Annotation, "declare the most specific return type possible")
- :122 **Bad** (from plinth 301 :1091, Example 10)
- :141 **Good** (from plinth 301 :645, Example 6)
- :163 **Bad** (from plinth 301 :1212, Example 11)
- :172 **Good** (record from plinth 301 :1188, Example 11; spec from rrezartprebreza/spring-boot-skills
- :195 **Bad** (from plinth 301 :510, Example 4)
- :207 **Good** (neutral)
- :221 **Bad** (from plinth 301 :366, Example 3)
- :233 A long load runs inside an event listener, on the thread that publishes the event. SB §Application Events and Listeners:
- :236 **Good** (from SB §Using the ApplicationRunner or CommandLineRunner)
- :256 **Bad** (from plinth 311 :1073, Example 14)
- :275 **Good** (from plinth 311 :1049, Example 14)

### code/references/java.md

- :39 | the logic reads the current time or makes a new id | an injected `Clock` (`Instant.now(clock)`, `LocalDate.now(clock)`) or a `Supplier<UUID>` (U4); the test's fixed clock is U1 (unit-tests.md) | `Instant.now()` is a static call on a final type, so a test cannot stub it (plinth 321 :136); alternate clocks plug in to simplify testing (JDK `Clock` Javadoc) |
- :40 | a point in time or a span of time | `Instant` for the point, `Duration` for the span (JV1) | `Instant` is machine time and `Duration` a time-based amount (pl 141 R:294; JDK tutorial *Instant Class*); `SimpleDateFormat` is not synchronized (JDK `SimpleDateFormat` Javadoc) |
- :41 | a local variable whose right-hand side is a method call | the type written out, unless the method's name states the type (JV5) | `var result = processData(data)` hides the return type (pl 141 R:507-508); `var` with a diamond infers `Object` (OpenJDK *LVTI Style Guidelines*) |
- :42 | a `toMap` whose keys may collide | a merge function (JV4) | a duplicate key throws `IllegalStateException` (JDK `Collectors.toMap` Javadoc; pl 142 R:772) |
- :44 | an I/O, logging or state-changing step in a stream | that step outside the pipeline (JV3) | side effects in behavioral parameters are discouraged (JDK `java.util.stream` package summary); isolate side effects at the edges (pl 142 R:740) |
- :45 | a multi-line SQL, JSON or HTML string | a text block (JV7) | embedded SQL, HTML or JSON in string literals is hard to read and maintain (JEP 378; pl 141 R:914) |
- :46 | an `AutoCloseable` opened in a method | a try-with-resources header (JV8) | each resource closes at the end of the statement (Java Tutorial *try-with-resources*; pl 126 R:195) |
- :50 tutorials. U4, JV2, JV9 and CV3 are operator preferences: JV2 follows the JDK warning on shared state in parallel
- :51 streams; JV9 and CV3 follow Google Java Style §4.1.1 and §4.4.
- :53 Operator preference, 2026-10-31 (SRC2), in whole or in part: U4, JV2, JV9 and CV3.
- :59 **Bad** (from plinth-pinned `321-frameworks-spring-boot-testing-unit-tests.md`:189)
- :70 **Good** (from plinth-pinned `321-frameworks-spring-boot-testing-unit-tests.md`:133; JDK `Clock` Javadoc)
- :89 **Bad** (from plinth-java-skills `141-java-refactoring-with-modern-features.md`:291, Example 4)
- :103 **Good** (from plinth-java-skills `141-java-refactoring-with-modern-features.md`:291, Example 4)
- :118 **Bad** (from plinth-java-skills `141-java-refactoring-with-modern-features.md`:457, Example 6; OpenJDK *LVTI Style
- :126 **Good** (from plinth-java-skills `141-java-refactoring-with-modern-features.md`:457, Example 6)
- :137 **Bad** (neutral)
- :144 **Good** (neutral)
- :154 - **Skip when** a framework's own style guide bans `var` (Spring Framework CONTRIBUTING.md:597): that ban serves a

### code/references/messaging.md

- :21 | a consumer that changes state | processing that handles a duplicate record safely (MS6) | consumers that change state must handle duplicates (pl123k :42) · no queue gives exactly-once across a consumer crash (addy api :335) |
- :22 | a check for "already done" followed by the act | one atomic claim: a unique constraint or a row lock picks the winner (MS6) | a check followed by an act is a race (addy api :173, :182, :347) |
- :23 | a step that leaves something behind: a lock, a temporary file, a half-written record, a claimed job | a marker the next run can judge stale, such as a temporary path renamed into place (MS6) | a marker the next run cannot judge turns every crash into manual cleanup (ps idempotent :14, :16) |
- :24 | a record that cannot be parsed | a dead-letter topic, with no retry (MS4) | define retry, DLT, alerting and replay behaviour for poison records (pl123k :45) · a `DeserializationException` is fatal, unlikely to be resolved on a retried delivery; the recoverer publishes it to a dead-letter topic (Spring Kafka error handling) |
- :26 Sources, all read at a pinned commit or at the URL named; `:N` is a line:
- :28 - pl123k: jabrena/plinth `skills/123-java-design-patterns/references/123-kafka-event-driven-patterns.md`, @a46375a.
- :29 - addy api: addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md`, @aeac41d.
- :30 - ps idempotent: pstack `skills/principle-make-operations-idempotent/SKILL.md`, @f713f14.
- :31 - Spring Kafka error handling: https://docs.spring.io/spring-kafka/reference/kafka/annotation-error-handling.html
- :32 §DefaultErrorHandler, §Publishing Dead-letter Records.
- :38 **Bad** (from addy api :176-180)
- :51 **Good** (from addy api :182-190)
- :71 to reconcile; the "runs twice" question still applies (MS6; ps idempotent :22). — **Do not
- :73 are not in one transaction (addy api :335). — **Confidence** medium

### code/references/security.md

- :109 | puts a value or a column name into SQL | a bound parameter for a value; an allowlist in code for an identifier (SE3) | input concatenated into SQL is an injection surface · OWASP SQL Injection Prevention Cheat Sheet §Prepared Statements, §Allow-list Input Validation; plinth 124-java-secure-coding "Never concatenate user input directly into SQL"; addyosmani security-checklist |
- :115 | must carry a bearer credential to the server | a header, an HttpOnly cookie, or a single-use short-lived ticket (SS8) | a URL leaks into logs and Referer · RFC 6750 §2.3, §5.3; OWASP REST Security Cheat Sheet |
- :116 | authenticates with a cookie | `HttpOnly; Secure; SameSite=Strict`, narrowest `Path`, and an `Origin` check (SS9) | stateless is no CSRF protection when a cookie authenticates · Spring Security csrf §CSRF and Stateless Browser Applications; OWASP Session Management and CSRF Prevention Cheat Sheets |
- :118 | logs users in through an external IdP | Spring `oauth2Login` (SS11) | `nonce` stops replay, bound `state` stops login CSRF · OIDC Core §3.1.3.7; ASVS V10 |
- :119 | checks who owns a resource, or adds an auth step | an `AuthorizationManager`, a SpEL bean, a chain filter or a meta-annotation (SS26) | operator preference: a hand-rolled check misses what the framework already checks |
- :121 | tests a guard | a guard bean's unit spec may use `@WithMockUser` or `jwt()`; an IT logs in for real (SS22) | operator preference · Spring Security testing: `@WithMockUser` "cannot apply to full HTTP requests" |
- :123 Operator preference, 2026-10-31 (SRC2), in whole or in part: SE2, SE7a, SS2, SS17, SS26, SS22, SS23 and SS25.
- :131 **Bad** (from addyosmani/agent-skills skills/security-and-hardening/references/hardening-patterns.md:126)
- :143 **Good** (from addyosmani/agent-skills skills/security-and-hardening/references/hardening-patterns.md:129-147)
- :167 **Bad** (neutral)
- :182 **Good** (encoder from jabrena/plinth skills/304-frameworks-spring-boot-security/references/304-frameworks-spring-boot-security.md:184-203; HMAC half neutral)
- :207 when** a second party verifies the token: add `iss` and `aud`. — **Confidence** high (RFC 8725 §3.9; OWASP JSON
- :208 Web Token Cheat Sheet §MAC "Do not reuse the same secret with another audience")

### code/references/services.md

- :22 | a branch that chooses an outcome: a state check, or the order of calls | a service method that returns the outcome (LY1) | pstack principle-boundary-discipline :9 "Business logic lives in pure functions. The shell is thin" · Jeffallan :183 `@Service` for business logic, `@RestController` for HTTP · plinth 301 :203 web stereotypes for HTTP adapters, `@Service` for application logic |
- :23 | a dependency a test replaces with a fake, such as an outbound port, or a type another module calls | an interface and one package-private `Default<Name>` implementation (LY2) | mattpocock tdd/mocking.md :3 "Mock at system boundaries only" · the `Default<Name>` name and package-private: operator preference |
- :24 | a class with one implementation that no test fakes | the concrete class, with no interface (LY2) | mattpocock codebase-design DEEPENING.md :29 "One adapter means a hypothetical seam" · plinth 123-java-design-patterns :44 "NO OVER-ABSTRACTION … single stable implementation" · pstack design-red-flags :33 "Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction" |
- :25 | two operations that must not be split | one use-case method in one transaction (LY3) | plinth 123-database-persistence-patterns :42 "Place transaction boundaries at use-case/service level" and Example 3 · pstack design-red-flags :13 "Callers coordinate several methods to complete one operation" |
- :27 Sources: pstack = cursor-plugins `pstack/skills` (`principle-boundary-discipline/SKILL.md`,
- :28 `architect/references/design-red-flags.md`); mattpocock = mattpocock-skills `skills/engineering`; plinth =
- :29 jabrena-plinth `skills/*/references`; Jeffallan = Jeffallan claude-skills `spring-boot-engineer/SKILL.md`.
- :30 How a bean takes its dependencies (LY6) and binds its settings (LY7) is in `spring.md`.
- :32 Operator preference, 2026-10-31 (SRC2), in whole or in part: LY2.
- :38 **Bad** (neutral)
- :56 **Good** (neutral)
- :75 **Bad** (neutral)
- :93 **Good** (neutral)
- :109 which is allowed (LY1, operator preference). — **Do not skip when** the controller itself checks state or chooses the

### code/references/smells.md

- :67 | a name that does not say what it holds or does | possible **Mysterious Name**: rename it (NM1, NM2) | mp :45 |
- :68 | the same logic shape in two hunks or files | possible **Duplicated Code**: extract it when it is a rule (DS12), not otherwise (DS14) | mp :46 |
- :69 | a method that reads another object's data more than its own | possible **Feature Envy**: move the method to that data; for a record, FW6 | mp :47 |
- :70 | the same fields or parameters travelling together | possible **Data Clumps**: bundle them into one type | mp :48 |
- :71 | a primitive or string standing for a domain concept | possible **Primitive Obsession**: give it its own small type (TY8, `types.md`) | mp :49 |
- :72 | the same `switch` or `if` cascade on one type at several sites | possible **Repeated Switches**: one sealed type or one shared map (DS3) | mp :50 |
- :73 | one logical change that edits many scattered files | possible **Shotgun Surgery**: gather what changes together into one module | mp :51 |
- :74 | one module edited for several unrelated reasons | possible **Divergent Change**: split it so each part changes for one reason | mp :52 |
- :75 | a parameter, hook or abstraction that no current need uses | possible **Speculative Generality**: delete it (DS6) | mp :53 |
- :76 | a caller walking `a.b().c().d()` | possible **Message Chains**: hide the walk behind one method (FW8) | mp :54 |
- :77 | a class or method that mostly delegates | possible **Middle Man**: call the real target (DS4, FW8) | mp :55 |
- :78 | a subclass or implementer that ignores most of what it inherits | possible **Refused Bequest**: drop the inheritance and use composition | mp :56 |
- :87 | a class doing too much: many fields, many responsibilities | possible **Large Class**: Extract Class; a file over 1000 lines is the DS2 operator preference | F 20 |
- :91 | nested or compound conditionals | possible **Conditional Complexity**: model the cases (DS3); nesting is DS9 (`../../deslop/SKILL.md`) | operator preference (SM2) |
- :92 | one problem solved two different ways in one code base | possible **Oddball Solution**: keep one way (NM4) | operator preference (SM2) |
- :93 | a class or method visible beyond the code that needs it | possible **Indecent Exposure**: narrow its visibility (SX14, `spring.md`) | operator preference (SM2) |
- :94 | an unused private member or an unreachable branch | possible **Dead Code**: delete it (DS7, `../../deslop/SKILL.md`) | SM3 · guru dead-code · simplification :152 |
- :96 `mp` is mattpocock `skills/engineering/code-review/SKILL.md` (plugin 1.2.3). `F n` is _Refactoring_ 2e ch. 3 at
- :97 InformIT, `seqNum=n`. `guru` is
- :98 refactoring.guru and `simplification` is addy
- :99 `skills/code-simplification/SKILL.md`. `:N` is the line.
- :100 Smell names checked against refactoring.com; the 2e smell-to-cure pairs were not checked against the book text.
- :102 Operator preference, 2026-10-31 (SRC2), in whole or in part: DS11, SM2, DS1, DS14, DS2, FW1, NM2 and NM4.
- :110 **Bad** (neutral)
- :127 **Good** (neutral)
- :148 **Bad** (from martinfowler.com bliki FlagArgument, adapted)
- :164 **Good** (neutral)
- :186 smell there. — **Confidence** high (mp :41)
- :190 **Confidence** high (mp :40)
- :193 (operator preference, 2026-10-31). — **Confidence** high

### code/references/spring.md

- :82 | a collaborator that may be absent, or zero or more of one type | an `ObjectProvider<T>` field, resolved where it is used, with no `@Lazy` (LY6, SC3) | SF §Constructor-based or setter-based DI: with setter injection "not-null checks must be performed everywhere" · plinth 301 :713 · Jeffallan :189 · resolve at use, no `@Lazy`: operator preference |
- :83 | a dependency cycle that cannot be cut | an `ObjectProvider<T>` field resolved at call time, and a comment naming the cycle (SC2) | SF §Circular dependencies: a constructor cycle throws `BeanCurrentlyInCreationException` · the provider and comment: operator preference |
- :84 | several implementations of one type, and only one should run | one `@ConditionalOnProperty` value per implementation, exactly one matching, an unset flag failing startup (SC4) | plinth 301 :598-599 (Example 6) selects by `@ConditionalOnProperty` · never `@Primary`: operator preference |
- :85 | several settings that belong together | one `@ConfigurationProperties` record (LY7); `@Value` for one scalar no other class reads | SB §@ConfigurationProperties vs. @Value · plinth 301 :429 "avoid scattering many `@Value` fields" · Jeffallan :182 |
- :86 | a check on one settings field | a Jakarta constraint, with `@Validated` on the record (SC15) | SB §@ConfigurationProperties Validation · plinth 301 :1170 · a compact-constructor check alone crashes on a missing key with an unnamed NullPointerException |
- :87 | a rule across settings fields | a compact-constructor check, beside the field constraints (SC15) | operator preference |
- :88 | a startup check on injected state | the constructor (X6) | SF §Initialization Callbacks: `@PostConstruct` runs in the singleton creation lock, "a risk for an initialization deadlock" · plinth 301 :317 "avoid heavy work in `@PostConstruct`" |
- :89 | startup work that must finish before traffic | an `ApplicationRunner` (SC19) | SB §Application Events and Listeners: a runner finishes after context refresh, before the app accepts traffic |
- :90 | startup work that may finish later | a thread started from an `@EventListener(ApplicationReadyEvent)` that returns at once (SC19) | SB §Application Events and Listeners: "Event listeners should not run potentially lengthy tasks" |
- :91 | background work that starts and stops | a `SmartLifecycle` bean (SC20) | SF §Startup and Shutdown Callbacks: `SmartLifecycle` phases |
- :92 | a proxied method (such as `@Transactional`) called from its own class | the method on a second bean (SC21) | SF §Understanding AOP Proxies: "self invocation … will bypass the advice" · plinth 311 :1006 (Example 14) |
- :93 | a service whose methods mostly read | `@Transactional(readOnly = true)` on the class; plain `@Transactional` on each write method (SC23) | plinth 311 :665-668 (Example 10) · Jeffallan data.md :153 · Spring Data JPA §Transactionality: `SimpleJpaRepository` reads run read-only, so Hibernate skips dirty checks |
- :95 Sources: SF = Spring Framework reference, SB = Spring Boot reference (docs.spring.io; one vendor, one source); plinth
- :96 301 / 311 = jabrena-plinth `skills/301-frameworks-spring-boot-core` and `311-frameworks-spring-jdbc` references;
- :97 Jeffallan = Jeffallan claude-skills `spring-boot-engineer/SKILL.md`. Rules without a row: SC1 one constructor (SF
- :98 §Constructor-based DI, plinth 301 :713), the rest operator preference; SC5 SF §Java-based Configuration (CGLIB
- :99 subclass); SC6 SF §Using the @Bean Annotation "declare the most specific return type"; SC8 SB §Detecting Test
- :100 Configuration, plinth 301 :53; SC11 SB §Constructor Binding, plinth 301 :429, :1170; SC12 as LY7; SC13 and SC10 SB
- :101 §Property Placeholders and §Relaxed Binding (kebab-case is canonical); SC14 SB §Converting Durations (a bare `long`
- :102 binds as milliseconds); SC15 the runner spec: rrezartprebreza/spring-boot-skills
- :103 `spring-boot-4/configuration-properties/SKILL.md:44-46`, giuseppe-trisciuoglio/developer-kit
- :104 `unit-test-config-properties/SKILL.md:31,34`; SC16 plinth 301 :1407 "Do not commit secrets", Jeffallan :194 "Hardcode … credentials" (MUST
- :105 NOT); SC17 JDK `java.lang.Record#toString` (the implicit string holds each component's name and value); SX18 Checkstyle
- :106 `HideUtilityClassConstructor` and `FinalClass`, github/awesome-copilot `instructions/springboot.instructions.md:33`;
- :107 SC9, SX14 and SX19 operator preference.
- :109 Operator preference, 2026-10-31 (SRC2), in whole or in part: LY6, SC1, SC2, SC3, SC4, SC9, SC5, SC6, SC13, SC10, SC14, SC17, SC19, SC20, SX19 and SX14.
- :117 **Bad** (from plinth 301 :791, Example 7)
- :135 With no `LoyaltyService` bean, `loyalty` stays null, so every order fails after it is saved. SF §Constructor-based or
- :138 **Good** (neutral)
- :161 **Bad** (from plinth 301 :486, Example 4)
- :181 **Good** (from plinth 301 :462, Example 4)
- :203 **Bad** (from plinth 311 :1073, Example 14)
- :222 **Good** (from plinth 311 :1049, Example 14)
- :246 `@Qualifier` at the injection point (plinth 301 :1072-1074, Example 10). — **Do not skip when** only one of them
- :250 as `@Primary` does, and a stub resolved by load order once beat the real bean (SC4, operator preference). —
- :256 come from environment variables or an untracked file outside the repo (operator preference). — **Do not skip when**
- :259 configuration leaks test doubles (operator preference). The industry allows `@Profile`: plinth prefers it over

### code/references/types.md

- :45 | a value that may be absent | `Optional` as a return type (JV6, `java.md`), a sealed interface with records, or an enum (TY1) | a bag of optional fields lets contradictory combinations compile (pstack :15); `Optional` states absence explicitly (pl141 :206) |
- :46 | a closed set of two or more cases | a sealed interface or an enum, and a switch with no `default` arm (TY2) | the compiler must fail when a new variant is not handled (pstack :20, :29); the compiler confirms every permitted subclass is covered (JEP 409) |
- :47 | a record whose fields are legal only in some combinations | one record per legal shape under a sealed interface; the compact constructor for what the shapes cannot exclude (TY3) | a comment that explains when fields are valid means the type is too loose (pstack :15, :26); sealed classes restrict the subclasses to model the domain (JEP 409); the compact-constructor clause is operator preference |
- :48 | two parameters of one primitive type that mean different things | one wrapping record per meaning (TY8) | same-typed arguments that mean different things are branded (pstack :17, :27); give the concept its own small type (mattpocock `code-review/SKILL.md` :49); type-safe wrappers (pl122 Example 4) |
- :49 | a cast, a null check or a "never happens" throw | the check moved into the type, where the value is built (TY9) | that place marks a type too weak (pstack :22, :28) |
- :50 | an operation with an answer for every input | the plain type (TY9) | if nothing would otherwise fail, keep the plain type (pstack :22, :31) |
- :51 | a wire DTO with a missing field | `null` inside the mapping only; `Optional`, a sealed case or an enum out of the adapter (TY12) | external data is untyped until parsed at the boundary (pstack :18) |
- :52 | an amount of money | `BigDecimal` with a set scale and rounding mode (TY5) | floating point is never for precise values such as currency (Java Tutorial *Primitive Data Types*); `BigDecimal` for precision (pl122 :670-672) |
- :53 | a method that returns a collection | an empty collection for "none" (TY7) | never return `null` from a method that returns a collection (pl121m :231-233) |
- :54 | an unchecked warning | the generic type fixed; else `@SuppressWarnings("unchecked")` on one statement, with its reason (TY10); any other suppression is CM7, `comments.md` | raw types defer generic type checks to runtime (Java Tutorial *Raw Types*); suppress only provably safe operations, as narrowly as possible (pl128 :1504-1506) |
- :55 | a value to construct | its record constructor or a static factory (TY13) | prefer constructors, static factories and records first (pl123 :22; pl121c Example 2) |
- :57 `pstack` is cursor-plugins pstack `skills/principle-type-system-discipline/SKILL.md`. `pl122` is plinth
- :58 `122-java-type-design.md`, `pl121m` is plinth `121-java-object-oriented-design-methods.md`, `pl128` is plinth
- :59 `128-java-generics.md`, `pl123` is plinth `123-java-design-patterns.md`, `pl141` is plinth
- :60 `141-java-refactoring-with-modern-features.md` and `pl121c` is plinth
- :61 `121-java-object-oriented-design-object-creation.md`. `:N` is the line.
- :62 TY4, TY6, TY7, TY9, TY11 and TY12 are operator preferences. TY7 follows pl121m :231-233, TY9 pstack :22, TY12
- :63 pstack :18, TY6 pl121-enums Example 2, and TY11 ErrorProne `EqualsIncompatibleType`.
- :64 TY3's sealed-variants part and TY13's constructor-or-factory part are industry; TY3's compact-constructor clause
- :65 and TY13's `Default<Name>` naming are operator preference.
- :67 Operator preference, 2026-10-31 (SRC2), in whole or in part: TY3, TY7, TY9, TY12, TY4, TY6, TY11 and TY13.
- :73 **Bad** (from plinth-java-skills `141-java-refactoring-with-modern-features.md`:203, Example 3)
- :87 **Good** (from plinth-java-skills `141-java-refactoring-with-modern-features.md`:203, Example 3)
- :101 **Bad** (from cursor-plugins pstack `principle-type-system-discipline/SKILL.md`:15)
- :109 **Good** (from cursor-plugins pstack `principle-type-system-discipline/SKILL.md`:15)
- :128 **Bad** (from cursor-plugins pstack `principle-type-system-discipline/SKILL.md`:17)
- :138 **Good** (from cursor-plugins pstack `principle-type-system-discipline/SKILL.md`:17; plinth-java-skills
- :155 **Bad** (from cursor-plugins pstack `principle-type-system-discipline/SKILL.md`:22)
- :166 **Good** (from cursor-plugins pstack `principle-type-system-discipline/SKILL.md`:16, :22)
- :191 - **Skip when** the operation has an answer for every input: keep the plain type (TY9, pstack :22). — **Do not skip
- :194 Example 3): expose one builder (TY13, operator preference). — **Do not skip when** a constructor or a static

### deslop/SKILL.md

- :71 **Bad** (neutral)
- :82 **Good** (neutral)
- :101 boundary. (Real evidence: ledger row DS8. Pair: 68f § DS8 — No null check or try/catch to silence a failure on a trusted
- :108 repo. — **Confidence** high (addy deprecation-and-migration :124, Strangler Pattern)
- :111 in-repo caller (DS8). — **Confidence** high (ctk :13; openclaw :15)
- :115 `openclaw` is openclaw `.agents/skills/deslop/SKILL.md`, `ctk` is cursor-team-kit `skills/deslop/SKILL.md`, and
- :116 `addy <name>` is addy `skills/<name>/SKILL.md`; `:N` is the line.
- :120 | DS13 | openclaw :12, :20, :24 · ctk :8, :20 |
- :121 | DS5 | addy deprecation-and-migration :110 · openclaw :18 |
- :122 | DS7 | addy code-review-and-quality :47 · addy code-simplification :152 · refactoring.guru Dead Code |
- :123 | DS8 | ctk :13 · openclaw :15 |
- :124 | DS9 | addy code-simplification :131, :133 · ctk :15 |
- :126 The categories come from openclaw :14-19 and ctk :12-16. Category rules point at their owner references and do not

## Pinned humanlayer cites (SR8, 2026-11-04)

humanlayer/humanlayer deleted `.claude/commands/create_plan.md` in `d8197bab` (2026-10-22). Every `create_plan` cite
above is pinned to `77c7fe99`, the last commit that changed the file; its text there is what was deleted. Each line was re-read there on 2026-11-04 and still
says what it is cited for.
