# Comments

Which comments, doc comments and lint suppressions may stay in code. Read it when you write or review a comment, a
Javadoc block or a suppression, in any file type.

Contents: Rules · When X, use Y · Good / Bad (CM3, CM4, CM7) · Decided edges · Review checks

## Rules

- **CM1** — Write no banner or divider comments, in any file type, because a divider stays after the section it
  labelled is split or moved.
- **CM2** — Write no comment that restates the code, a dependency or a config value, because a restating comment adds
  nothing and is a second place to update, which goes stale once the code changes.
- **CM3** — Keep a comment only for what code cannot show (external dependency or protocol, public-API contract,
  license, issue/RFC link, must-not-fail boundary catch (ER4)); else reshape, because a why-comment about our code
  rots into a false claim.
- **CM4** (operator preference, 2026-10-31) — Check each comment's claim before it lands; replace a 'do not remove' note
  with a type, test or lint, because a false comment gets believed and a 'keep in sync' note never fails.
- **CM5** (operator preference, 2026-10-31) — Write Javadoc on an interface only when its contract is not obvious from
  the signature, and none on its implementation, because Javadoc on the implementation is a second copy that goes stale.
- **CM7** — Fix the type instead of suppressing a lint or compiler rule that protects correctness or safety
  (`eslint-disable`, `@ts-expect-error`, `@SuppressWarnings`); style-only rules may be suppressed, because a suppressed
  correctness rule stops catching the bugs it targets.

## When X, use Y

| the comment is | use | why |
|---|---|---|
| a banner or divider | delete it (CM1) | banners are on the kill list (sicko :12) |
| narration of what the code, a dependency or a config value does | delete it (CM2) | narration is on the kill list (sicko :12); a comment that explains "what" goes (simplification :144) |
| a legal or license header | keep it (CM3) | sicko :16 |
| behaviour forced by an external dependency, platform, vendor or protocol | keep it (CM3) | sicko :17 |
| a surprise in our own code | delete it; rename, extract or type the symbol until the behaviour is obvious (CM3) | sicko :17 |
| a doc comment that defines a public API contract | keep it when the signature does not show the contract (CM3, CM5) | sicko :19; an interface is also its invariants, ordering constraints and error modes (codebase-design :16) |
| an issue or RFC link for a constraint the code cannot express | keep it (CM3) | sicko :20 |
| a constraint note: `do not remove`, `do not change wording`, `talk to X before changing` | check the claim; encode it as a type, test or lint, then delete it (CM4) | sicko :26; no-comments :23 |
| a lint or compiler suppression | fix the type when the rule protects correctness or safety; keep it when the rule is style-only (CM7) | sicko :18, :24 |

`sicko` is pstack `agents/comment-sicko.md`, `no-comments` is pstack `skills/no-comments/SKILL.md`, `simplification`
is addy `skills/code-simplification/SKILL.md` and `codebase-design` is mattpocock
`skills/engineering/codebase-design/SKILL.md`; `:N` is the line.

## Good / Bad

### CM3 — A comment survives only for a constraint the code cannot show

**Bad** (neutral)
```java
// Metric: payment.charge.duration tagged by method + status. Bounded cardinality —
// payment methods are an enum, statuses are a small fixed set. Operators get a graph
// of "is the gateway getting slower?" and "is the PAID rate dropping?"
try {
    meters.timer("payment.charge.duration",
        "method", method,
        "status", status.toString())
        .record(latency);
} catch (RuntimeException meterFailure) {
    log.warn(
            "action=payment.charge.metric_failed cause={} message={}",
            meterFailure.getClass().getSimpleName(),
            meterFailure.getMessage());
}
```
The comment defends our own tag choice instead of the code showing it, and it is false: `method` is a `String`.

**Good** (neutral)
```java
private void recordChargeDuration(
        final PaymentMethod method,
        final ChargeStatus status,
        final Duration latency) {
    try {
        meters.timer("payment.charge.duration", "method", method.name(), "status", status.name())
                .record(latency);
    } catch (final RuntimeException meterFailure) {
        log.warn(
                "action=payment.charge.metric_failed method={} cause={} message={}",
                method,
                meterFailure.getClass().getSimpleName(),
                meterFailure.getMessage());
    }
}
```
Two enum parameters now show the bounded cardinality, so the comment has nothing left to say. Operator questions
belong in the metrics docs. (Real evidence: ledger row CM3.)

### CM4 — Check a comment's claim; encode a constraint note

**Bad** (neutral)
```java
// Mandatory anti-buffering headers — without these, nginx + corporate proxies stall
// SSE responses for 30s+ at a time. Stays in sync with docs/architecture.md §Streaming.
response.setHeader("Cache-Control",     "no-cache, no-transform");
response.setHeader("X-Accel-Buffering", "no");
```
The doc section holds no header text, so the claim is false. The same two headers are hand-copied into two other
stream endpoints.

