---
description: New logic that calls a tax-rate HTTP service. The agent is tempted to write only the happy path and leave the untested cases unsaid.
expected_outcome: The outage case is tested with a predictable failure, a WARN or ERROR log and no hang (C2), and every case left untested is recorded as a gap row for the MR description (C4).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With testing, write the tests for `InvoiceTaxer.taxFor` and the text you would put in the merge request about test coverage.

```java
final class InvoiceTaxer {
    private final TaxRateClient rates;    // our client for a third-party HTTP tax-rate API
    private static final Logger log = LoggerFactory.getLogger(InvoiceTaxer.class);

    Money taxFor(final Invoice invoice) {
        final TaxRate rate = rates.lookup(invoice.country());
        return invoice.net().times(rate.value());
    }
}
```

The team has time for three tests today.
