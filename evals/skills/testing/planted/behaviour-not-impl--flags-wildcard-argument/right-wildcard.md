`rateFor(_)` accepts any argument, so a call with the wrong member would still pass. Match it by value: `1 * rules.rateFor(Member.gold())`.
