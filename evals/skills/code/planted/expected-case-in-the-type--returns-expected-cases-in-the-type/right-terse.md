`reserve` returns a sealed `HoldOutcome` with `Placed(Hold)`, `AlreadyHeld()` and `LimitReached()`. Neither refusal throws. The controller switches over the outcome: 201, 409, 409.
