---
description: A service throws for an expected not-found and a catch rethrows without the cause. The review should flag both.
expected_outcome: The thrown not-found is reported as a case for a sealed return type (ER1); the rethrow that drops the cause is reported (ER3).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With code, review this invoice service and list each rule it breaks, with the fix.

```java
@Service
class InvoiceService {
    private final InvoiceRepository invoices;
    private final PaymentGateway gateway;

    InvoiceService(final InvoiceRepository invoices, final PaymentGateway gateway) {
        this.invoices = invoices;
        this.gateway = gateway;
    }

    Invoice find(final InvoiceId id) {
        return invoices.findById(id)
                .orElseThrow(() -> new InvoiceNotFoundException(id));
    }

    void settle(final InvoiceId id) {
        final Invoice invoice = find(id);
        try {
            gateway.charge(invoice.total());
        } catch (final GatewayException e) {
            throw new SettlementFailedException("could not settle " + id);
        }
    }
}
```

`find` is called from a controller that turns `InvoiceNotFoundException` into a 404.
