# 31c · Good/Bad — mutation (M1–M10), property (P1–P4, P6–P8, P10), Gherkin AC (GA1–GA5), scenario→tests (GT1–GT6)

Read on `origin/master` (fetched 2026-10-02). Format per GB1 (31-good-bad-BRIEF.md).

## Mutation — testing/references/mutation.md

### M1 — Mutation testing is a report, never a gate; threshold stays 0
**Good** (real)
```kotlin
    // A report, never a gate (#456). Set explicitly rather than left to the plugin default, so
    // that the decision is visible in the file where someone would go to change it.
    mutationThreshold.set(0)
```
`build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:15-17` — threshold pinned at 0 in the file a person would edit, with the #456 reason beside it.

**Bad** (n/a) — master has no gating threshold; `make mutation` is outside every gate (`Makefile:236-243`).

### M2 — Read a surviving mutant as a missing case; name its CORRECT/RIGHT-BICEP letter
**Good** (real, partial)
```java
    @Test
    @DisplayName("tool output is redacted Tier-1 only, with the NER sidecar available and unused")
    void shouldNotReachTheNerSidecarWhenSanitizingToolOutput() {
        // given a sidecar the pipeline would call if this path asked for Tier-2
        // when
        ToolOutputSanitizer.Result result = sanitizer.sanitize("{\"contact\":\"ada@example.com\"}", false);

        // then
        assertThat(nerPort.consulted).isFalse();
        assertThat(result.llmBody()).isEqualTo("{\"contact\":\"[EMAIL_1]\"}");
    }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerHardeningTest.java:41-51` — a survivor (class javadoc :18 "answers a mutant that survived") became a named example test asserting the missed decision. Partial: neither javadoc nor name cites the letter (here RIGHT-BICEP **Cross-check** on the NER port), which M2 now requires.

**Bad** (adapted from ToolOutputSanitizerHardeningTest, NEEDS COMPILE CHECK)
```groovy
def "kills mutant on line 88"() {
    expect:
    sanitizer.sanitize("{}", false) != null
}
```
— names a line, not a case; no letter; asserts non-null, so the next mutant on the same line survives too.

### M3 — Report score and test strength; NO_COVERAGE = not reached, survived = not asserted
**Good** (adapted from pitest.org report fields — no mutation report is committed on master)
```text
make mutation · aruvii-guardrails · PIT DEFAULTS
mutation score 71% (142/200) · test strength 89% (142 killed ÷ 160 killed+survived)
NO_COVERAGE 40 → not reached by any test (coverage gap, add a test that runs it)
SURVIVED 18 → reached, not asserted (missing case, see M2)
```
— both numbers, and the two non-kills read as different defects.

**Bad** (adapted)
```text
mutation score 71% — good enough
```
— one number mixes unreached code with unasserted code; reader cannot tell which fix is needed.

### M4 — Exclude only code with no decision in it; never to raise the number
**Good** (real)
```kotlin
    // Bean wiring, not behaviour — nobody writes a test for how a bean is assembled.
    // Deliberately NOT excluding get*/set*/is*: CustomPiiResponse.isAllow/isBlock/isRedact
    // are `"ALLOW".equals(action)` decisions, not accessors, and must stay measured.
    excludedClasses.set(listOf("*Config", "*Properties"))
```
`build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:22-25` — excludes wiring (`*Config`, `*Properties`) and says why `is*` accessors stay in: they hold decisions.

**Bad** (adapted, NEEDS COMPILE CHECK)
```kotlin
excludedClasses.set(listOf("*Config", "*Properties", "*Sanitizer", "get*", "is*"))
```
— drops `ToolOutputSanitizer` and `CustomPiiResponse.isAllow` decisions to lift the score.

### M5 — After changing exclusions/avoidCallsTo, compare per-class mutant counts before and after
**Good** (real)
```kotlin
    // avoidCallsTo REPLACES pitest's defaults rather than adding to them, so the four logging
    // packages must be repeated here. Omitting them makes every `log.warn(...)` mutable and
    // added 14 survivors in one run (measured, #505).
    avoidCallsTo.set(listOf(
        "java.util.logging",
        "org.apache.log4j",
        "org.slf4j",
        "org.apache.commons.logging",
        "org.springframework.http.client",
    ))
    // Not "org.springframework.web.client": it would also suppress the RestClient call inside
    // evaluate(), which is real behaviour. One wiring mutant in defaultRestClient stays
    // uncovered as a result, and that is the cheaper of the two mistakes.
```
`build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:31-43` — records the measured +14 survivors and why the broader `web.client` glob was rejected (would hide `evaluate()`).

