`refund(order.customerId, order.id, …)` swaps the ids; both are `string`, so it compiles. Brand them: `type OrderId = string & { readonly __brand: 'OrderId' }`, and the same for `CustomerId`.