**Good** (neutral)
```java
final class SseHeaders {
    private SseHeaders() {
    }

    // nginx and corporate proxies hold text/event-stream frames unless these two headers are set
    static void disableProxyBuffering(final HttpServletResponse response) {
        response.setHeader(HttpHeaders.CACHE_CONTROL, "no-cache, no-transform");
        response.setHeader("X-Accel-Buffering", "no");
    }
}
```
```groovy
def "should tell proxies not to buffer the order event stream"() {
    given: "a response for an order event stream, before any frame is written"
    def response = new MockHttpServletResponse()
    when: "the endpoint prepares the stream"
    SseHeaders.disableProxyBuffering(response)
    then: "nginx and caching proxies pass each frame on at once instead of holding it"
    response.getHeader("X-Accel-Buffering") == "no"
    response.getHeader(HttpHeaders.CACHE_CONTROL) == "no-cache, no-transform"
}
```
Every stream endpoint calls one helper and a spec pins the headers, so the sync note goes. The proxy sentence stays:
it is an outside constraint. (Real evidence: ledger row CM4.)

### CM7 — Fix the type instead of suppressing a correctness rule

**Bad** (neutral)
```ts
interface ConfirmEntry {
  id: string;
  options: ConfirmOptions;
  mode: 'confirm' | 'prompt';
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  resolve: (value: any) => void;
}
// … "Pay invoice" asks before charging …
ask(options: ConfirmOptions): Promise<boolean> {
  return this.enqueue(options, 'confirm') as Promise<boolean>;
}
```
Silencing `no-explicit-any` lets `accept()` hand a string to the "Pay invoice" confirm, and the cast hides it.

**Good** (neutral)
```ts
type ConfirmEntry =
  | { id: string; options: ConfirmOptions; mode: 'confirm'; resolve: (accepted: boolean) => void }
  | { id: string; options: ConfirmOptions; mode: 'prompt'; resolve: (input: string | null) => void };

ask(options: ConfirmOptions): Promise<boolean> {
  return new Promise((resolve) => this.enqueue({ id: newId(), options, mode: 'confirm', resolve }));
}

accept(inputValue = ''): void {
  const entry = this._current();
  if (entry?.mode === 'confirm') entry.resolve(true);
  if (entry?.mode === 'prompt') entry.resolve(inputValue);
  this._current.set(this.queue.shift() ?? null);
}
```
The union ties each `mode` to its `resolve` type, so the suppression and the cast go. (Real evidence: ledger row
CM7.)

## Decided edges

- **Skip when** the comment fits a keep clause of CM3 that is proven true today on a live path (sicko :26). — **Do not
  skip when** you are not sure a keep clause applies: the comment goes (sicko :22). — **Confidence** high
- **Skip when** the why names a constraint the code cannot show (CM3). — **Do not skip when** the why is about our own
  code, even though addy keeps such comments (simplification :145): delete it and ask for a reshape (operator
  preference, 2026-10-31). — **Confidence** high
- **Skip when** a member's contract is obvious from its signature: write no Javadoc (Google Java Style §7.3.1 makes it
  optional for a simple, obvious member, and §7.3.2 for an override). — **Do not skip when** the interface has an
  invariant, ordering constraint or error mode the signature cannot show (codebase-design :16). — **Confidence** high
- **Skip when** the suppression is a Java unchecked cast: TY10 (`types.md`) owns that one exception to CM7. — **Do not
  skip when** the rule is `no-explicit-any` or another correctness rule: fix the type (NGA2, `angular-ui.md`;
  typescript-eslint `ban-ts-comment`). — **Confidence** high

## Review checks

Walk every comment, Javadoc block and suppression that the change adds or edits, in every file type. CM6 is a
review check only, not an author rule.

- [ ] CM1 — A banner or divider comment is a finding.
- [ ] CM2 — A comment that restates the code next to it, a dependency or a config value is a finding.
- [ ] CM3 — Each kept comment fits one keep clause: an external dependency or protocol, a public-API contract, a
  license, an issue/RFC link, or a must-not-fail boundary catch (ER4). A comment that fits none is a finding; name the symbol to rename, extract or type.
- [ ] CM4 — Check each factual claim against the code or the source it names. A false claim is a finding, and so is a
  constraint note ('do not remove', 'talk to X first', 'keep in sync') that no type, test or lint enforces.
- [ ] CM5 — Javadoc on an implementation of an interface is a finding, and so is interface Javadoc that only repeats
  the signature.
- [ ] CM7 — For each suppression (`grep -nE "eslint-disable|@ts-expect-error|@ts-ignore|@SuppressWarnings"`), look up
  the rule. A suppressed rule that protects correctness or safety is a finding.
- [ ] CM6 — A long justification comment is a finding: ask for a reshape or a keep-clause reason (CM3), because a long
  justification usually defends a branch that should be deleted.
