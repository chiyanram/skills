AC1 is misread: a `DELIVERED` order can be cancelled, because the guard checks only `SHIPPED`. Refuse every status other than `PLACED` and `PAID`.
