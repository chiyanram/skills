# Messaging

How a consumer, a job or any state-changing operation survives a rerun, and what a consumer does with a message it
cannot read. Read it when you write or review a message consumer, a scheduled job, or an operation that can run twice.
The timeout, retry and idempotency-key rules for the remote calls a consumer makes are CC3, CC8 and CC9 in
`concurrency.md`.

Contents: Rules · When X, use Y · Good / Bad (MS6) · Decided edges · Review checks

## Rules

- **MS6** — For every state-changing operation, answer "what if it runs twice, or the last run crashed halfway?";
  reconcile when the answer depends on leftovers, because a rerun on leftover partial state gives a different result.
- **MS4** — Skip a message we did not author that cannot be parsed, and log its partition and offset; never skip our own
  failures, because a retried malformed message fails again and blocks the partition.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a consumer that changes state | processing that handles a duplicate record safely (MS6) | consumers that change state must handle duplicates (pl123k :42) · no queue gives exactly-once across a consumer crash (addy api :335) |
| a check for "already done" followed by the act | one atomic claim: a unique constraint or a row lock picks the winner (MS6) | a check followed by an act is a race (addy api :173, :182, :347) |
| a step that leaves something behind: a lock, a temporary file, a half-written record, a claimed job | a marker the next run can judge stale, such as a temporary path renamed into place (MS6) | a marker the next run cannot judge turns every crash into manual cleanup (ps idempotent :15) |
| a record that cannot be parsed | a defined path for poison records; for a record we did not author, skip it and log partition and offset (MS4) | define retry, DLT, alerting and replay behaviour for poison records (pl123k :45) |

Sources, all read at a pinned commit; `:N` is a line:

- pl123k: jabrena/plinth `skills/123-java-design-patterns/references/123-kafka-event-driven-patterns.md`, @a46375a.
- addy api: addyosmani/agent-skills `skills/api-and-interface-design/SKILL.md`, @aeac41d.
- ps idempotent: pstack `skills/principle-make-operations-idempotent/SKILL.md`, @f713f14.

## Good / Bad

### MS6 — Runs twice, or crashed halfway: the answer is in the code

**Bad** (neutral)
```java
@Override
@Transactional
public CancelOutcome cancel(final UUID orderId, final UUID requestedBy, final String reason) {

    final Optional<OrderCancellation> completed = cancellationPort.findCompletedByOrderId(orderId);
    if (completed.isPresent()) {
        return new CancelOutcome.AlreadyCancelled(completed.orElseThrow());
    }
    … // PENDING cancellation row, audit row, void the invoice, order CANCELLED, row COMPLETED
    } catch (RuntimeException failure) {
        log.error("order_cancel FAILED orderId={} cancellationId={}: {}: {}", …, failure);
        cancellationEntity.setStatus(CancellationStatus.FAILED);
        cancellationRepository.save(cancellationEntity);
        throw failure;
    }
```
Two concurrent cancels both pass the check-then-act guard, and the FAILED row is rolled back with the transaction it
lives in.

**Good** (neutral)
```java
@Override
@Transactional
public CancelOutcome cancel(final CancelRequest request) {
    lockOrder(request.orderId());
    return cancellationPort.findCompletedByOrderId(request.orderId())
            .<CancelOutcome>map(CancelOutcome.AlreadyCancelled::new)
            .orElseGet(() -> cancelLocked(request));
}

private void lockOrder(final UUID orderId) {
    jdbc.queryForObject("SELECT id FROM orders WHERE id = ? FOR UPDATE", UUID.class, orderId);
}
```
The row lock makes a second run wait and then see COMPLETED; one transaction means a crash leaves nothing to reconcile.
(Real evidence: ledger row MS6.)

## Decided edges

- **Skip** the reconcile step **when** every write of the operation commits in one transaction: a crash leaves nothing
  to reconcile; the "runs twice" question still applies (MS6; the MS6 Good above; ps idempotent :22). — **Do not
  skip when** an effect sits outside that transaction, such as a broker ack or a call out: the ack and the side effect
  are not in one transaction (addy api :335). — **Confidence** medium

## Review checks

Walk every changed message consumer, scheduled job and state-changing service method.

- [ ] MS6 — For each one, answer both questions from the code. A check for "already done" followed by a separate act
  (`SELECT` then `INSERT` or update) with no unique constraint or row lock is a finding. A leftover the next run cannot
  judge stale is a finding.
- [ ] MS4 — For each consumer path that skips a record (returns or acknowledges without processing), the record failed
  to parse, we did not author it, and the log line carries partition and offset. A skip of our own failure, such as a
  downstream timeout, is a finding.
