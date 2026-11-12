---
name: onboard
description: Set up this repo for coding agents - find what an agent would get wrong here that the code and docs do not say, and propose only those lines for the repo's AGENTS.md or CLAUDE.md. Use for /onboard, once per repo and again when its first code lands.
disable-model-invocation: true
---

# Onboard

Find what an agent would get wrong in this repo, and propose a line for each. Nothing else.

An instruction file costs attention on every run. A line that repeats the README or describes what the code already
shows makes agents slower and worse, not better. A short or empty result is a good result: say so.

## 1. Read what is already written

Read the root `AGENTS.md` and `CLAUDE.md`, the README, `CONTRIBUTING`, and the docs they link. Anything they already
say is never proposed again. Note which file holds the instructions: `AGENTS.md` when `CLAUDE.md` only imports it
(`@AGENTS.md`), else whichever exists.

## 2. Look for traps, with evidence

Look where agents and people trip, and keep the evidence for each find:

- **Commands.** The front door (`make`, `package.json` scripts, `./gradlew`, `./mvnw`) and what CI runs that a local
  command skips. What the build needs first: Docker, a running service, an env var, a tool version. Confirm a command
  by listing tasks or reading its help; run no build or test.
- **Places not to touch.** Generated code, vendored code, files a tool rewrites (changelogs, lockfiles, router tables).
- **Two ways of doing one thing.** Two HTTP clients, two test styles, an old and a new module. The code cannot say
  which is the way forward.
- **Repeated mistakes.** `git log` for reverts, repeated `fix:` commits on the same area, and review comments that
  recur. Each is a lesson nobody wrote down.
- **Costly to learn.** A fact an agent would rebuild by reading many files: how a request flows, where config comes
  from.

## 3. Ask what the repo cannot say

Ask at most three questions, one at a time, each with your recommended answer. Ask only what step 2 could not settle:

- For each pair found: which one is the way forward?
- What do you care about that the code does not show? Offer the codebase-health rule as the recommended answer: each
  change leaves the modules it touches no worse, and a change that would make one worse says so and proposes the
  refactor as its own ticket.
- What has an agent got wrong here before?

## 4. Propose

Show a table: each proposed line, its evidence (`file:line`, a command's output, a commit), and why an agent would get
it wrong without it. Drop any line that fails that test, and any generic advice ("write clean code"), and any rule a
linter could enforce instead: say "make it a lint" for those.

If nothing survives, say "nothing to add yet" and when to run again, such as when the first code lands.

## 5. Write, after a yes

- Put the accepted lines in the file that holds the instructions, next to related text, or under `## Agent notes`
  when nothing fits. Replace your own earlier block in place; never touch other text.
- Change no other file and do not commit. Tell the person it is ready to review, and that later lessons belong to
  `/correct` when a mistake repeats.
