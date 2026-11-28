---
description: TypeScript code casts a response body with `as` and takes two ids as plain strings, and a caller swaps them. The review should ask to parse the body from `unknown` at the boundary, and to give the ids distinct types so the swap cannot compile. Today's skill covers the `as` cast in its stack notes; branded ids and object arguments are planned TypeScript notes.
expected_outcome: The review flags `body as Order` and asks for a schema or a checking type guard on `unknown`; it finds the swapped `refund` arguments and asks for branded id types or a named-field argument.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Review this TypeScript change. List each problem and the change you would ask for.

```ts
type OrderLine = { sku: string; quantity: number; priceCents: number };
type Order = { id: string; customerId: string; totalCents: number; lines: OrderLine[] };

export async function loadOrder(res: Response): Promise<Order> {
  const body = await res.json();
  return body as Order;
}

export async function refund(orderId: string, customerId: string, cents: number): Promise<void> {
  await fetch(`/api/orders/${orderId}/refunds`, {
    method: 'POST',
    body: JSON.stringify({ customerId, cents }),
  });
}

export async function cancelAndRefund(res: Response): Promise<void> {
  const order = await loadOrder(res);
  await refund(order.customerId, order.id, order.totalCents);
}
```

`tsconfig.json` has `strict: true`. The project already depends on `zod`.