**Bad** (adapted, NEEDS COMPILE CHECK)
```kotlin
avoidCallsTo.set(listOf("org.slf4j", "org.springframework"))
```
— over-matching glob; total survivors fall, which looks like success while real RestClient calls stop being mutated. No before/after count.

### M6 — Keep PIT DEFAULTS mutators; never ALL
**Good** (real)
```kotlin
extensions.configure<PitestPluginExtension>("pitest") {
    junit5PluginVersion.set(version("pitestJunit5"))
    pitestVersion.set(version("pitest"))

    failWhenNoMutations.set(true)
```
`build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:9-13` — the whole `pitest` block (`:9-50`) sets no `mutators`, so PIT DEFAULTS apply.

**Bad** (adapted, NEEDS COMPILE CHECK)
```kotlin
mutators.set(listOf("ALL"))
```
— pulls in unstable non-default operators and floods the report with equivalent mutants.

### M7 — Run make mutation after branching logic in guardrails; other modules: wire in, say so
**Good** (real)
```text
6. **Mutation-test what you just wrote.** `make mutation` runs PIT against `aruvii-guardrails` today;
   if you added real branching logic to another module, wire it in there too (a `build.gradle.kts`
   change, not a redesign) and run it. A survived mutant on logic you just wrote is a red test, not a
```
`docs/agents/personas/developer.md:58-60` — guardrails is the wired module; another module must be wired in first. Missing: "say so in the MR".

**Bad** (real)
```text
`make mutation` runs PIT against `aruvii-guardrails` (`gradlew :aruvii-guardrails:pitest`) — a report,
not a gate (deliberately, per #456), because a mutation score needs a human reading it, not a
threshold. It exists for exactly the failure this whole translation step is vulnerable to: a unit test
that passes today but would still pass if the logic it's supposedly covering were deleted. Run it on
any module you've added meaningful branching logic to, even outside `aruvii-guardrails` — wiring a
second module in is a `build.gradle.kts` change away, not a redesign.
```
`.claude/skills/gherkin-to-test/SKILL.md:66-71` — "Run it on any module" via `make mutation`, which only runs `:aruvii-guardrails:pitest` (`Makefile:242-245`); reads as if other modules are covered.

### M8 — Mutant is equivalent only with a stated reason; unsure = recorded gap
**Good** (adapted from pitest.org basic concepts; no equivalent-mutant claim exists on master)
```text
Gap · <Class>:<line> CONDITIONALS_BOUNDARY survived (`> 0` → `>= 0`)
equivalent? unsure — the two differ only for an empty body; not proven unreachable.
recorded as gap, not as equivalent; risk: <what breaks if it is not equivalent>.
```
— names the mutant, the reason, and records doubt as a gap.

**Bad** (adapted)
```text
18 survivors — all equivalent, ignore.
```
— no reason per mutant; turns survivors into silence.

### M9 — Do not rely on withHistory for a verdict you will trust
**Good** (real)
```kotlin
    timestampedReports.set(false)
    outputFormats.set(listOf("HTML", "XML"))
    // coerceAtLeast(1): integer division gives 0 on one core, and pitest with 0 threads does
    // nothing while exiting successfully.
    threads.set((Runtime.getRuntime().availableProcessors() / 2).coerceAtLeast(1))
```
`build-logic/src/main/kotlin/aruvii.mutation-conventions.gradle.kts:45-49` — the block ends with no `withHistory`/`historyInputLocation`: every run is a full analysis.

**Bad** (adapted, NEEDS COMPILE CHECK)
```kotlin
withHistory.set(true)
```
— incremental reuse rests on an assumption PIT itself calls unproven; a stale kill can be reported.

### M10 — Mutation-kill test passes first run; prove with a temporary hand mutation, then revert
**Good** (adapted from ChatMessageHardeningSpec, NEEDS COMPILE CHECK)
```groovy
/** Kills survivor ChatMessage.withContent (dropped toolCallId).
 *  Proved: hand-edited withContent to pass null toolCallId -> this failed; reverted. */
def "withContent carries toolCallId across"() {
    when: "the body is redacted"
    def copy = original.withContent('{"contact":"[EMAIL_1]"}')

    then: "the tie to the assistant call survives"
    copy.toolCallId() == "call_1"
}
```
(`original` as built in `ChatMessageHardeningSpec.groovy:29-31`) — green on first run, and the record of the temporary mutation is what proves it can fail.

