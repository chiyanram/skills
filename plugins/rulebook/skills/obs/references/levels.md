# Log levels

Which level a log event gets. Read it when you write or review a log call, or choose the level for a caught exception.

How to write the log call itself (fields, throwable, what never to log) is in `logging.md` (LG1–LG6, LG8, LGN1).

## Rules

This file holds no rules of its own: it is the level table that `logging.md` uses. LG2 (log a failure once, where it
is handled) decides *where* a failure is logged; the table below decides *at which level*.

## When X, use Y

| the event | level | why |
|---|---|---|
| the process cannot go on (bad config at startup, out of memory) | ERROR (FATAL where the API has it), then exit | the event ends the process · OpenTelemetry exceptions in logs; Log4j `Level` · r47 :456 |
| a failure that application code did not handle: it reaches the top-level handler (5xx), or a consumer gives up on a message | ERROR, with the throwable | someone must look at it · OpenTelemetry exceptions in logs, logs data model; Log4j `Level` · r47 :457 |
| a dependency call failed and the code handled it (timeout, I/O error, retries used up, then a fallback) | WARN, once, with the throwable | not yet an error, but it may become one · OpenTelemetry exceptions in logs, logs data model; Log4j `Level` · r47 :458 |
| a single retry attempt inside a retry loop | DEBUG; the final outcome gets the one WARN | logging every attempt multiplies one failure · OpenTelemetry exceptions in logs, recording errors · r47 :459 |
| a client error: request validation fails (400), or authentication fails (401) | never ERROR; INFO or WARN is the project's choice, written in its own docs | a client fault, not a server fault · OpenTelemetry HTTP spans; OWASP Logging and Logging Vocabulary · r47 :460, :467 |
| authorization denied (403) | WARN or higher | a possible probe, which OWASP lists as an event to log · OWASP Logging and Logging Vocabulary · r47 :461 |
| an exception that shows no real problem (the client cancelled the request) | DEBUG | nothing to act on · OpenTelemetry exceptions in logs; Log4j `Level` · r47 :462 |
| a business or lifecycle event happened (order placed, job finished, service started) | INFO | it records that something happened · OpenTelemetry logs data model; Log4j `Level`; OWASP Logging Vocabulary · r47 :463 |
| diagnostic detail that helps while debugging | DEBUG | off by default in production · OpenTelemetry logs data model; Log4j `Level` · r47 :464 |
| fine-grained flow (method entry and exit, loop iterations) | TRACE | too noisy unless switched on for one logger · OpenTelemetry logs data model; Log4j `Level` · r47 :465 |

SLF4J has no FATAL, so the first row maps to ERROR there. `r47` is agent-factory
`research/47-industry-migrations-obs.md`; `:N` is a line in that file. The table comes from industry sources, not from
one project's history (operator, 2026-10-31, agent-factory#34).

## Good / Bad

None: each row of the table states its own case.

## Decided edges

- **Skip when** the request failed on the client's input (400) or credentials (401): never ERROR, and the project
  picks INFO or WARN (r47 :460, :467; the sources agree only on "not ERROR"). — **Do not skip when** the same request
  then fails inside the server: that failure is a 5xx and logs at ERROR. — **Confidence** high

## Review checks

Walk every log call added or changed in the diff, and every `catch` block that logs.

- [ ] For each log call, find its row in the table above. A level that differs from its row is a finding: an ERROR
  for a handled dependency failure or a client error, or a WARN per retry attempt.
- [ ] For each 400 or 401 log call, open the project's docs for its INFO-or-WARN choice. A level that differs from the
  choice, or an ERROR, is a finding.
