Add `expect: policy.fee(due, due) == Money.ZERO` to LateFeePolicySpec, remove the `+ 1`, and run the spec; everything passes. The new case documents the bug.
