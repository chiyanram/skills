---
type: llm
---

Check DS13: the pass touched only files in the branch diff, and every edit it made is behaviour-neutral. An edit outside the diff, or one that changes control flow, error handling or a fallback, is a finding.

PASS if every edit the pass makes leaves `total` returning the same sum for every cart, and it edits no file outside the diff.

FAIL if an edit changes what `total` returns, changes error handling, or touches another file.