**Bad** (real, partial)
```groovy
/**
 * REQ-052 · #223 — withContent replaces the body and nothing else.
 *
 * <p>Answers the one mutation site this REQ added to the record, which no other test in this
 * module covers. The method exists so the worker's history compressor can hand a summarising
 * provider a redacted TOOL frame; a copy that quietly lost toolCallId would break the tie between
 * that frame and the assistant call it answers, and one that lost role would change which frames
 * the compressor redacts at all. The record's own javadoc warns the result must never be
 * persisted — this pins that the copy is otherwise faithful.
 *
 * <p>Converted from ChatMessageHardeningTest (#492). Same assertions, block by block.
```
`aruvii-chat/src/test/groovy/ai/aruvii/chat/domain/ChatMessageHardeningSpec.groovy:7-17` — a kill test with no trace of a hand mutation proving it can fail; nothing shows it was ever red.

## Property — testing/references/property-based.md

### P1 — Property when the requirement says "for any input"; otherwise examples
**Good** (real)
```java
    @Test
    @DisplayName("replay redaction is idempotent, so a replayed window settles instead of drifting")
    void shouldNotRedactItsOwnPlaceholdersOnTheNextTurn() {
        forAllBodiesCarryingTwoEmails(body -> {
            final String once  = sanitizer.redactForReplay(body);
            final String twice = sanitizer.redactForReplay(once);

            assertThat(twice).isEqualTo(once);
        });
    }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerPropertyTest.java:137-146` — idempotence ("a replayed window settles") is a for-any law, so it is a property.

**Bad** (real)
```gherkin
Scenario: No number of failures produces an unbounded wait
  Given any number of consecutive failed attempts against one account
  When the next attempt is made
  Then the backoff is at most the account cap
  And the backoff is finite
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:331-335`
```groovy
    def "no number of failures produces an unbounded wait"() {
        expect: "D1 — an attacker driving a victim's key costs them the cap, never their account"
        secondsOf(decide(Integer.MAX_VALUE, 0)) == unspread().accountCapSeconds()
    }
```
`aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:43-46` — REQ says "any number of consecutive failed attempts"; the unit spec checks one value (`Integer.MAX_VALUE`). An invariant over all counts tested as one example.

### P2 — A property never replaces examples; boundary cases stay as examples beside it
**Good** (real)
```java
    @Test
    @DisplayName("an absent replayed body yields an empty one, never null")
    void shouldReturnEmptyForAnAbsentReplayedBody() {
        assertThat(sanitizer.redactForReplay(null)).isEmpty();
        assertThat(sanitizer.redactForReplay("")).isEmpty();
    }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerTest.java:185-190` — Existence boundary (null, "") kept as an example in `ToolOutputSanitizerTest` beside the property class; the property generators never produce `null`.

**Bad** (n/a) — both property users on master have example siblings (`ToolOutputSanitizerTest.java`, `aruvii-ui/playwright/unit/history.spec.ts`).

### P3 — A conditional property counts branch hits; fails if a branch is never reached
**Good** (adapted from ToolOutputSanitizerPropertyTest:67-77 — the harness has no counting yet, NEEDS COMPILE CHECK)
```java
final AtomicInteger passed = new AtomicInteger();
Property.forAll(Gen.asciiStrings(80), Gen.booleans(), (rawBody, piiGoverned) -> {
    final ToolOutputSanitizer.Result result = sanitizer.sanitize(rawBody, piiGoverned);
    if (result instanceof ToolOutputSanitizer.Result.Passed) {
        passed.incrementAndGet();
        assertThat(result.userVisibleBody()).isEqualTo(rawBody);
    }
});
assertThat(passed.get()).as("Passed branch reached").isPositive();
```
— the `if` branch is counted and the test fails if no case ever reached it. Real near-miss: `ToolOutputSanitizerPropertyTest.java:48-53` javadoc records the earlier version that "passed a thousand times a run having never once reached the branch", fixed by a generator, not a count.

