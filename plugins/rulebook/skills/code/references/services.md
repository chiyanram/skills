# Services

Where a decision lives, when a class earns an interface, and what a single use-case method must hold together. Read it
when you write or review a controller, a service, an interface or a use case that makes two calls.

Contents: Rules · When X, use Y · Good / Bad (LY1, LY2) · Decided edges · Review checks

## Rules

- **LY1** — Keep a controller to binding, delegating and shaping the response; put any branch that chooses an outcome
  in a service, because logic in a controller cannot be tested without the web framework.
- **LY3** — Put operations that must succeed or fail together, such as a change and its audit row, in one
  transactional use-case method, because two calls left to the caller let one commit without the other.
- **LYN1** — Return response DTOs from a controller, never persistence entities, because an entity in a response leaks
  every field it owns and ties the API to the schema.
- **LY2** — Add an interface only where two implementations exist now, such as an adapter and a fake, or at a
  module boundary; else depend on the class, because a one-implementation interface is indirection without a seam.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a branch that chooses an outcome: a state check, or the order of calls | a service method that returns the outcome (LY1) | SBS layered-architecture: "`@RestController` ← HTTP only. No business logic." · DDH: a controller is "used for parsing requests, triggering business logic and presenting the result back to the client" (r48 :761) |
| operations that must succeed or fail together | one use-case method in one transaction (LY3) | SBS transactional-patterns: "Place multi-step business transactions at the application/service boundary." · DDH: "a global transaction to make sure all the changes … are stored atomically (all or nothing)" (r48 :772) |
| a controller response | a response DTO, mapped from the entity (LYN1) | SBS layered-architecture: "No JPA entities in responses" · DDH: "clients only receive data described in DTOs contract, not everything that your model/entity owns (which may result in data leaks)" (r48 :778) |
| a dependency with a production adapter and a test fake | an interface for the seam (LY2) | MP codebase-design: "Two adapters means a real one." (r48 :766) |
| a class with one implementation | the concrete class, with no interface (LY2) | MP DEEPENING: "A single-adapter seam is just indirection." · DDH: "it's totally fine to depend on a concrete implementation instead of abstracting it with an interface" (r48 :766) |

Sources: `r48 :N` is a line of agent-factory `research/48-industry-recheck-code.md`, which records each quote with
the repository and commit it was read at. SBS = rrezartprebreza/spring-boot-skills `skills/spring-boot-4/*/SKILL.md`;
DDH = Sairyss/domain-driven-hexagon `README.md`; MP = mattpocock/skills `skills/engineering/codebase-design`.
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

### LY2 — An interface only where two implementations exist now, or at a module boundary

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
An interface with one implementation and no fake of it is indirection without a seam; the real boundary is
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
68f § LY2 — An interface only where two implementations exist now, or at a module boundary. Real evidence: ledger row
LY2.)

## Decided edges

- **Skip when** the controller switches exhaustively over a sealed outcome the service returned: that switch presents
  the result, which is shaping (DDH, r48 :761) (LY1). — **Do not skip when** the controller itself checks state or
  chooses the order of calls (LY1). — **Confidence** high

## Review checks

Walk every changed controller, service and interface.

- [ ] LY1 — For each controller method, list its `if`, `switch` and loop statements. A branch that chooses an outcome is
  a finding; an exhaustive `switch` over an outcome the service returned is not.
- [ ] LY3 — For each set of operations that must succeed or fail together, such as a change and its audit row, find one
  use-case method in one transaction. Two calls left to the caller, or two transactions, is a finding.
- [ ] LYN1 — List the entity classes (`grep -rlE "^\s*@Entity\b"`). A controller method whose return type is, holds
  or wraps one of them is a finding.
- [ ] LY2 — For each new or changed interface, find two implementations in the code now (a test fake counts) or a
  caller in another module. An interface with neither is a finding.
