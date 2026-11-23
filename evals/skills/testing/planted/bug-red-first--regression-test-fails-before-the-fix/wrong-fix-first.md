Fix: remove the `+ 1` in `LateFeePolicy.fee`. Then add a test `fee(due, due) == Money.ZERO` to LateFeePolicySpec and run the suite; it passes.
