## Findings

| # | where | finding | ask |
|---|---|---|---|
| 1 | `loadOrder` | `body as Order` is a cast with no check, so any JSON becomes an `Order`. | Type the body as `unknown` and parse it with a zod `OrderSchema`; infer `Order` from the schema. |
| 2 | `cancelAndRefund` | The ids are swapped: `refund(order.customerId, order.id, …)`. | Call `refund(order.id, order.customerId, order.totalCents)`. |
| 3 | `loadOrder` | `res.ok` is not checked. | Throw on a non-2xx status before parsing. |

```ts
export async function loadOrder(res: Response): Promise<Order> {
  if (!res.ok) throw new Error(`order fetch failed: ${res.status}`);
  const body: unknown = await res.json();
  return OrderSchema.parse(body);
}

export async function cancelAndRefund(res: Response): Promise<void> {
  const order = await loadOrder(res);
  await refund(order.id, order.customerId, order.totalCents);
}
```

Verdict: request changes.
