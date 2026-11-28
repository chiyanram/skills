The ids are swapped in `cancelAndRefund`. Change `refund` to take one object, `refund({ orderId, customerId, cents })`, so each id is passed by name and a swap no longer compiles.
