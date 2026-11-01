# Smells — Good / Bad examples

Every approved Good/Bad pair for the smells rules, one per rule that can be misread. The rules, the baseline and the
review checks are in [`../smells.md`](../smells.md). Each pair is in one neutral domain (orders, invoices and
payments). The other rules state themselves and have no pair.

Contents: DS1 · DS3 · DS4 · DS12 · DS14

### DS1 — Delete the branch, do not move it

**Bad** (neutral)
```java
// OverdueReminder.java — the job decodes the sentinel …
final int graceDays = resolveGraceDays(customer.graceDays(), defaultGraceDays);
if (graceDays == 0) {
    log.debug("overdue_reminder customerId={} never_overdue — skipped", customer.id());
    continue;
}
Instant cutoff = Instant.now(clock).minus(graceDays, ChronoUnit.DAYS);
// InvoicePreviewController.java — … and the preview decodes it again
int graceDays = resolveGraceDays(customer.graceDays(), defaultGraceDays);
if (graceDays == 0) {
    return new OverduePreview(customer.id(), 0, null, 0L);
}
Instant cutoff = Instant.now(clock).minus(graceDays, ChronoUnit.DAYS);
```
The "0 means never overdue" rule and the cutoff arithmetic are written twice, so the preview can disagree with the job.

**Good** (neutral)
```java
public sealed interface GracePeriod {
    record NeverOverdue() implements GracePeriod {}
    record Days(int count) implements GracePeriod {}   // compact ctor rejects count <= 0, unchanged

    default Optional<Instant> overdueBefore(final Instant now) {
        return switch (this) {
            case NeverOverdue _ -> Optional.empty();
            case Days days -> Optional.of(now.minus(days.count(), ChronoUnit.DAYS));
        };
    }
}
// job:     period.overdueBefore(clock.instant()).ifPresent(cutoff -> remind(customer.id(), cutoff));
// preview: final long invoiceCount = period.overdueBefore(clock.instant())
//                  .map(cutoff -> invoiceRepository.countOpenDueBefore(customer.id(), cutoff))
//                  .orElse(0L);
```
The cutoff rule lives on the type, so both callers lose their branch instead of each switching on it. (Real evidence:
ledger row DS1. Pair: 68f § DS1 — Look for a restructure that deletes branches, not one that moves them.)

### DS3 — Model the case; add no second boolean

**Bad** (neutral)
```java
private void recordPaymentSafely(PaymentIds ids, GatewayExchange exchange, PaymentStatus status,
                                 boolean requiresReview, UUID reviewId,
                                 boolean sandbox, String sandboxSource) {
```
Sandbox mode arrived as a boolean plus a string that means something only when it is true. Review repeats that shape.

**Good** (neutral)
```java
sealed interface GatewayRun {
    record Live() implements GatewayRun {}
    record Sandbox(SandboxSource source) implements GatewayRun {}
}

sealed interface ReviewGate {
    record NotRequired() implements ReviewGate {}
    record Required(UUID reviewId) implements ReviewGate {}
}

record PaymentAttempt(PaymentIds ids, PaymentMethod method, GatewayExchange exchange, PaymentStatus status,
                      ReviewGate review, GatewayRun run) {
}

private void recordPaymentAttempt(final PaymentAttempt attempt) {
```
Each mode is a sealed case that carries only its own data, so a sandbox source or a review id cannot exist without its
mode. (Real evidence: ledger row DS3. Pair: 68f § DS3 — No one-off `if` or second boolean in a flow; model the case.)

### DS4 — Remove the pass-through; apply the deletion test

**Bad** (neutral)
```java
public List<Invoice> findDueReminders() {
    return invoiceRepository.findDueReminders();
}

public boolean claimAndAdvance(UUID invoiceId, Instant expectedNextReminderAt, Instant newNextReminderAt) {
    return invoiceRepository.claimAndAdvance(invoiceId, expectedNextReminderAt, newNextReminderAt);
}
```
Two one-line forwards whose only caller is the reminder job add a layer to trace and hide nothing.