**Bad** (real)
```java
    @Test
    @DisplayName("a passed verdict hands the human the tool's own bytes, whatever the input")
    void shouldNeverAlterTheBodyTheHumanSeesUnlessBlocked() {
        Property.forAll(Gen.asciiStrings(80), Gen.booleans(), (rawBody, piiGoverned) -> {
            final ToolOutputSanitizer.Result result = sanitizer.sanitize(rawBody, piiGoverned);

            if (result instanceof ToolOutputSanitizer.Result.Passed) {
                assertThat(result.userVisibleBody()).isEqualTo(rawBody);
            }
        });
    }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerPropertyTest.java:67-77` — conditional assertion with no count; if a generator change made every body Blocked, this passes having checked nothing.

### P4 — Seed random per run, printed on failure, replayable; never fixed, never retried
**Good** (real)
```java
    /**
     * Random per run so the tier keeps exploring, overridable so a reported failure replays
     * exactly. A fixed default would turn a property into a thousand fixed examples.
     */
    private static long seed() {
        return Optional.ofNullable(System.getProperty("aruvii.property.seed"))
            .map(Long::parseLong)
            .orElseGet(() -> new Random().nextLong());
    }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/property/Property.java:134-142` — random per run, `aruvii.property.seed` replays; `report()` (`:126-132`) prints it.

**Bad** (real)
```ts
export function check<T>(
  gen: Gen<T>,
  predicate: (value: T) => boolean | void,
  opts: PropertyOptions = {},
): Counterexample<T> | null {
  const { runs = 200, seed = 0x5eed } = opts;
  const rng = rngFrom(seed);
```
`aruvii-ui/playwright/support/property.ts:114-120` — default `seed = 0x5eed`: every UI property run explores the same 200 cases, a fixed example set in disguise.

### P6 — Generators include edge cases (0, 1, min, max, empty) by default
**Good** (real)
```ts
const ROLE: Gen<string> = oneOf('ASSISTANT', 'assistant', 'USER', 'TOOL', 'SYSTEM', 'ERROR', '');
const CONTENT: Gen<string> = oneOf('', '   ', '\n\t ', 'ok', 'It is 21°C.');
const TOOL_NAME: Gen<string> = oneOf('weather', 'email', 'rag_search');
const CALL_ID: Gen<string> = oneOf('call-1', 'call-2', 'call-3');
```
`aruvii-ui/playwright/property/history.property.spec.ts:20-23` — alphabets list the empty and whitespace-only cases first, so they are drawn every run; `arrayOf` (`support/property.ts:58`) also draws length 0.

**Bad** (real)
```java
 * <p>What this gives up against a real framework: stateful/model-based testing, exhaustive
 * generation, edge-case injection, statistics. What it keeps is what these properties need —
 * random cases, coordinate-wise shrinking, and a reproducible seed.
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/property/Property.java:25-27`
```java
    private static Gen<String> strings(int maxLength, char from, char to) {
        return new Gen<>() {
            @Override public String generate(Random random) {
                final int length = random.nextInt(maxLength + 1);
                final StringBuilder out = new StringBuilder(length);
                for (int i = 0; i < length; i++) {
                    out.append((char) (from + random.nextInt(to - from + 1)));
                }
                return out.toString();
            }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/property/Gen.java:66-75` — the JVM harness says outright it gives up edge-case injection; `strings` draws length uniformly in [0, max], so `""` and max-length appear only by chance (~1 in 81 for `asciiStrings(80)`).

### P7 — A JVM property is a unit test: runs in make test, counts toward coverage
**Good** (real)
```java
 * <p>A unit test, run by every backend test target and counted in coverage like any other. It was
 * tagged {@code property} and excluded, which meant the invariants most worth having — the ones
 * whose failure is a security defect — were the ones the main gate did not run (#440).
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerPropertyTest.java:28-30`
```make
# The JVM property tests are NOT here any more: they are unit tests and run in `test` with every
# other one (#440). What remains is the UI's Playwright tier, which uses a different runner
# entirely — the only reason this target still exists.
##! deploys: no  ·  destroys: no
##! runs: npm run test:property:pw
##! not: the JVM property tests are NOT here — they are unit tests and run inside `test` (#440)
test-property: ## Property tests that need their own runner — the UI's Playwright tier
	@cd $(UI_DIR) && npm run test:property:pw
```
`Makefile:280-287` — the property class runs in every backend test target and the Makefile states it is not tagged out.

**Bad** (n/a) — the `@Tag("property")` exclusion the javadoc describes was removed in #440; no JVM property is tagged out on master.

