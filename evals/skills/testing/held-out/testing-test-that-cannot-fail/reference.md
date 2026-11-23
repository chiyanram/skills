---
approved: operator
---

It would not catch a bug in the rate. The expected value comes from `calculator.rateFor(...)`, the code under test, so a wrong rate passes on both sides; write the expected fine out by hand (for example 40 cents for 4 days at 10 cents). The assertion sits inside an `if`, so if the condition is false the spec passes with no assertion; assert unconditionally. Also compare with a non-student case, since the name promises "cheaper".