**Good** (neutral)
```java
@Component
class OverdueReminder {

    private final InvoiceRepository invoices;
    // … other collaborators unchanged

    ReminderOutcome remind(final Invoice invoice, final ClaimWindow window) {
        return switch (invoices.claimAndAdvance(invoice.id(), window)) {
            case ReminderClaim.Won _ -> send(invoice);
            case ReminderClaim.Lost _ -> ReminderOutcome.NOT_CLAIMED;
        };
    }
}
```
The job depends on the port that does the work. The forwards are deleted, and the claim returns a sealed `Won` or
`Lost`. (Real evidence: ledger row DS4. Pair: 68f § DS4 — Remove pass-throughs and single-caller wrappers; apply the
deletion test.)

### DS12 — Define the rule once, call it everywhere

**Bad** (neutral)
```ts
const smokeOrders = orders.filter(order => order.reference?.startsWith('smoke-') || order.reference?.startsWith('rate-limit-smoke-'));
const staleInvoices = invoices.filter(invoice => invoice.reference.startsWith('smoke-'));
const smoke = customers.filter(customer => (customer.email ?? '').startsWith('smoke-') || (customer.name ?? '').startsWith('smoke-'));
```
"What counts as smoke data" lives in three lambdas that already disagree, so numbered prefixes such as `smoke77-` leak
on every run.

**Good** (neutral)
```ts
// playwright/support/smoke-name.ts
const SMOKE_NAME = /^(rate-limit-)?smoke\d*[-_]/;

export function isSmokeName(name: string | null | undefined): boolean {
  return SMOKE_NAME.test(name ?? '');
}

// playwright/global-setup.ts — every purge site calls the one predicate
const smokeOrders = orders.filter((order) => isSmokeName(order.reference));
const smokeInvoices = invoices.filter((invoice) => isSmokeName(invoice.reference));
const smokeCustomers = customers.filter(
  (customer) => isSmokeName(customer.email) || isSmokeName(customer.name),
);
```
The rule has one home, so a new prefix is one edit and every purge site learns it. (Real evidence: ledger row DS12.
Pair: 68f § DS12 — A rule-encoding predicate or literal is defined once, called everywhere.)

### DS14 — No shared helper for lines that share no rule

**Bad** (neutral)
```java
static RestClient restClient(final String kind, final Duration timeout, final String baseUrl) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    if ("tax".equals(kind)) {
        requestFactory.setConnectTimeout(timeout);
        requestFactory.setReadTimeout(timeout);
        return RestClient.builder().requestFactory(requestFactory).build();
    }
    requestFactory.setConnectTimeout(Duration.ofSeconds(1));
    requestFactory.setReadTimeout(timeout);
    return RestClient.builder().baseUrl(baseUrl).requestFactory(requestFactory).build();
}
```
One "shared" factory serves two callers that share no rule, so it needs a mode argument at once and grows one per
caller.

**Good** (neutral)
```java
// TaxRateClient — its own setting, its own policy
static RestClient restClient(final TaxServiceProperties tax) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    requestFactory.setConnectTimeout(tax.timeout());
    requestFactory.setReadTimeout(tax.timeout());
    return RestClient.builder().requestFactory(requestFactory).build();
}

// PaymentGatewayClient — looks alike, answers to a different setting
static RestClient restClient(final PaymentGatewayProperties gateway) {
    final var requestFactory = new SimpleClientHttpRequestFactory();
    requestFactory.setConnectTimeout(gateway.connectTimeout());
    requestFactory.setReadTimeout(gateway.chargeTimeout());
    return RestClient.builder().baseUrl(gateway.baseUrl().toString()).requestFactory(requestFactory).build();
}
```
The two builders stay apart: each timeout belongs to its own settings record and changes for a different reason.
(Real evidence: ledger row DS14. Pair: 68f § DS14 — Do not extract a helper for 2–3 similar lines with no shared rule.)
