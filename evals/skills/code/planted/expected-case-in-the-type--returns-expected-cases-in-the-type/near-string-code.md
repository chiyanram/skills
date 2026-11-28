`reserve` returns `record HoldOutcome(String code, Hold hold)`, with `code` set to `"PLACED"`, `"ALREADY_HELD"` or `"LIMIT_REACHED"`. Nothing is thrown. The controller maps the code to 201 or 409.
