---
approved: null
---

Report, do not rewrite: `fine` nests three `if` levels that guard clauses could flatten, and `label` holds a nested ternary. A flatter shape may be suggested, but changing control flow needs review, so the pass does not restructure the `if` levels in `fine` or the ternary in `label`. A behaviour-neutral edit that leaves the control flow as it is, such as `loan.isReturned() == false` to `!loan.isReturned()`, is allowed. No edit outside the diff.
