---
description: An agent reports tests added with no run output. The skill should give a not-verified verdict, never a pass. Today's skill does not state a verdict set; it is expected to fail until PR 2 adds the verify note.
expected_outcome: The verdict is NOT VERIFIED (or inconclusive) because no test was run; the reply asks for the command and its output.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:testing An agent finished this ticket and posted the note below. Give a verdict: is the change verified? Say why in two or three lines.

> Done. Added `RefundServiceSpec` with 4 cases (full refund, partial refund, refund after 30 days rejected, refund of a cancelled order rejected). Changed `RefundService.refund` to reject refunds after 30 days. All tests should pass.

No command output and no CI link are attached.
