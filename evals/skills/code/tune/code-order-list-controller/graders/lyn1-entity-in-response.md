---
type: llm
---

Check LYN1: a controller returns response DTOs, never persistence entities.

PASS if the review says the controller returns the `Order` entity (leaking `internalNotes` and tying the API to the schema) and recommends a response DTO.

FAIL if the entity in the response is not flagged.
