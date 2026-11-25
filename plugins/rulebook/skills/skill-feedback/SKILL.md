---
name: skill-feedback
description: Use at the end of a session in any project to turn where a rulebook skill or this repo's tooling failed into issues for the skills repo - a correction, a retraction, a redo, a rule that misled or a rule that was missing. Drafts each issue with its proposed fix and the case that proves it; files only on the person's yes.
disable-model-invocation: true
---

# Skill feedback

Turn this session's evidence into issues on `chiyanram/skills`, so each skill is fixed from real use. A person starts
it by hand. It reads the session and changes no skill and no code.

```
session ──▶ find gaps ──▶ trace each to its owner ──▶ draft issues ──▶ person: yes / no / edit ──▶ file the yes
```

## What counts

A **gap** is a moment the session shows: the person corrected the work, the agent took a claim back, work was
redone, or advice from a skill was followed and proved wrong. Count only what the session holds, with a quote or a
log line, because a gap from memory is a guess.

Each gap has one **owner** in the skills repo:

- a rule in a skill: name the skill, its section and the rule's words, quoted;
- missing: the skill covers the work but no rule says what was needed;
- trigger: the skill loaded for work it does not cover, or stayed unloaded for work it does;
- tooling: a file of the skills repo itself, such as `scripts/skill_eval.py`, `.github/workflows/release.yml` or
  `CONTRIBUTING.md`; name the file.

A gap in another project's own code or in the agent harness has no owner here. Report it in one line and file
nothing.

## Steps

1. **List the skills that loaded**, and the skills-repo files the session ran or edited. If no skill loaded, look
   for work a skill covers that ran without it (a trigger gap). Done when each is named with the work it was used for.
2. **Find the gaps.** Read the whole session, including the part before any summary: the harness transcript holds
   it when the context was compacted. Done when every correction, retraction and redo is listed with its quote.
3. **Trace each gap to its owner.** Read the rule in the installed skill, or the tooling file, before you name it.
   Drop a gap that an existing rule already covers and that the agent simply missed, and say which rule. Done when
   each gap has an owner or a one-line reason it has none.
4. **Search for a twin**: `gh issue list -R chiyanram/skills --state open --search "<skill or file> <two key words>"`.
   A match becomes a comment draft on that issue. Done when each gap is a new issue or a comment on a named one.
5. **Draft each issue** in the shape below.
   - Quote the person's own words as evidence. Paraphrase their code, file names and data, because the skills repo
     is public and the session may hold an employer's code. A gap with no quote cites its log line instead.
   - Propose the fix at the highest level that holds: a script or lint, then a review check, then a rule's wording,
     then a new rule, because a written rule only asks.
   - Give the case that would have caught the gap: for a skill, an eval prompt in two lines and what its grader
     checks; for tooling, the test and the fixture it uses. A fix without its case cannot be proved.
6. **Show every draft at once** and wait. File only the drafts the person says yes to, because an issue is public
   the moment it is filed: `gh issue create -R chiyanram/skills --label needs-triage`, or `gh issue comment` for a
   twin. If `gh` cannot reach the repo, print the drafts for the person to paste.
7. **Report** one line per gap: its issue link, "comment on #N", "no owner: <why>" or "not filed".

## Issue shape

```markdown
Title: fix(<skill or area>): <what went wrong, at most 8 words>      (feat(...) for a missing rule)

**What happened**: <the work, paraphrased> · **Expected**: <what the person wanted>
**Owner**: <skill + section, or the file> · missing · trigger — <the rule's words, quoted>
**Evidence**: "<the person's words>" or <the log line> (<project kind, never its name>, <date>)
**Proposed fix** (<level>): <the new wording, the script, or the check>
**Case**: <eval prompt + grader check, or test + fixture>
```

## Good / Bad

**Bad**: `fix(code): code skill is too strict`. No owner, no quote, no case: nobody can act on it.

**Good**: `fix(testing): junk-test rule flags a routing swap test`. Owner: testing, "Writing the test", its accessor
line quoted. Evidence: "that test is not junk, the two ids can swap". Proposed fix (rule wording): "test the routing
of two inputs of one type". Case: a service passes `orderId` and `userId` to two calls; the grader checks the reply
keeps the swap test.
