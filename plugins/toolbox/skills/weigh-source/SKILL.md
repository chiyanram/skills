---
name: weigh-source
description: Weigh a shared article, talk, post or note against this project's own design and the field, and say what to take, reject or watch. Use for /weigh-source.
disable-model-invocation: true
---

Read the source in full. Then weigh it, short.

1. **Who and why.** Name the author and their stake: vendor, practitioner, researcher, opinion. Say what they gain if the reader agrees. A sales piece is a checklist, never a recommendation. If part of the source is missing (an image, a paywall, a demo), say so, and weigh only what you read.
2. **Claims.** Pull out the core ideas, at most seven. Mark each as data, anecdote or assertion.
3. **Ours.** Read the project's own design first: the principles, decisions and roadmap that AGENTS.md or CLAUDE.md points to. Never weigh from memory. Work not yet merged is a gap, never have. For each claim pick one verdict:
   - **have**: cite where;
   - **conflict**: cite the decision it would change; that is a question for the person, never a change you make;
   - **gap**: real and missing; read the roadmap and say which step it belongs to;
   - **not for us**: one-line reason.
4. **Field.** For the claims that matter, say whether they're common practice, contested, or one vendor's view. Cite a source, or mark it unverified.
5. **Verdict.** Take, reject, watch: one line each.

Report terse. Fragments fine. No preamble, no praise, no recap of the source.

```
<title> — <author>, <stake>
claim | kind | verdict | where/why
take: …
reject: …
watch: …
ask: <conflicts, as questions>
```

Limits: no ticket, no file change, no approval. Agreeing with everything is a smell: look again for the conflict.
