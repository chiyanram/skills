# Comments

Which comments, doc comments and lint suppressions may stay in code. Read it when you write or review a comment, a
Javadoc block or a suppression, in any file type.

Contents: Rules · When X, use Y · Good / Bad (CM3, CM4, CM7) · Decided edges · Review checks

## Rules

- **CM1** — Write no banner or divider comments (`// ====`, `// --- Helpers ---`), because a divider outlives the
  section it labelled once code moves; use a new method or file instead.
- **CM2** — Write no comment that restates the code, a name or a config value, because it adds nothing and goes stale
  when the code changes; rename instead.
- **CMN1** — Delete commented-out code, because it is never compiled, goes stale, and version control already keeps
  it.
- **CM3** — Try a rename, extracted method or type first; keep a comment only for what code cannot say (non-obvious
  reason, outside constraint, contract, license, link), because prose duplicating code goes stale.
- **CM4** — Check a comment's factual claim against the code before it lands, and delete or fix any that is false,
  because readers act on a false comment.
- **CM5** — Document a public interface method's contract (what the signature cannot say: nulls, errors, side
  effects); skip it for a self-explanatory member, and write none on an override, because a copied doc drifts from
  the original.
- **CM7** — Fix the code rather than suppress a compiler or lint warning that guards correctness; scope a proven-safe
  suppression to one declaration, with a comment saying why, because a bare suppression hides the next real bug.

## When X, use Y

| the comment is | use | why |
|---|---|---|
| a banner or divider | delete it (CM1) | avoid positional markers; let names and formatting give the structure (clean-code-javascript, r48 :301); banners are on the kill list (pstack `comment-sicko` :12, r48 :301) |
| a restatement of the code, a name or a config value | delete it; rename instead (CM2) | delete a comment that explains "what" (addy `code-simplification` :144, r48 :306); a first sentence redundant with the name could be deleted (Martin and Ousterhout, aposd-vs-clean-code, r48 :306) |
| commented-out code | delete it (CMN1) | don't leave commented-out code in your codebase (clean-code-javascript, r48 :338); commented-out blocks: remove (addy `code-simplification` :152, r48 :338); also Sonar S125 (r48 :338) |
| prose a rename, an extracted method or a type could replace | the rename, method or type, then no comment (CM3) | implementation code only needs comments when the code is nonobvious (Ousterhout and Martin, aposd-vs-clean-code, r48 :312) |
| a non-obvious reason, outside constraint, contract, license or link | keep it (CM3) | keep "why" comments: they carry intent the code can't express (addy `code-simplification` :145, r48 :312); a comment is for important information not obvious from the code (Ousterhout, r48 :312) |
| a factual claim | check it against the code; fix or delete it if false (CM4) | every comment is potential misinformation (Martin, aposd-vs-clean-code, r48 :319); run `/how` or `/why` on the named symbol when the claim is not obvious (pstack `comment-sicko` :26, r48 :319) |
| a public interface method | a doc comment on its contract: nulls, errors, side effects (CM5) | a header comment describes the method's interface, all a caller needs (Ousterhout, r48 :326); doc comments that define a public API contract survive (pstack `comment-sicko` :19, r48 :326) |
| a simple, obvious member or an override | no doc comment (CM5) | Javadoc is optional for simple, obvious members and not always present on an override (Google Java Style §7.3.1, §7.3.2, r48 :326) |
| a lint or compiler suppression | the code fixed; a proven-safe one scoped to one declaration, with a comment saying why (CM7) | eliminate warnings; when the code is proven safe, suppress and comment on why it is safe (Effective Java Item 27, r48 :333); a suppression needs a comment explaining why the warning is safe to ignore (Error Prone `SuppressWarningsWithoutExplanation`, r48 :196) |

`r48 :N` is the line in agent-factory `research/48-industry-recheck-code.md` that quotes the source, read at the
commit it names.

## Good / Bad

### CM3 — Try a rename, method or type before a comment

**Bad** (neutral)
```java
// Bounded cardinality: method and status each take only a few fixed values.
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
The comment says what a type could show. `method` is a `String`, so nothing stops an unbounded tag value.

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
Two enum parameters now show the bounded cardinality, so the comment has nothing left to say. (Real evidence: ledger
row CM3.)

### CM4 — Check a comment's factual claim

**Bad** (neutral)
```java
// Mandatory anti-buffering headers — without these, nginx + corporate proxies stall
// SSE responses for 30s+ at a time. Stays in sync with docs/architecture.md §Streaming.
response.setHeader("Cache-Control",     "no-cache, no-transform");
response.setHeader("X-Accel-Buffering", "no");
```
The doc section holds no header text, so the sync claim is false.

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
The false sync claim goes. The proxy sentence stays, because it states an outside constraint. One helper and a spec
keep the headers in one place. (Real evidence: ledger row CM4.)

### CM7 — Fix the code instead of suppressing a correctness warning

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
The suppression has no proof and no reason. Silencing `no-explicit-any` lets `accept()` hand a string to the "Pay
invoice" confirm, and the cast hides it.

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

- **Skip when** the suppression is a Java unchecked cast proven safe: TY10 (`types.md`) sets its form, on the smallest
  declaration with a comment saying why (Effective Java Item 27, r48 :196). — **Do not skip when** the warning is
  TypeScript `no-explicit-any`: type the value `unknown` and narrow it instead (NGA2, `angular-ui.md`;
  typescript-eslint `no-explicit-any`, r48 :1253). — **Confidence** high

## Review checks

Walk every comment, Javadoc block and suppression that the change adds or edits, in every file type. CM6 is a
review check only, not an author rule.

- [ ] CM1 — A banner or divider comment (`grep -nE "(//|#|/\*|<!--) *([=*#-]){4,}|(//|#) *-{2,} .+ -{2,}"`) is a
  finding.
- [ ] CM2 — A comment that restates the code next to it, a name or a config value is a finding.
- [ ] CMN1 — Commented-out code (`grep -nE "^\s*(//|#).*[;{}]\s*$"`) is a finding.
- [ ] CM3 — For each kept comment, ask whether a rename, an extracted method or a type could say it. One that could is
  a finding; name the symbol. One that states a non-obvious reason, an outside constraint, a contract, a license or a
  link stays.
- [ ] CM4 — Check each factual claim against the code or the source it names. A false claim is a finding.
- [ ] CM5 — A public interface method whose contract (nulls, errors, side effects) the signature cannot say, with no
  doc comment stating it, is a finding. A doc comment on an override, or one that only repeats the signature, is a
  finding.
- [ ] CM7 — For each suppression (`grep -nE "eslint-disable|@ts-expect-error|@ts-ignore|@SuppressWarnings|NOSONAR"`),
  look up the rule. A suppressed correctness warning the code could fix is a finding, and so is a suppression wider
  than one declaration or with no comment saying why.
- [ ] CM6 — A long justification comment is a finding: ask for a reshape or the reason the code cannot say (CM3),
  because a long justification usually defends a branch that should be deleted.
