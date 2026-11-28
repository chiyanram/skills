---
approved: operator
---

Two problems. First, `body as Order` checks nothing: `res.json()` gives an untyped value, and the cast tells the
compiler it is an `Order` whatever arrives, so a missing or wrong field crashes later. Treat the body as `unknown` and
parse it at the boundary, for example with a zod schema (`OrderSchema.parse(body)`, with `Order` as
`z.infer<typeof OrderSchema>`) or a type guard that checks each field. Second, `cancelAndRefund` passes
`order.customerId` as `orderId` and `order.id` as `customerId`; it compiles because both are `string`. Swapping them
back fixes this call only. Give the ids distinct types, such as branded `OrderId` and `CustomerId` made by the parser,
or take one object argument with named fields (`refund({ orderId, customerId, cents })`), so a swap no longer compiles.

Allowed extras: a check of `res.ok` before parsing, a check of the refund response status, an integer check on
`cents`, or a test of the parser with a bad body.
