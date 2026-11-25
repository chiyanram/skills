---
name: skill-feedback
description: Use at the end of a session in any project to turn where a rulebook skill failed into issues for the skills repo - a correction, a retraction, a redo, a rule that misled or a rule that was missing. Drafts each issue with its proposed rule change and eval case; files only on the person's yes.
disable-model-invocation: true
---

# Skill feedback

Turn this session's evidence into issues on `chiyanram/skills`, so each skill is fixed from real use. A person starts
it with `/rulebook:skill-feedback`. It reads the session; it changes no skill and no code.

```
session ──▶ find gaps ──▶ trace to a rule ──▶ draft issues ──▶ person: yes / no / edit ──▶ file the yes
```

## Rules

- **SF1** — Count a moment as a gap only when the session shows it: the person corrected the work, the agent took a
  claim back, work was redone, or a rule's advice was followed and proved wrong, because a gap from memory is a guess.
- **SF2** — Trace each gap to one skill and one rule (its id, or its section and quoted line), or to "missing" when no rule covers it, or to "trigger" when
  the skill loaded for work it does not cover or stayed unloaded for work it does.
- **SF3** — Quote the person's own words as evidence and paraphrase their code, file names and data, because the
  skills repo is public and the session may hold an employer's code.
- **SF4** — Propose the fix at the highest level that holds: a lint or script, then a check in a review, then a rule's
  wording, then a new rule, because a written rule only asks.
- **SF5** — Give each issue the eval case that would have caught the gap: the prompt in two lines and what a grader
  checks, because a fix without its case cannot be proved.
- **SF6** — Show every draft at once and file only those the person says yes to, because an issue is public the
  moment it is filed.

## Steps

1. **List the skills that loaded** in this session, from the rulebook plugin. If none loaded, look for work a skill
   covers that ran without it (SF2 "trigger"). Done when each skill is named with the work it was used for.
2. **Find the gaps** (SF1). Read the whole session, the part before any summary too: the harness transcript holds it
   when the context was compacted. Done when every correction, retraction and redo is listed, each with its quote.
3. **Trace each gap** (SF2). Read the rule in the installed skill and name it. Drop a gap that no skill owns:
   it is a project or harness gap, and goes in the report, not an issue. Done when each gap has skill, rule and
   whether the rule was missing, misleading, unclear or untriggered.
4. **Search for a twin.** Run `gh issue list -R chiyanram/skills --state open --search "<skill> <two key words>"`. A
   match becomes a comment draft on that issue. Done when each gap is a new issue or a comment on a named one.
5. **Draft** each issue in the shape below (SF3 to SF5).
6. **Show the drafts** and wait (SF6). File each yes with `gh issue create -R chiyanram/skills --label needs-triage`,
   or `gh issue comment` for a twin. If `gh` cannot reach the repo, print the drafts for the person to paste.
7. **Report**: one line per gap with its issue link, "comment on #N", "dropped: <why>" or "not filed".

## Issue shape

```markdown
Title: fix(<skill>): <what went wrong, at most 8 words>      (feat(<skill>): for a missing rule)

**What happened**: <the work, paraphrased> · **Expected**: <what the person wanted>
**Rule**: <id or section> · missing · trigger — <the rule's words, quoted from the skill>
**Evidence**: "<the person's words>" (<project kind, never its name>, <date>)
**Proposed fix** (<level>): <the new wording, the lint, or the check>
**Eval case**: prompt: <two lines> · grader checks: <one line>
```

## Good / Bad

**Bad**: `fix(code): code skill is too strict` — no rule, no quote, no case; nobody can act on it.

**Good**: `fix(testing): junk-test rule flags a routing swap test` — Rule: "Writing the test", its swap line quoted; Evidence: "that test is not
junk, the two ids can swap"; Proposed fix (rule wording): "test the routing of two inputs of one type"; Eval case:
a service passes `orderId` and `userId` to two calls, the grader checks the reply keeps the swap test.
