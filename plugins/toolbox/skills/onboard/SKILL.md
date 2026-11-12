---
name: onboard
description: Set up this repo for the rulebook - its build, test and run commands, which stack notes apply, and the codebase-health rule - as one block in the repo's AGENTS.md or CLAUDE.md. Use for /onboard, once per repo.
disable-model-invocation: true
---

# Onboard

Write the one block every rulebook skill needs from a project: how to build and test it, which stack notes apply, and
what the agent must care about beyond the task. Explore, show a draft, write only after a yes.

The issue tracker, labels and domain docs are a separate setup; if the repo has none, say so and leave them out.

## 1. Explore

- The front door: `Makefile`, `package.json` scripts, `./gradlew`, `./mvnw`, `justfile`. Name its targets, not the
  raw tool underneath, because that is what a person runs.
- Confirm each command by listing tasks or running its help (`make help`, `./gradlew tasks`, `npm run`). Run no build
  or test. A command you could not confirm is marked "unconfirmed".
- The stacks, from the files: Spock or Spring Boot (`build.gradle`, `pom.xml`, `src/integrationTest`), Playwright
  (`playwright.config.*`), a model SDK in the dependencies.
- `AGENTS.md` and `CLAUDE.md` at the root: which one holds the instructions, and whether it already has a
  `## Rulebook` block. A repo with no code yet gets only the lines that apply now.

## 2. Draft and ask

Show the block below, filled in, and ask one question: anything to change? Wait for the answer.

```markdown
## Rulebook

Build: `<command>` · Test: `<command>` · Integration tests: `<command>` · Run: `<command>`

Stack notes: the `testing` skill's `stack.md` applies (Spock, Spring Boot, Playwright: <the ones found>).
<Only if a model SDK was found:> Tests here call a model: read the `testing` skill's `model-calls.md`.

Codebase health: each change leaves the modules it touches no worse than it found them. If it would make one worse,
say so and propose the refactor as its own ticket. The next change being easy matters, not only this one working.
```

Leave out any line that does not apply. Point at a skill by name, never by path, because the plugin's install folder
differs per machine.

## 3. Write

- Edit the file that holds the instructions: `AGENTS.md` when `CLAUDE.md` only imports it (`@AGENTS.md`), else
  `CLAUDE.md` if it exists, else `AGENTS.md`. If neither exists, ask which to create.
- Replace an existing `## Rulebook` block in place; never append a second one, and never touch the rest of the file.
- Change no other file. Do not commit: tell the person the file is ready to review.
