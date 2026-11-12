---
description: A test for invoice totals whose expected value is computed by the code under test and which asserts the input it passed in.
expected_outcome: The rewritten test states worked expected values (C3) and asserts observable behaviour, not the input or a default (S2).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With testing, review this Spock spec and give the rewrite you would land.

```groovy
class InvoiceTotalsSpec extends Specification {
    def calculator = new InvoiceCalculator()

    def "totals an invoice"() {
        given:
        def invoice = new Invoice(lines: [new Line(qty: 3, unit: 4.50), new Line(qty: 2, unit: 10.00)], vatRate: 0.20)

        when:
        def result = calculator.total(invoice)

        then:
        result.net == calculator.net(invoice)
        result.gross == calculator.net(invoice) * (1 + invoice.vatRate)
        result.invoice == invoice
        result.status == InvoiceStatus.DRAFT
    }
}
```