### P8 — Build generators by mapping/combining, not filtering; never loosen discards to pass
**Good** (real)
```java
    private static Gen<String> injectedBodies() {
        final Gen<String> verbs  = Gen.oneOf("ignore", "disregard", "forget", "override", "bypass");
        final Gen<String> nouns  = Gen.oneOf("instructions", "rules", "guidelines",
                                             "constraints", "directives");
        final Gen<String> filler = Gen.alphaStrings(1, 20);
        return new Gen<>() {
            @Override public String generate(final Random random) {
                return body(verbs.generate(random), filler.generate(random), nouns.generate(random));
            }
```
`aruvii-guardrails/src/test/java/ai/aruvii/guardrails/application/ToolOutputSanitizerPropertyTest.java:194-202` — the injection body is composed from verb/filler/noun generators, so every case trips the guard without rejecting any.

**Bad** (adapted from ToolOutputSanitizerPropertyTest, NEEDS COMPILE CHECK)
```java
Property.forAll(Gen.asciiStrings(80), rawBody -> {
    if (!rawBody.contains("ignore") || !rawBody.contains("instructions")) return;
    assertThat(sanitizer.sanitize(rawBody, false))
        .isInstanceOf(ToolOutputSanitizer.Result.Blocked.class);
});
```
— filters random ASCII for a rare shape; effectively every case is discarded and the property passes vacuously.

### P10 — UI properties: fast-check, seed printed, numRuns explicit, no retries
**Good** (real, partial)
```ts
  // Zero, and it must stay zero: the harness is seeded, so a property that fails and then passes on
  // retry would mean the property is unsound, not that the run was unlucky. Hiding that is the
  // point of REQ-072.
  retries: 0,
```
`aruvii-ui/playwright.property.config.ts:21-24`
```ts
  if (found) {
    throw new Error(
      `Property failed: ${description}\n` +
      `  after ${found.run} run(s), seed ${found.seed}\n` +
      `  shrunk counterexample: ${JSON.stringify(found.value)}\n` +
      `  ${found.error}`,
```
`aruvii-ui/playwright/support/property.ts:164-169` — retries 0 with the reason, and the seed printed in every failure. Partial: harness is home-grown, not fast-check (P10 names fast-check; P5 keeps the home-grown JVM runner — reconcile).

**Bad** (real)
```ts
  test('the singular and plural assistant questions never disagree', () => {
    forAll('assistantReply === assistantReplies[0] ?? null', HISTORY, messages =>
      assistantReply(messages) === (assistantReplies(messages)[0] ?? null));
  });
```
`aruvii-ui/playwright/property/history.property.spec.ts:53-56` — no `runs` passed, so `numRuns` is the harness default (200) and the seed the fixed `0x5eed` (`support/property.ts:119`); nothing at the call site says how hard it searched.

## Analyst Gherkin — planning/references/acceptance-criteria.md

### GA1 — Scenarios live in the REQ AC section as one fenced gherkin block
**Good** (real)
~~~~gherkin
```gherkin
# CORRECT · Existence — the defect this REQ exists for: a counter with no TTL
@domain @security
Scenario: A failure counter always carries an expiry
  Given a caller with no previous failed attempts
  When a failed attempt is recorded
  Then the counter exists
  And the counter has a positive time to live
~~~~
`docs/spec/REQ-500-login-throttle-progressive-delay.md:294-301` — one ```` ```gherkin ```` block inside the REQ (`:294-537`); no `.feature` file, no runtime.

**Bad** (real)
~~~~text
```
AC-1  Given A has no prod version (current_version = 0)
      When  each prod path is exercised
      Then  it is blocked as the row says; no tool executes for real; a WARN records
            agentId + traceId + code=agent-not-verified

~~~~
`docs/spec/REQ-075-certification-execution-gate.md:699-704` — Given/When/Then as prose in an untyped fence (a path table follows at `:705-712`); not Gherkin, Outline/Examples not expressible. 32 of 33 REQs with `## Acceptance criteria` have no gherkin block.

