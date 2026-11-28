# Worker

Every agent that crq starts (a helper, a researcher or a reviewer) follows these rules, even when its kickoff does
not repeat them. A kickoff overrides a rule here only when it names that rule and says it overrides it.

- If you start an agent, the first line of its kickoff is `Read <path>/worker.md before anything else.`, with
  `<path>` the absolute path of the folder that holds this file, and the kickoff names the commit SHA to work on.
  Use a rulebook agent where the harness has one.
- Read `docs/agents/domain.md` before you explore, and follow the rules under its file list (the domain.md shape in
  [setup.md](setup.md)). A documented project standard wins over a rulebook rule.
- The bar in your kickoff is the whole bar. Add no check, gate, approval or review round above it.
- With no bar stated, the change must be no worse than its base and pass its own tests.
- Block only for a failing run at this head or a bug a user would hit. Report a problem the base already has in one
  line, and do not hold for it.
- Ask the person only for what crq's four stops name, a question about what the spec means or an act that cannot be
  undone, and only through `NEEDS-HUMAN` below, because crq turns it into a stop.
- Put evidence logs, run histories and long tables in a file or a PR comment, and link to them.
- End with one word, `PASS`, `ISSUES`, `BLOCKED` or `NEEDS-HUMAN` with its question, and the commit SHA you worked
  on, from your kickoff when you cannot run git, because a report with no SHA cannot be checked against the code.

For the agent that starts you: a report with no SHA is dropped, and the work goes once more to a fresh agent; a
second miss is a gap on the card, and a gap is not a pass. Give a fix round, a retry or a follow-up to a fresh agent
with the original brief, every instruction you gave after it, and the earlier report, because a resumed agent
carries the earlier round's reading into the next.
