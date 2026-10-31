# Services

Where a decision lives, when a class earns an interface, and what a single use-case method must hold together. Read it
when you write or review a controller, a service, an interface or a use case that makes two calls.

Contents: Rules · When X, use Y · Good / Bad (LY1, LY2) · Decided edges · Review checks

## Rules

- **LY1** — Keep a controller to binding, delegating and shaping the response; put any branch that chooses an outcome
  in a service, because logic in a controller cannot be tested without the web framework.
- **LY2** (operator preference, 2026-10-31) — Add an interface only for a boundary dependency a test fakes, or a type
  another module calls, with one package-private implementation named `Default<Name>`, because a one-implementation
  interface is indirection with no real seam.
- **LY3** — Put two operations that must not be split (a write and its audit record) behind one method and one
  transaction at the use-case level, because two separate calls let one be dropped, leaving half done.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a branch that chooses an outcome: a state check, or the order of calls | a service method that returns the outcome (LY1) | pstack principle-boundary-discipline :9 "Business logic lives in pure functions. The shell is thin" · Jeffallan :183 `@Service` for business logic, `@RestController` for HTTP · plinth 301 :203 web stereotypes for HTTP adapters, `@Service` for application logic |
| a dependency a test replaces with a fake, such as an outbound port, or a type another module calls | an interface and one package-private `Default<Name>` implementation (LY2) | mattpocock tdd/mocking.md :3 "Mock at system boundaries only" · the `Default<Name>` name and package-private: operator preference |
| a class with one implementation that no test fakes | the concrete class, with no interface (LY2) | mattpocock codebase-design DEEPENING.md :29 "One adapter means a hypothetical seam" · plinth 123-java-design-patterns :44 "NO OVER-ABSTRACTION … single stable implementation" · pstack design-red-flags :33 "Keep a forwarding boundary only when it adds policy, adaptation, or a distinct abstraction" |
| two operations that must not be split | one use-case method in one transaction (LY3) | plinth 123-database-persistence-patterns :42 "Place transaction boundaries at use-case/service level" and Example 3 · pstack design-red-flags :13 "Callers coordinate several methods to complete one operation" |

Sources: pstack = cursor-plugins `pstack/skills` (`principle-boundary-discipline/SKILL.md`,
`architect/references/design-red-flags.md`); mattpocock = mattpocock-skills `skills/engineering`; plinth =
jabrena-plinth `skills/*/references`; Jeffallan = Jeffallan claude-skills `spring-boot-engineer/SKILL.md`.
`68f § ID — title` is a heading of `research/68f-neutral-code.md`. How a bean takes its dependencies (LY6) and binds
its settings (LY7) is in `spring.md`.

## Good / Bad

### LY1 — A controller binds, delegates and shapes; a branch that chooses an outcome lives in a service

**Bad** (neutral)
```java
Invoice invoice = invoiceService.get(id);
// … caller id, trace id, 6 comment lines on ordering …
if (invoice.status() != InvoiceStatus.OPEN) {
    throw new OrderException(ErrorCode.INVOICE_ALREADY_PAID,
        "invoice " + invoice.id() + " is " + invoice.status());
}
// … 4 comment lines on charging before recording …
if (paymentGateway.charge(invoice.id(), invoice.total())
        instanceof ChargeDecision.Declined declined) {
    throw new OrderException(ErrorCode.PAYMENT_DECLINED,
        "gateway declined: " + declined.reason());
}
paymentService.record(invoice.id(), invoice.total());
```
The controller decides whether an invoice may be paid and in what order, so that contract lives where no service test
reaches.

**Good** (neutral)
```java
@PostMapping("/{id}/payments")
@PreAuthorize("@invoiceAuth.canPay(#id)")
public ApiResponse<PaymentResponse> pay(
        @PathVariable final UUID id,
        @RequestBody final PayInvoiceRequest request,
        final Authentication authentication) {
    final PayOutcome outcome = invoicePayer.pay(id, callerOf(authentication), request);
    return switch (outcome) {
        case PayOutcome.Paid paid -> ApiResponse.ok(PaymentResponse.of(paid));
        case PayOutcome.AlreadyPaid already ->
                throw new OrderException(ErrorCode.INVOICE_ALREADY_PAID, already.detail());
        case PayOutcome.Declined declined ->
                throw new OrderException(ErrorCode.PAYMENT_DECLINED, declined.detail());
    };
}
```
The service checks status, charges and records in order, returning a sealed outcome; an exhaustive switch over it is
shaping, which is allowed. (Pair: 68f § LY1 — A controller binds, delegates and shapes; a branch that chooses an outcome
lives in a service. Real evidence: ledger row LY1.)

### LY2 — An interface only for a faked boundary or a module boundary; its one implementation is `Default<Name>`

**Bad** (neutral)
```java
@Service
public class PaymentGatewayRegistryImpl implements PaymentGatewayRegistry {
    private final List<PaymentGateway> gateways;

    public PaymentGatewayRegistryImpl(List<PaymentGateway> gateways) {
        this.gateways = gateways;
    }

    @Override
    public PaymentGateway forMethod(String method) {
        for (PaymentGateway gateway : gateways) {
            if (gateway.supports(method)) {
                return gateway;
            }
        }
        throw new UnsupportedPaymentMethodException(method);
    }
```
A public `*Impl` behind an interface in a shared module, though every caller is in billing and the real boundary is
`PaymentGateway`.

**Good** (neutral)
```java
@Service
public class PaymentGatewayRegistry {

    private final List<PaymentGateway> gateways;

    public PaymentGatewayRegistry(final List<PaymentGateway> gateways) {
        this.gateways = List.copyOf(gateways);
    }

    public PaymentGateway forMethod(final String method) {
        return gateways.stream()
                .filter(gateway -> gateway.supports(method))
                .findFirst()
                .orElseThrow(() -> new UnsupportedPaymentMethodException(method));
    }
```
One concrete class in billing; tests build it with `FakePaymentGateway`s instead of mocking the selection logic. (Pair:
68f § LY2 — An interface only for a faked boundary or a module boundary; its one implementation is `Default<Name>`. Real
evidence: ledger row LY2.)

## Decided edges

- **Skip when** the controller switches exhaustively over a sealed outcome the service returned: that switch is shaping,
  which is allowed (LY1, operator preference). — **Do not skip when** the controller itself checks state or chooses the
  order of calls (LY1). — **Confidence** high

## Review checks

Walk every changed controller, service and interface.

- [ ] LY1 — For each controller method, list its `if`, `switch` and loop statements. A branch that chooses an outcome is
  a finding; an exhaustive `switch` over an outcome the service returned is not.
- [ ] LY2 — For each new or changed interface, find a fake of it in the tests or a caller in another module. An
  interface with neither is a finding. A single implementation not named `Default<Name>`, or not package-private, is a
  finding, and so is `*Impl` (`grep -rn "class .*Impl "`).
- [ ] LY3 — For each pair of operations that must not be split, such as a write and its audit record, find one use-case
  method in one transaction. Two calls left to the caller, or two transactions, is a finding.
