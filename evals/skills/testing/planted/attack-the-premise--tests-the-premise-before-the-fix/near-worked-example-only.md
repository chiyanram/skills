The premise is checked first. For 100 EUR, `compareTo(100) >= 0` is true, so the rule is correct. In the caller, 10000 cents becomes 10.000, not 100.00.
