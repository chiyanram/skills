---
name: writing
description: Use when you write or review text that a person or an agent reads, such as a doc, a README, an AGENTS.md or CLAUDE.md, a glossary, a skill or agent instruction, or a PR body. Covers each sentence and its words, one mode per doc, and what each project doc holds. Lists each writing notes file and when to read it.
---

# Writing

Text works when its reader acts right on the first read. A person reads a doc once and acts on it. An agent reads an
instruction on every run and does what the words say.

## The order

1. **Name the reader.** Say who reads the text and what they do next. Done when you can name the reader.
2. **Pick the mode.** For a doc under `docs/` or a README section, pick its mode by [modes.md](modes.md). Done when
   you can name the mode, where one applies.
3. **Place each fact.** Look up the file in [project-docs.md](project-docs.md). Done when each fact sits where
   `planning`'s writing-docs notes put it.
4. **Write each sentence** by [sentences.md](sentences.md). Done when each sentence carries one idea.
5. **Cut** by the first rule below. Done when no sentence fails it.
6. **Review** by the list at the end of each notes file you used, and by the list below. Done when every finding is
   fixed or reported.

## Rules for every text

- Keep only prose that changes a decision. Delete a sentence that repeats its heading or an earlier sentence. Delete a
  sentence that gives a model an instruction it follows with no prompt, such as "Write clear code" or "Be careful".
  Such a sentence costs reading time and says nothing. Delete the whole sentence, not some of its words.
- Say the positive target: write what to do. A rule that only bans a thing puts that thing in the reader's context,
  and a model then reaches for it more. Keep a ban only as a hard guardrail that has no positive form, and put the
  positive target beside it.
- Write the real name of the symbol, file, flag or command, because the reader searches for that name.
- Name the mechanism or give the number, because a vague claim gives the reader nothing to check.
- Sometimes a rule would drop a condition, give an "it" two readings, or rename a term the reader searches for. Then
  keep the sentence, and name the rule you skipped in the PR body.
- Leave compliant text alone. A rewrite keeps every condition, number and scope word of the text it replaces. A
  shorter sentence that drops a condition is a wrong sentence.

## Good / Bad

### Say what to do, not only what to avoid

**Bad**
```markdown
- Do not put dates in file names.
- Do not use abbreviations in names.
```
The reader learns two things to avoid and no target. A model reads "dates" and "abbreviations" and writes more of
them.

**Good**
```markdown
- Name a file by its subject: `renewal-policy.md`.
- Spell each word of a name in full: `loanCount`, not `lnCnt`.
```
Each line names the target. The second line keeps the ban beside its target, because the example makes it clear.

### Name the mechanism

**Bad**
```markdown
Schema changes can cause issues in the catalog service.
```

**Good**
```markdown
A column rename in `titles` fails the catalog build, because the generated queries still name the old column.
```
The reader can check the second sentence and act on it.

## Notes

- A sentence: its length, voice and words, hedges, steps and lists, links, and words such as "it" and "only":
  [sentences.md](sentences.md).
- A tutorial, a how-to, a reference or an explanation, and which mode a doc is: [modes.md](modes.md).
- A README, an AGENTS.md, a CLAUDE.md, a glossary, the `docs/` folder and its docs map, history notes and the
  **Today:** marker: [project-docs.md](project-docs.md).
- A claim and its cite, a count, or the one file that owns a fact: `planning`'s writing-docs notes.
- A PR body: `crq`'s pr-readiness notes.

A finding names the skill and its section, such as `writing`, sentences notes, Steps and lists.

## Review

Walk every line of text that the change adds or edits. Each line is a blocker unless marked (warning).

- A rule that is only a ban, with no positive target beside it.
- A rewrite that drops a condition, a number or a scope word from the text it replaced.
- A sentence that repeats its heading or an earlier sentence, or that gives a model an instruction it follows with no
  prompt, such as "Write clear code" or "Be careful".
- A rewrite of text that followed these rules already.
- A vague claim where the text could name the mechanism, the symbol or the number.
