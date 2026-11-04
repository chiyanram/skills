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
| a banner or divider | delete it (CM1) | a divider outlives the section it labelled once code moves |
| a restatement of the code, a name or a config value | delete it; rename instead (CM2) | it adds nothing and goes stale when the code changes |
| commented-out code | delete it (CMN1) | it is never compiled, goes stale, and version control already keeps it |
| prose a rename, an extracted method or a type could replace | the rename, method or type, then no comment (CM3) | prose that duplicates code goes stale |
| a non-obvious reason, outside constraint, contract, license or link | keep it (CM3) | it carries what the code cannot say |
| a factual claim | check it against the code; fix or delete it if false (CM4) | readers act on a false comment |
| a public interface method | a doc comment on its contract: nulls, errors, side effects (CM5) | a caller needs what the signature cannot say |
| a simple, obvious member or an override | no doc comment (CM5) | a copied doc drifts from the original |
| a lint or compiler suppression | the code fixed; a proven-safe one scoped to one declaration, with a comment saying why (CM7) | a bare suppression hides the next real bug |

## Good / Bad

### CM3 — Try a rename, a method or a type before a comment

**Bad**
```java
// The carrier label API accepts a weight with at most one decimal place.
final BigDecimal labelWeight = parcel.weightKg().setScale(1, RoundingMode.HALF_UP);
// We check the flag because the printer must not print a second label for the same parcel.
if (parcel.stage() == ParcelStage.LEFT_DEPOT && !parcel.labelPrinted()) {
    printer.print(parcel.id(), labelWeight);
    parcel.setLabelPrinted(true);
}
```
The second comment explains our own code: a loose flag needs it, where a method could own the guard.

**Good**
```java
// The carrier label API accepts a weight with at most one decimal place.
final BigDecimal labelWeight = parcel.weightKg().setScale(1, RoundingMode.HALF_UP);
parcel.labelDue(labelWeight).ifPresent(labels::print);
```
`labelDue` owns the guard (left the depot, no label yet) and does no I/O (SEAM1, `design.md`), so the second comment
goes. The first comment stays: it names a constraint of an outside API.

### CM4 — Check a comment's claim before it lands

**Bad**
```java
// Do not change this text: the mobile app parses it.
static final String PARCEL_LOST = "Parcel lost in transit";

record ParcelEventResponse(
        ParcelEventCode code,
        String message) {
}
```
The app matches on `code`, not on the text, so the claim is false. A reader who believes it freezes a message that is
free to change.

**Good**
```java
static final String PARCEL_LOST = "Parcel lost in transit";

record ParcelEventResponse(
        ParcelEventCode code,
        String message) {
}
```
The claim was checked in the app, which matches on `code`. It is false, so the note goes and the text is free to
change.

### CM7 — Fix the code instead of suppressing a correctness warning

**Bad**
```ts
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function trackingNumber(payload: any): string {
  return payload.shipment.trackingNumber;
}
```
The suppression turns off the check on each property access. A payload without `shipment` throws at run time.

**Good**
```ts
interface CarrierPayload {
  shipment: { trackingNumber: string };
}

function isCarrierPayload(value: unknown): value is CarrierPayload {
  if (typeof value !== 'object' || value === null || !('shipment' in value)) return false;
  const shipment = value.shipment;
  return typeof shipment === 'object' && shipment !== null && 'trackingNumber' in shipment
    && typeof shipment.trackingNumber === 'string';
}

function trackingNumber(payload: unknown): string | undefined {
  return isCarrierPayload(payload) ? payload.shipment.trackingNumber : undefined;
}
```
`unknown` and a type guard let the compiler check each access, so the suppression goes.

## Decided edges

- **Skip when** the suppression is a Java unchecked cast proven safe: TY10 (`types.md`) sets its form, on the smallest
  declaration with a comment saying why. — **Do not skip when** the warning is TypeScript `no-explicit-any`: type the
  value `unknown` and narrow it instead (NGA2, `angular-ui.md`). — **Confidence** high

## Review checks

Walk every comment, Javadoc block and suppression that the change adds or edits, in every file type.

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
