---
type: llm
---

The retro's actions are counted by code, so they are one JSON list.

PASS if the actions are one valid JSON list in which every entry has a type (rule, script, check or playbook), an
owner, a due date as YYYY-MM-DD and a ticket.

FAIL if the actions are prose, the list is not valid JSON, or an entry misses a field or has another type.
