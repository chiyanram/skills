---
type: llm
---

The human should see what each phase did without reading the files.

PASS if each phase that ended in this turn (intake, research, spec, design, design review) is followed by a short
status that names the phase and what comes next, or the final message lists each phase with what it produced.

FAIL if phases end with no status, so the human cannot tell which phases ran.
