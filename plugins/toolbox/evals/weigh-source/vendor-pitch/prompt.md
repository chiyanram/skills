---
description: A vendor article that sells its own product. The tool should name the vendor's stake and not recommend buying.
expected_outcome: The report names the author as a vendor and what they gain; it uses the piece as a checklist and does not recommend the product.
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
---

/toolbox:weigh-source Weigh this article against our design.

The source, "Stop hand-rolling your CI: why every team needs PipeFlow", by the PipeFlow product team:

```markdown
Teams waste weeks on CI scripts. PipeFlow gives you hosted runners, a visual pipeline editor and built-in flaky-test
detection. Our customers cut build times by 60%. Caching should be automatic, not configured. Every pipeline needs a
dashboard. Start your free trial today and move your pipelines in an afternoon.
```

The project's design, from `docs/design.md`:

```markdown
- D1: CI runs on GitHub Actions; the workflow files live in the repo and a person reviews each change to them.
- D2: The test suite caches dependencies with `actions/cache`, keyed on the lockfile.
- D3: Flaky tests are quarantined by hand with a ticket; no automatic retry.
- Roadmap: step 2 adds a weekly report of slow tests.
```
