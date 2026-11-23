---
type: llm
---

Check: never mock your own classes; prefer the real object and assert observable behaviour, because a mock of your own class breaks on refactors that keep behaviour.

PASS if the review says not to mock `DiscountRules` (because it is the team's own class) and asks to use the real object and assert the resulting price.

FAIL if the review accepts the mock of `DiscountRules`, or only asks for a different stubbed value.
