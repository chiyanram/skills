`HoldController`: `return switch (outcome) { case Placed p -> created(p.hold()); case AlreadyHeld _ -> status(409); case LimitReached _ -> status(422); };` with no `default`.
