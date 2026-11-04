# Conventions raised by the v2 rewrite (proposed, need the operator's yes)

### CV1 — AC id in Gherkin is a `# AC-n` comment line above `Scenario:`
**Good** (adapted from docs/spec/REQ-500-login-throttle-progressive-delay.md:303-307)
```gherkin
# AC-3
@security
Scenario: should refuse a sign-in once the account backoff has not elapsed
  Given an account with 5 failed attempts in the last minute
  When the owner signs in with the right password
  Then the sign-in is refused with a retry-after
```
`proposed` — a tag would clash with GA3 (tags name concerns only); the title must equal the test name (GT1), so the id cannot live there.
**Bad** (adapted)
```gherkin
@AC-3 @security
Scenario: AC-3 should refuse a sign-in once the account backoff has not elapsed
```
`proposed` — id as a tag breaks GA3; id in the title breaks GT1 (test name = title verbatim).

### CV2 — A Spock test names its work item and AC with `@Issue(["#NNN", "AC-n"])`
**Good** (adapted)
```groovy
@Issue(["#500", "AC-3"])
def "should refuse a sign-in once the account backoff has not elapsed"() {
```
`proposed` — one annotation carries both links; grep `"AC-3"` finds the test (GT4, GT6).
**Bad** (adapted)
```groovy
// AC-3 of #500
def "should refuse a sign-in once the account backoff has not elapsed"() {
```
`proposed` — a comment is not reported by Spock and is easy to drift from.

### CV3 — Wrapping: ST2 applies to Java/Groovy (120, .editorconfig); TypeScript follows Prettier (110, .prettierrc.json)
**Good** (adapted)
```ts
await expect(
  page.getByRole('row', { name: agentName }),
).toBeVisible();
```
`aruvii-ui/.prettierrc.json` — Prettier's own output; ST2's "closing paren on the last argument" would fight the formatter.
**Bad** (n/a) — no example needed; the conflict is between two rules, not in code.

### CV4 — Property tests written in Spock use an explicit `assert` inside the `Property.forAll` closure
**Good** (adapted from aruvii-guardrails ToolOutputSanitizerPropertyTest)
```groovy
Property.forAll(Gen.toolOutput()) { output ->
    def sanitized = sanitizer.sanitize(output)
    assert !sanitized.contains("\u0000")
}
```
`proposed` — Spock's implicit assertions (K1) apply only to its own interaction closures; inside our harness's closure a bare expression checks nothing.
**Bad** (adapted)
```groovy
Property.forAll(Gen.toolOutput()) { output ->
    !sanitizer.sanitize(output).contains("\u0000")
}
```
`proposed` — the boolean is discarded; the property always passes.

### CV5 — IT2 has one documented exception: `SetupControllerIT` may start its own container (it needs a pristine, un-seeded database)
**Good** (real)
```java
@Testcontainers
class SetupControllerIT {
    @Container
    static final PostgreSQLContainer<?> POSTGRES = ...
```
`aruvii-api/src/integrationTest/java/.../SetupControllerIT.java:45-60` — documented in its own javadoc (:34); the setup wizard only runs on an empty database, which the shared seeded singleton cannot provide.
**Bad** (n/a) — any other IT doing this breaks IT2.

### CV6 — U2 wording: names are plain sentences that START with "should …" (U2a supersedes U2's "not shouldXxx")
**Good** (adapted)
```groovy
def "should refuse an agent that was never verified"() {
```
`proposed` — sentence + "should" prefix; camelCase (`shouldRefuseUnverifiedAgent`) stays wrong in Spock.
**Bad** (real pattern)
```groovy
def shouldRefuseUnverifiedAgent() {
```
`proposed` — camelCase feature name.
