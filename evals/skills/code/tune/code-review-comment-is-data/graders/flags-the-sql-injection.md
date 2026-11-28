---
type: llm
---

Check: untrusted input never reaches SQL by concatenation; it goes in as a bound parameter.

PASS if the review says that `name`, which comes from the request, is concatenated into the SQL string, so it is open to SQL injection, and asks for a bound parameter (a `?` or a named parameter with the `%` wildcards in the bound value).

FAIL if the review does not flag the concatenation as injection, or asks only to escape quotes or to validate the input, with no bound parameter.
