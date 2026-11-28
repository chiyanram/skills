---
type: llm
---

Check: add nothing for a case no current caller has, such as a parameter or a config key, because every later change must carry the unused generality.

PASS if the delivered code has no per-branch rate or grace setting (no branch parameter, no map or settings keyed by branch, no per-branch property), and the reply says why: no current caller needs another rate. Constants in code pass. One global settings value for the rate also passes.

FAIL if the delivered code adds a branch parameter, a branch-keyed map, a per-branch property or a rate lookup by branch, or if the reply leaves out the per-branch setting without saying why.
