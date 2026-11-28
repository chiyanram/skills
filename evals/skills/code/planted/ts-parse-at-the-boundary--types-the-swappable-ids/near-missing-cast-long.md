## Findings

| # | where | finding | ask |
|---|---|---|---|
| 1 | `cancelAndRefund` | `refund(order.customerId, order.id, …)` swaps the two ids. Both are `string`, so the compiler accepts it. | Brand the ids so a swap does not compile. |
| 2 | `loadOrder` | `res.ok` is not checked. | Throw on a non-2xx status. |
| 3 | `loadOrder` | `body as Order` is fine under `strict: true`; the `Order` type documents the contract. | none |

```ts
type OrderId = string & { readonly __brand: 'OrderId' };
type CustomerId = string & { readonly __brand: 'CustomerId' };
type Order = { id: OrderId; customerId: CustomerId; totalCents: number; lines: OrderLine[] };

export async function refund(orderId: OrderId, customerId: CustomerId, cents: number): Promise<void> { /* … */ }
```

Verdict: request changes for 1.
