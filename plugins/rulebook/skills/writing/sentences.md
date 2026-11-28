# Sentences

How each sentence and its words read. Read it when you write or review any text: a doc, a skill, an agent
instruction or a PR body.

## Words

- Give each word one meaning, and use one word for each thing or action. Repeat that word every time, because a
  reader takes a new word for a new thing. Write "check" each time, not "check", "verify" and "confirm" in turn.
- Define each domain term once, where it first appears, or in the glossary. Keep a technical term the reader needs.
- Write whole sentences, with their articles and small words such as "the", "a" and "that". Spell out arrows and
  abbreviations. A dropped word leaves two readings: "Files not saved are lost" does not say which files.
- Keep a noun cluster to three words at most. Turn a longer one into a phrase: "the handler that sets queue
  priority", not "task queue priority handler".
- Put "only" and "not" next to the word they change, because the place sets the meaning.
- Make each "it", "this" and "they" point at one thing the reader can see. When it could point at a whole clause,
  name the thing again.
- Use the literal word and a strong verb. Give the number where an adverb would stand: "in 40 ms", not "very fast".
  A metaphor makes the reader translate it back.

## Sentences

- Put one idea in each sentence, and one instruction in each step. Split a sentence that the reader must read twice.
- Keep a sentence to 20 words or fewer in a procedure, and to 25 or fewer in a description. Split a longer one at
  its "and" or at its condition, because each extra clause is one more thing to hold.
- Use the active voice, and name the actor. Use the passive only when the actor is unknown or does not matter.
- Write to the reader as "you", in the present tense.
- Give a claim one hedge at most, such as "may", or state the condition under which it holds. Stacked hedges hide
  whether the claim is true.
- Give the answer in the first sentence, with no praise opener and no chatbot close, because the reader came for the
  answer.

## Steps and lists

- Write each step as a command. Put the condition before the instruction, and the common case first. A reader acts
  on a step before they read a condition that follows it.
- Use a numbered list for three or more steps, and a bulleted list for three or more conditions.
- In a procedure, say what the step does, with no "easy", "just" or "quickly". A reader who finds the step hard then
  doubts the whole doc. Outside a procedure these words can be correct, as in "just inside the limit".
- Make link text name its target, such as "the release guide", not "here", because a reader scans the links to
  find their way.

## Good / Bad

### A rewrite keeps every condition

**Bad**
```markdown
Before: Renew the loan up to two times, which is blocked if the member has unpaid fines or a reservation is held on the title.
After:  Renew the loan.
```
The rewrite is shorter and wrong. The fine check, the reservation check and the limit are gone.

**Good**
```markdown
Before: Renew the loan up to two times, which is blocked if the member has unpaid fines or a reservation is held on the title.
After:  If the member has no unpaid fines and no one holds a reservation on the title, renew the loan. Renew it two times at most.
```
The rewrite puts both conditions before the step, names the actor, and keeps the limit.

### The condition comes before the step

**Bad**
```markdown
Delete the branch and close the ticket, but only after the release job passes, and tell the owner.
```
The reader deletes the branch before reaching "only after". Three actions share one sentence.

**Good**
```markdown
When the release job passes:
1. Delete the branch.
2. Close the ticket.
3. Tell the owner.
```

## Review

Walk every sentence that the change adds or edits. Each line is a blocker unless marked (warning).

- Two words for one thing or action, or one word for two.
- A domain term used before it is defined, with no glossary entry.
- A dropped article or verb, an arrow or an abbreviation that leaves two readings.
- A noun cluster of four words or more.
- An "it", "this" or "they" that could point at two things, or an "only" or "not" away from its word.
- A sentence over 20 words in a procedure, or over 25 in a description. (warning)
- A step that holds two instructions, or a condition after the step it guards.
- A passive sentence that hides an actor who matters.
- Two hedges on one claim, a praise opener or a chatbot close.
- "easy", "just" or "quickly" in a procedure step.
- Link text that does not name its target.
