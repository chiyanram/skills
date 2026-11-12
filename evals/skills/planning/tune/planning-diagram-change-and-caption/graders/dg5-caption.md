---
type: llm
---

Check DG5: a diagram has at most a one-line caption, and a diagram that needs more prose is redrawn smaller.

PASS if the review flags the multi-sentence caption as explaining the diagram, and the corrected version has a caption of one line or less.

FAIL if the long caption is kept, or only moved elsewhere next to the diagram.
