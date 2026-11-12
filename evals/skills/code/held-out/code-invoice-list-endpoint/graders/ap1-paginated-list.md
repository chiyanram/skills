---
type: llm
---

Check AP1: every list endpoint is paginated from its first release, with a documented default and maximum page size, capping a larger request at the maximum.

PASS if the written endpoint takes a page size with a default and a maximum, caps a larger request, and does not return the full list.

FAIL if the endpoint returns every invoice, or takes a page size with no default or no maximum.
