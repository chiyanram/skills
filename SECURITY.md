# Security policy

## Reporting a vulnerability

Report it privately through GitHub: **Security → Report a vulnerability** on this repository. Do not open a public
issue or pull request.

Include what you found, where, and how to reproduce it. You will get an answer within 5 working days.

## Handling secrets

- Credentials never go into the repository, issues, comments or commit messages; refer to them by name.
- If a secret is committed by mistake, revoke it first, then remove it from history.

## Scope

The rulebook plugin ships text that AI agents read and follow. A rule, example or role card that could lead an agent to
leak data, run untrusted code, weaken a test or a check, or obey instructions planted in a ticket, comment or file is
a security report.
