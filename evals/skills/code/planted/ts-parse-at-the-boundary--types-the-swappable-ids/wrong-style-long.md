## Review

| # | where | comment |
|---|---|---|
| 1 | `loadOrder` | Add a JSDoc comment that says the function reads the body once. |
| 2 | `refund` | `cents` could be `amountCents` to match `totalCents`. |
| 3 | `refund` | Prefer `const url = …` above the `fetch` call for readability. |
| 4 | types | `type` and `interface` are mixed in the module; pick one. |

The types are clear and `strict` is on. Approve with nits.
