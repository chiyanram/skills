# Report

What the human reads. Two shapes: a status block after each phase, and the final message. Name every ticket and PR
by its number with two to six words of context, every time.

## Status block, after each phase

````text
crq #<ticket> — <ticket in 2-6 words> · step <n>/12 <phase> · <lane> lane

```diff
  <file or place tree>
+ <added>
~ <changed>
- <removed>
```
<one or two lines: what now works or what was decided>
Next: <the next step>, starting now.        (or: Waiting for you: <the stop and what to answer>)
````

Keep it under ten lines. A phase with nothing to show says so in one line and goes on.

## At a stop

Lead with what you need from the human, then the context to decide it:

- what is decided, and the state of each option, with `file:line` and numbers;
- what changes with each answer;
- your recommendation, worded so "yes" accepts it.

## Final message

````text
crq #<ticket> — <ticket in 2-6 words> · PR #<n> — <PR in 2-6 words> · ready for your review

```diff
  <tree of changed files, each + ~ ->
```

| AC | command | result |
|---|---|---|
| AC-1 | <command> | <result copied from its output> |

Rulings I made: each `Ruling:` line from the ledger, or "none".
Deferred: each `consider` and `noted` finding, and each item deslop reported, at `file:line`, or "none".
Where to look: the one to three riskiest places, at `file:line` (PR6).
````

Every result is copied from its command's output (VB10). A finding the verify pass dismissed is not shown.
