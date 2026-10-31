---
name: obs
description: Use when you write or review a log call or its level, a logger, a meter or tag, a span or observation, or the logging, metrics or tracing configuration. Lists each observability reference and when to read it.
---

# Observability

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

| reference | rule IDs | read it when |
|---|---|---|
| [levels](references/levels.md) | — | you choose the level of a log call or of a caught exception |
| [logging](references/logging.md) | LG1–LG6, LG8, LGN1 | you write or review a log call, a logger field, a `catch` that logs, or the logging configuration |
| [metrics](references/metrics.md) | MX1–MX3, MX5, MXN1–MXN3 | you write or review a meter, a tag, a timer or histogram setting, or the metrics of an endpoint, an outbound dependency, a pool, a queue or a job |
| [tracing](references/tracing.md) | TR1–TR3, TR5, TRN1–TRN3 | you write or review a span or observation, a message producer or consumer, a thread hand-off, or the tracing configuration |
