# rulebook

Generic engineering rules for coding agents. Each skill holds references, and each reference holds rules with a
reason, Good/Bad examples and review checks. One file serves the agent that writes the code and the agent that
reviews it. Project-specific values stay in each project.

The plugin ships no skills yet.

## Install

Claude Code:

```bash
claude plugin marketplace add chiyanram/skills
claude plugin install rulebook@chiyanram
```

Other agent tools:

```bash
npx skills add chiyanram/skills
```
