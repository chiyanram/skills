# Demo

## Rules

- **DM1** — Stop a call that runs past `gate.timeout`, and give the runner no more than `runner.memory_ceiling`,
  because a hung call holds the runner. See AC-1 and VB3.
- **DM2** — Write the report to `build/report` in 2 passes, because one pass misses the summary.

Bind the app to `server.port`. It answers 409 when the loan is reserved.

```yaml
server:
  port: 8080
gate.timeout: 900s
```