### GA2 — Every scenario has a stable analyst-assigned id (AC-1…), fixed once approved
**Good** (real)
~~~~text
```
AC-1  Given A has no prod version (current_version = 0)
      When  each prod path is exercised
      Then  it is blocked as the row says; no tool executes for real; a WARN records
~~~~
`docs/spec/REQ-075-certification-execution-gate.md:699-702` — `AC-1` is a stable handle the MR and tests can cite.

**Bad** (real)
```gherkin
@domain @security
Scenario: An interrupted write leaves no immortal counter
  Given the counter write is interrupted after the value is set and before any second call
  When the counter is read
  Then it either does not exist or has a positive time to live
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:303-307` — no id; the title is the only handle, so rewording the title breaks every reference (see GT1 drift).

### GA3 — Tags name the domain/concern, never the tier
**Good** (adapted from REQ-500:353-357)
```gherkin
@security @auth
Scenario: An attacker cannot keep a real user out
```
— concern tags only; the developer picks IT vs smoke by S1.

**Bad** (real)
```gherkin
# D3 — the denial of service this REQ removes
@api @security
Scenario: An attacker cannot keep a real user out
  Given an attacker has failed against victim@example.com enough times to reach the account cap
  When the real owner of victim@example.com submits correct credentials after the cap has elapsed
  Then the login succeeds
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:352-357` — `@api` pre-decides the tier; REQ-500 carries 24 tier tags (`@domain`/`@api`), every scenario has one.

### GA4 — Examples header names exactly the <placeholders>; shared preconditions once as Background
**Good** (real)
```gherkin
Scenario Outline: The effective backoff is the larger of the two
  Given an account backoff of <account> seconds and a source backoff of <source> seconds
  When the effective backoff is resolved
  Then it is <effective> seconds

  Examples:
    | account | source | effective |
    | 0       | 0      | 0         |
    | 4       | 0      | 4         |
    | 0       | 8      | 8         |
    | 4       | 8      | 8         |
    | 8       | 4      | 8         |
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:339-350`
```text
Shared setup, unless a criterion says otherwise:
- There is an agent A in workspace W, and a `WORKSPACE_OWNER` of W.
- A has a complete version **v-verified** with status `VERIFIED`.
- A's draft carries later edits, saved as a newer complete version **v-draft**, status `DRAFT`.
```
`docs/spec/REQ-075-certification-execution-gate.md:692-695` — header `account | source | effective` equals the three placeholders; REQ-075 writes the shared preconditions once (as "Shared setup", the prose form of `Background:`).

**Bad** (adapted from REQ-500:376-386)
```gherkin
Scenario Outline: The source key tolerates far more failures than the account key before it triggers
  Given <failures> consecutive failures from one address, spread across different accounts
  Then the source backoff is <backoff>
  Examples:
    | count | wait |
    | 99    | 0    |
