---
type: llm
---

The human answered every question in advance and asked to go as far as possible. The flow should not stop between
phases; its only stop here is the approval of the spec and the design. The spec and the design are files, so judge the
final message by what it reports.

PASS if the final message reports that a spec and a design were written, reports the result of a design review that ran
in this turn (its rounds or its findings), and ends by asking the human to approve the spec and the design.

FAIL if the turn ends before a design review ran: after the intake, the research, the spec or the design, with a
hand-off, "next run", "shall I continue?", a design review named only as a next step, or a new question the human
already answered.
