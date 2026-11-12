---
type: llm
---

Check B3: for a Range, test just inside and just outside each edge, not only the edge.

PASS if the added tests include 100.00 (on the edge) and a value just below (99.99), and optionally just above (100.01), with the expected shipping worked by hand.

FAIL if only the 100.00 edge is added, or only one side of it.