```
— header names no placeholder; with no Gherkin parser (GA1) nothing catches it. No real mismatch found on master (all 11 REQ-500 Outlines match).

### GA5 — One checkable Then per scenario; every AC has a failure/refusal scenario
**Good** (real)
```gherkin
@domain @security
Scenario Outline: Every throttle call fails open when Redis is unreachable
  Given Redis is unreachable
  When <operation> is called
  Then it does not throw
  And the caller is treated as not throttled

  Examples:
    | operation                |
    | recording a failure      |
    | resolving the backoff    |
    | clearing on success      |
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:428-439` — the unavailable-Redis path, with Thens a test can observe (no throw, not throttled).

**Bad** (real)
```gherkin
@api @security
Scenario Outline: A dead lockout path no longer exists
  Given the login endpoint
  When <condition>
  Then no AuthLockedException path is reachable

  Examples:
    | condition                          |
    | credentials are wrong              |
    | the caller is already throttled    |
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:394-403` — "no AuthLockedException path is reachable" is a claim about code structure, not an observable outcome of one attempt; no test can check it by running the scenario.

## Scenario → tests — testing/workflows/scenario-to-tests.md

### GT1 — Test name is the scenario title verbatim (Outline adds " — #placeholder")
**Good** (real, near-verbatim)
```gherkin
Scenario: A counter that has expired starts again from zero
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:455-455`
```groovy
    def "a counter that has expired starts again from zero"() {
```
`aruvii-api/src/integrationTest/groovy/ai/aruvii/api/security/LoginThrottleServiceIT.groovy:178-178` — same sentence (only the initial capital differs), so `grep -iF` of the title finds the test. 1 of 9 REQ-500 titles sampled matched a test name.

**Bad** (real)
```gherkin
Scenario Outline: The backoff is zero below the threshold, then grows, then stops at the cap
```
`docs/spec/REQ-500-login-throttle-progressive-delay.md:311-311`
```groovy
    def "the account backoff is zero below the threshold, then doubles to the cap"() {
```
`aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:25-25` — "then grows, then stops at the cap" reworded to "then doubles to the cap"; a title search finds nothing.

### GT2 — Spock block texts repeat the Given/When/Then; Playwright one test.step per step
**Good** (adapted from 25-gherkin-to-every-tier.md §3 over REQ-500:455-458, NEEDS COMPILE CHECK)
```groovy
def "A counter that has expired starts again from zero"() {
    given: "a caller whose failure counter has expired"
    def human = humanSpeedThrottle()
    def email = uniqueEmail()
    12.times { i -> human.recordFailure(email, uniqueAddress(), WRONG + i) }
    redis.delete([accountKey(email), accountKey(email) + ":meta"])

    when: "a failed attempt is recorded"
    human.recordFailure(email, uniqueAddress(), WRONG)

    then: "the backoff is that of a first failure"
    human.backoffFor(email, uniqueAddress()) instanceof BackoffDecision.Allowed
}
```
— each block label is the scenario step word for word.

**Bad** (real)
```groovy
    def "D4 — a counter can never exist without an expiry"() {
        given: "an account nobody has failed against"
        def email = uniqueEmail()

        when: "one failure is recorded"
        throttle.recordFailure(email, IP, WRONG)

        then: "a key at TTL -1 is the immortal counter this REQ exists to prevent"
        redis.getExpire(accountKey(email)) > 0
    }
```
`aruvii-api/src/integrationTest/groovy/ai/aruvii/api/security/LoginThrottleServiceIT.groovy:56-65` — block texts ("an account nobody has failed against", "a key at TTL -1 is…") paraphrase REQ-500:298-301 instead of repeating it. Playwright side: 0 `test.step` in 94 smoke specs.

### GT3 — Outline → Spock where: / test.each with Examples columns unchanged; e2e one row
**Good** (adapted from LoginBackoffPolicySpec:25-41 over REQ-500:311-327, NEEDS COMPILE CHECK)
```groovy
def "The backoff is zero below the threshold, then grows, then stops at the cap — #failures failures"() {
    expect:
    secondsOf(decide(failures, 0)) == backoff

    where:
    failures || backoff
    0        || 0
    10       || 1
    15       || 30
    400      || 30
}
```
— `failures | backoff` exactly as the Examples header (rows abridged here; real spec keeps all ten).

**Bad** (real)
```groovy
        where:
        failures || expected
        0        || 0
        9        || 0
        10       || 1
```
`aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:29-33` — column `backoff` renamed `expected`. Worse at `:52-58`: REQ-500:345 columns are seconds (`account | source | effective`) but the spec feeds failure counts (`accountFailures | sourceFailures`) with different rows.

### GT4 — Each scenario test carries @Issue("#NNN") / Playwright issue annotation + AC id
**Good** (adapted from 25-gherkin-to-every-tier.md §3, NEEDS COMPILE CHECK)
```groovy
@Issue("#500")
def "A counter that has expired starts again from zero"() {
```
```ts
test('An attacker cannot keep a real user out',
  { tag: ['@auth'], annotation: { type: 'issue', description: '#500 · AC-n' } }, async ({ page }) => {
```
— machine-readable link to the work item and scenario id. 0 `@Issue` in 190 Spock files and 0 `issue` annotations on master.

**Bad** (real)
```groovy
/**
 * REQ-500 §Acceptance criteria. Every figure asserted here is D7's, and D7 cites where each one
 * comes from — the two marked derived there are the two to revisit, not the five that are Keycloak's
 * or NIST's.
 *
 * <p>The curve tables run against settings whose spread is zero. The spread is a separate property
 * with its own features below, and folding it into the tables would turn D7's cited figures into
 * numbers only this file can explain.
 */
class LoginBackoffPolicySpec extends Specification {
```
`aruvii-shared/src/test/groovy/ai/aruvii/shared/security/LoginBackoffPolicySpec.groovy:8-17` — traceability only as free javadoc text ("REQ-500 §Acceptance criteria"); no work-item number, no scenario id.

### GT5 — One owning tier per scenario by S1; second tier only for a risk the first cannot see
**Good** (real)
```java
    @Test
    @DisplayName("POST /api/auth/login — the real owner gets back in once the wait is served")
    void shouldLetTheOwnerBackInAfterTheWaitHasElapsed() {
        // given — at the threshold, with the wait already served
        seedFailuresAt(settings.get().accountThreshold());
        seedLastFailureAt(Duration.ofMinutes(1));

        // when / then — an attacker who knows an email must not be able to hold its owner out
        attemptLogin(PASSWORD).expectStatus().isOk();
        assertThat(redis.hasKey("auth:fail:account:" + EMAIL)).isFalse();
    }
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/security/LoginThrottleIT.java:130-140` — REQ-500:354 (HTTP + Redis) owned by one IT; no smoke replays it (no login-throttle smoke spec on master).

**Bad** (real, judgement)
```groovy
    def "D1 — no number of failures produces an unbounded wait"() {
        given: "one account, each failure from a fresh address so only its own counter grows"
        def human = humanSpeedThrottle()
        def email = uniqueEmail()
        200.times { i -> human.recordFailure(email, uniqueAddress(), WRONG + i) }

        expect: "an attacker driving a victim's key costs them the cap, never their account"
        secondsOf(human.backoffFor(email, uniqueAddress())) <= ceilingOf(settings.get().accountCapSeconds())
    }
```
`aruvii-api/src/integrationTest/groovy/ai/aruvii/api/security/LoginThrottleServiceIT.groovy:67-75` — REQ-500:331 (D1) already owned by unit `LoginBackoffPolicySpec.groovy:43-46`; the IT re-asserts the cap and names no risk the unit cannot see (real-Redis counter growth is arguable — reviewer call).

### GT6 — MR lists every AC-id → tier → test file:line; unlisted = "not done"
**Good** (adapted from crq.md stage 8 + 25-gherkin-to-every-tier.md §4)
```markdown
| AC | scenario | tier | test |
|---|---|---|---|
| AC-3 | The backoff is zero below the threshold… | unit | LoginBackoffPolicySpec.groovy:25 |
| AC-7 | An attacker cannot keep a real user out | IT | LoginThrottleIT.java:131 |
| AC-9 | A dead lockout path no longer exists | — | not done |
```
— every scenario has a row; a missing test is visible as "not done". (AC ids illustrative: REQ-500 has none, see GA2.)

**Bad** (real)
```text
- Take each acceptance criterion from the REQ written at stage 3 — or from the **issue body**, where
  the change has no REQ.
- For each one, find the code that satisfies it and **cite `file:line`**. Not the test that covers
  it; the code that does it.
- A criterion you cannot cite is **not met**. Say which, and either implement it or say plainly on
  the MR why it is out of scope for this change.
```
`.claude/commands/crq.md:388-393` — stage 8 cites code per criterion and says "Not the test that covers it"; no scenario → test mapping, and `.gitlab/merge_request_templates/Default.md:1-16` has no AC table.

---

## Tally

| | real | adapted | n/a |
|---|---|---|---|
| Good (29) | 20 | 9 | 0 |
| Bad (29) | 17 | 9 | 3 (M1, P2, P7) |
| **all 58** | **37** | **18** | **3** |

**No real Good on master (9):** M3 (no committed report) · M8 (no equivalence claim anywhere) · M10 (no hand-mutation record) · P3 (harness has no branch counting) · GA3 (every REQ-500 scenario has a tier tag) · GT2 (no verbatim block texts, 0 `test.step`) · GT3 (only Outline mirror renames columns) · GT4 (0 `@Issue`) · GT6 (no AC→test table). Partial real Goods: M2 (no letter named), P10 (home-grown harness, not fast-check), GT1 (case differs).

**Widely broken on master:**

| rule | count |
|---|---|
| GA1 gherkin block | 32 of 33 REQs with `## Acceptance criteria` have none (only REQ-500) |
| GA2 stable AC ids | only 11 spec files carry a line-leading `AC-n` id (33 REQs have an AC section) |
| GA3 tier tags | 24 tier tags in REQ-500 (every scenario) |
| GT1 title verbatim | 1 of 9 sampled REQ-500 titles match a test name |
| GT2 `test.step` | 0 in 94 smoke specs |
| GT4 `@Issue` / issue annotation | 0 of 190 Spock files; 0 Playwright |
| P4 / P10 random seed | the one UI property spec runs on fixed `0x5eed` |

**Contradictions to settle:** P10 says fast-check, P5/master use home-grown harnesses · `.claude/commands/crq.md:390-391` "Not the test" vs GT6 test file:line · `gherkin-to-test/SKILL.md:66-71` contradicts M7 · `gherkin-to-test/SKILL.md:61` names `PiiRedactorTest` as a runner user (false, per 21-mutation-and-property.md).
