## Findings

| # | where | finding | ask |
|---|---|---|---|
| 1 | `loadOrder` | `body as Order` checks nothing. `res.json()` gives an untyped value, and the cast tells the compiler it is an `Order` whatever the server sends. A missing `lines` or a string `totalCents` crashes later, far from the cause. | Parse the body from `unknown` with a schema at the boundary. |
| 2 | `cancelAndRefund` | `refund(order.customerId, order.id, order.totalCents)` passes the customer id as the order id and the reverse. It compiles because both are `string`. | Give the ids distinct types, so the swap is a compile error. |
| 3 | `loadOrder` | `res.ok` is not checked, so an error body is parsed as an order. | Check `res.ok` first. |
| 4 | `refund` | The refund response status is ignored. | Throw or return a result on a non-2xx status. |

## Suggested code

```ts
import { z } from 'zod';

const OrderId = z.string().brand<'OrderId'>();
const CustomerId = z.string().brand<'CustomerId'>();
type OrderId = z.infer<typeof OrderId>;
type CustomerId = z.infer<typeof CustomerId>;

const OrderSchema = z.object({
  id: OrderId,
  customerId: CustomerId,
  totalCents: z.number().int().nonnegative(),
  lines: z.array(z.object({ sku: z.string(), quantity: z.number().int().positive(), priceCents: z.number().int() })),
});
type Order = z.infer<typeof OrderSchema>;

export async function loadOrder(res: Response): Promise<Order> {
  if (!res.ok) throw new Error(`order fetch failed: ${res.status}`);
  const body: unknown = await res.json();
  return OrderSchema.parse(body);
}

export async function refund(orderId: OrderId, customerId: CustomerId, cents: number): Promise<void> { /* … */ }
```

With these types, `refund(order.customerId, order.id, …)` no longer compiles. Add a parser test with a body that lacks `lines`.

Verdict: request changes for 1 and 2.
