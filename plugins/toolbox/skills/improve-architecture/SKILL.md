---
name: improve-architecture
description: Find where the code is hard to change - shallow modules, leaking seams, logic split only for tests - and turn the one you pick into a refactor-first ticket with its pin. Use for /improve-architecture.
disable-model-invocation: true
---

# Improve architecture

**You own finding where a change is hard, and proving it. The person picks what to fix.**

## Before you start

Load the rulebook's `code` skill and read its rules on interfaces and pass-throughs; they are the bar here. Steps 2, 5
and 6 also use `crq`'s worker notes, the `grilling` skill and `planning`'s spec-review notes. If the rulebook is not
installed, stop and say this tool needs it. Never judge depth from rules you recall.

## Words

- **Module**: anything with an interface and an implementation: a method, a class, a package, a Spring service.
- **Interface**: all a caller must know to use a module: the signature, the order the calls must come in, the errors
  it returns, and the settings it reads.
- **Deep**: much behaviour behind a small interface. **Shallow**: an interface nearly as large as what it hides.
- **Seam**: the place where behaviour can change without editing that place. **Adapter**: what fills a seam.
- **Leverage**: what callers get from depth. **Locality**: what maintainers get: a change, a bug and its test in one
  place.
- **Trace**: the files a reader must open to follow one idea, such as "a reader of renew opens 3 files".

## Steps

1. **Scope.** Take the area the person names. With none, run
   `git log --since='6 months ago' --name-only --format= | sort | uniq -c | sort -rn | head -20` and look first at the
   top files, because a module nobody changes costs nothing to leave alone. Done when the scope is named in one line.
2. **Explore.** Start one read-only helper by `crq`'s worker notes. Its kickoff names the scope, the SHA, the five
   signs below and the deletion test, and asks for one row per suspect: `file:line · sign · deletion-test result`; it
   ends `ISSUES` when it has rows. With no way to start a helper, walk the scope yourself. The signs:
   - one idea that needs many small modules open at once to follow;
   - a shallow module;
   - logic split into a pure function only for a test, while the bugs sit in how it is called;
   - two modules that reach into each other past their seam;
   - code that cannot be tested through its interface.
   The **deletion test**: imagine deleting the suspect; if its complexity comes back across its callers, it earns its
   place; if it vanishes, it was a pass-through. Done when each suspect has its row.
3. **Report.** Write a Markdown file in the scratchpad folder the harness gives; with none, in
   `${TMPDIR:-/tmp}/improve-architecture/<repo>-candidates.md`. Give its absolute path. One card per candidate:

   ```markdown
   ## Candidate 2: loan rules spread across three services   (Strong)
   Files: LoanService.java, RenewalService.java, FineService.java
   Problem: a renewal rule needs all three open; each repeats the reservation check
   Solution: one Loan module owns the renewal rule and the reservation check
   Benefits: locality (one place for the rule and its test); leverage (callers call one module)
   Before / after: (a diff call tree or a mermaid graph, side by side)
   ```

   The strength is one of `Strong`, `Worth exploring` or `Speculative`. End with one **Top recommendation** and why.
   Use the project glossary's words for the domain and the words above for the shape. Name a decision record a
   candidate contradicts only when the friction is real, as
   `Contradicts ADR-0007 (one service per aggregate), but worth reopening because …`. Name the module and what moves
   into it, not its methods. Done when every candidate has Files, Problem, Solution, Benefits, Before / after and a
   strength.
4. **Ask** which candidate to explore, and wait.
5. **Grill** the chosen one with the `grilling` skill: its constraints, what sits behind the new seam, the deeper
   module's shape, which tests survive. Offer a glossary word for a new module, and a decision record when the
   person rejects a candidate for a lasting reason; write either only on their yes.
6. **Ticket.** Draft a refactor-first ticket with four parts: the candidate; its shape; its pin, the tests, snapshot
   or old-against-new diff that hold today's behaviour (a type check is not a pin, by `planning`'s spec-review
   notes); and the trace it shortens, such as "a reader of renew opens 1 file, not 3". Show it. On the person's yes,
   file it with the commands in `docs/agents/issue-tracker.md`; with no such file, give the ticket as Markdown. Done
   when the ticket is filed, given or declined.

## Review

- A candidate with no deletion test, no file list or no strength.
- An interface or a method proposed before the person picked a candidate.
- A ticket with no pin or no trace it shortens, or filed with no yes.
