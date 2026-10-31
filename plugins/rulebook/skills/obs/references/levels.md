# Log levels

Which level a log event gets. Read it when you write or review a log call, or choose the level for a caught exception.

How to write the log call itself (fields, throwable, what never to log) is in `logging.md` (LG1–LG6, LG8, LGN1).

## Rules

This file holds no rules of its own: it is the level table that `logging.md` uses. LG2 in `logging.md` decides
*where* a failure is logged; the table below decides *at which level*.

## When X, use Y

| the event | use | why |
|---|---|---|
| the process cannot go on (bad config at startup, out of memory) | ERROR (FATAL where the API has it), then exit | the event ends the process · OpenTelemetry exceptions in logs; Log4j `Level` · r47 :456 |
| a failure that application code did not handle: it reaches the top-level handler (5xx), or a consumer gives up on a message | ERROR, with the throwable | someone must look at it · OpenTelemetry exceptions in logs, logs data model; Log4j `Level` · r47 :457 |
| a dependency call failed and the code handled it (timeout, I/O error, retries used up, then a fallback) | WARN, once, with the throwable | not yet an error, but it may become one · OpenTelemetry exceptions in logs, logs data model; Log4j `Level` · r47 :458 |
| a single retry attempt inside a retry loop | DEBUG; the final outcome gets the one WARN | logging every attempt multiplies one failure · OpenTelemetry exceptions in logs, recording errors · r47 :459 |
| a client error: request validation fails (400), or authentication fails (401) | never ERROR; INFO or WARN is the project's choice | a client fault, not a server fault · OpenTelemetry HTTP spans; OWASP Logging and Logging Vocabulary · r47 :460, :467 |
| authorization denied (403) | WARN or higher | a possible probe, which OWASP lists as an event to log · OWASP Logging and Logging Vocabulary · r47 :461 |
| an exception that shows no real problem (the client cancelled the request) | DEBUG | nothing to act on · OpenTelemetry exceptions in logs; Log4j `Level` · r47 :462 |
| a business or lifecycle event happened (order placed, job finished, service started) | INFO | it records that something happened · OpenTelemetry logs data model; Log4j `Level`; OWASP Logging Vocabulary · r47 :463 |
| diagnostic detail that helps while debugging | DEBUG | off by default in production · OpenTelemetry logs data model; Log4j `Level` · r47 :464 |
| fine-grained flow (method entry and exit, loop iterations) | TRACE | too noisy unless switched on for one logger · OpenTelemetry logs data model; Log4j `Level` · r47 :465 |

`r47` is agent-factory `research/47-industry-migrations-obs.md`; `:N` is a line in that file.

## Good / Bad

None: each row of the table states its own case.

## Decided edges

- **Skip when** a 400 or 401 log call is at INFO or WARN: both are allowed (r47 :460, :467). — **Do not skip when**
  the failure is the server's: it reaches the top-level handler as a 5xx and logs at ERROR (r47 :457). —
  **Confidence** high

## Review checks

Walk every log call added or changed in the diff, and every `catch` block that logs.

- [ ] For each log call, find its row in the table above. A level that differs from its row is a finding, such as an
  ERROR for a handled dependency failure or a WARN per retry attempt. A process-ending event that does not exit after
  its log call is a finding. "Once" and "with the throwable" are the LG2 and LG3 checks in `logging.md`.
- [ ] For each 400 or 401 log call, an ERROR is a finding. When the project's docs name INFO or WARN, a level that
  differs from that choice is a finding.
