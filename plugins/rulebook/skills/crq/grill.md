# Grill

Ask the human until you both hold the same picture of the change. Facts are yours to find; decisions are the human's.

## The question tree

Each decision opens the decisions that depend on it. The **frontier** is every open decision whose parents are
settled: what you can ask now without guessing an answer you have not heard.

## Each round

1. Find the facts first. A question the code, the docs or the research subagent can answer is not a question. Look it
   up, and give the fact at `file:line` when you use it.
2. Ask the whole frontier in one numbered round. Each question has two to four short choices and one recommended
   choice, worded so "yes" accepts it. The human answers with "yes", "1A 2B" or their own words. With the project's
   `questions: one-at-a-time`, ask the first question on the frontier only.
3. Challenge each directive of the human's that nobody has examined, once: name the cost or the conflict you see, and
   recommend. After the human answers, it is settled. Do not ask it again.
4. Check a correction from the human against the code before you accept it. When the code disagrees, say so at
   `file:line`, and ask once.
5. Write the answers into the spec draft before the next round, each with the human's words.
6. Work out the new frontier. A question that waits on another question in this round goes in a later round.

Then stop (stop 1) and wait for the answers.

## Done when

- the frontier is empty: every branch of the tree is settled, and nothing is silently assumed;
- every assumption is marked stated, inferred at `file:line`, or a default the human confirmed (SR19);
- the human says the picture is right.

A default goes in the spec only when the human confirmed it. A guess you would make yourself is a question.

## Good / Bad

**Bad**
```text
Q1 Retention period? Q2 Soft or hard delete? Q3 Batch size?
(the rest assumed as defaults; grill ends)
```
Q3 depends on Q2, and the defaults were never shown to the human.

**Good**
```text
Round 1
1. How long do we keep a deleted loan before the purge? A) 30 days  B) 90 days  C) 1 year
   -> B: LoanRepository.java:21 keeps deletedAt, and nothing reads it after 60 days.
2. Purge means a hard delete of the row? A) yes  B) move to an archive table
   -> A: no report reads deleted loans (grep finds no reader of deleted_at).
Batch size waits for answer 2.
```
Each question has choices and a recommendation, the facts come with `file:line`, and a question that depends on
another waits.
