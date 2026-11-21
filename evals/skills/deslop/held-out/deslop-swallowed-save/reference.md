---
approved: null
---

Edit: remove the two commented-out lines above the `try`. Report, do not fix: the `try`/`catch` around `stocks.save` logs and continues, so a failed reservation looks like a success. `stocks` is an injected repository, so the catch silences a real failure; the author decides how the failure is handled.
