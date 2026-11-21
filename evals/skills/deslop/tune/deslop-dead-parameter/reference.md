---
approved: null
---

Edit: remove the unused `locale` parameter from `sum` and the `Locale.ROOT` argument at its one call. `total` returns the same sum for every cart. Other behaviour-neutral cleanups of lines the branch added are allowed, such as inlining `sum` into `total`. No edit outside the diff, and no change to what `total` returns.
