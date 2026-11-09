---
name: grilling
description: Grill the user about a plan, decision, or idea, one question at a time in plain words, until you share an understanding. Use for /grilling, or when the user wants to stress-test their thinking.
disable-model-invocation: true
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Ask **one question at a time**. Pick it from the **frontier**: the decisions whose prerequisites are already settled, so you can ask them now without guessing at answers you haven't heard yet. Of those, ask the one that unblocks the most other decisions. Then wait for the user's answer before the next question.

Use plain words. Write the question as you would say it to a colleague, and use the user's own terms. Don't use this skill's words (frontier, design tree, round) in the question. When you need a new term, say what it means in the same sentence.

Format each question like so:

```
❓ **<question title>**: <question body, a few short sentences, with the choices if there are any>

➡️ <your recommended answer, and why in one sentence>
```

Word each question so "yes" accepts your recommended answer.

Each answer reshapes the tree: a settled decision unblocks the questions that depended on it. Pick the next question from what is now unblocked.

Finding _facts_ is your job, never the user's. When a question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: ask a question that does not depend on that fact while the sub-agent works. The _decisions_ are the user's: put each to them and wait.

The session is done when nothing is left to decide: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.
