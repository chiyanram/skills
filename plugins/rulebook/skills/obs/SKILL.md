---
name: obs
description: Use when you write or review a log call or its level, a logger, a meter or tag, a span or observation, or the logging, metrics or tracing configuration. Lists each observability reference and when to read it.
---

# Observability

Read only the references the task needs. Each one holds Rules, When X use Y, Good / Bad, Decided edges and Review
checks, so a writer reads it top to bottom and a reviewer starts at Review checks. Where a reference cannot hold every
approved Good/Bad pair, `references/examples/<name>.md` holds them all.

<!-- index: built by `make index` from each reference; do not edit by hand -->
| reference | rule IDs | read it |
|---|---|---|
| [levels](references/levels.md) | — | when you write or review a log call, or choose the level for a caught exception |
| [logging](references/logging.md) | LG1–LG6, LG8, LGN1 | when you write or review a log call, a logger field, a `catch` block that logs, or the logging configuration |
| [metrics](references/metrics.md) | MX1–MX3, MX5, MXN1–MXN3 | when you write or review a meter, a tag, a `Timer` or histogram setting, or the metrics of an endpoint, a dependency, a pool, a queue or a job |
| [tracing](references/tracing.md) | TR1–TR3, TR5, TRN1–TRN3 | when you write or review an `Observation`, a span, a message producer or consumer, a hand-off between threads, or the tracing configuration |
<!-- /index -->
