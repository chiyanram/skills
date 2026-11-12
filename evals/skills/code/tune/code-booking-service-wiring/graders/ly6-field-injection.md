---
type: llm
---

Check LY6: required dependencies come through the constructor into `final` fields, never fields or setters.

PASS if the review flags the `@Autowired` fields and recommends constructor injection into `final` fields.

FAIL if the field injection is accepted or not mentioned.
