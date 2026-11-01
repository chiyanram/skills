# Messaging

How a consumer, a job or any state-changing operation survives a rerun, and what a consumer does with a message it
cannot read. Read it when you write or review a message consumer, a scheduled job, or an operation that can run twice.
The timeout, retry and idempotency-key rules for the remote calls a consumer makes are CC3, CC8 and CC9 in
`concurrency.md`.

Contents: Rules · When X, use Y · Good / Bad (MS6) · Decided edges · Review checks

## Rules

- **MS6** — Make each state-changing consumer or job safe to run twice: claim the work atomically with a unique
  constraint or row lock in the same transaction as the change, because delivery is at-least-once.
- **MSN1** — Acknowledge or commit the offset only after the state change has committed, because acking first loses the
  message if the consumer crashes in between.
- **MSN2** — When a database change must also publish an event, write the event to an outbox in the same
  transaction and publish from there, because publishing beside the write loses or invents events on a crash.
- **MS4** — Send a record that fails deserialization to a dead-letter topic, or log its topic, partition and offset and
  skip it; retry only transient failures, because a poison record fails every retry and blocks its partition.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a consumer or job that changes state | processing that is safe to run twice (MS6) | KAFKA design: a crash "after processing messages but before saving its position" redelivers them, "'at-least-once' semantics" · PL123: "Consumers that change state must handle duplicate records safely" (r48 :784) |
| a check for "already done" followed by the act | one atomic claim in the same transaction as the change (MS6) | ADDY api: "Claim atomically. A check followed by an act is a race" · SBS idempotency: "record a unique consumer/event pair and apply the projection in one transaction" (r48 :784) |
| a consumer that acknowledges or commits an offset | the ack after the state change commits (MSN1) | KAFKA design: saving the position before processing "corresponds to 'at-most-once' semantics" · SBS idempotency: "acknowledge only after commit." (r48 :796) |
| a database change that must also publish an event | an outbox row in the same transaction, published from there (MSN2) | PL123: "Use outbox when a service updates a database and must publish an event without a dual-write race." · SBS event-driven-messaging: "Use a transactional outbox when a database write and message must agree" (r48 :797) |
| a record that fails deserialization | a dead-letter topic, with no retry (MS4) | SK: the `DefaultErrorHandler` considers a `DeserializationException` fatal and "retries are skipped" · PL123: "Poison records block progress \| Retry topic and DLT" · SBS: "Route permanent or exhausted failures to a dead-letter destination" (r48 :790) |
| a transient failure | a retry (MS4) | PL123: "Transient failures should retry while permanent failures are isolated" (r48 :790) |

Sources: `r48 :N` is a line of agent-factory `research/48-industry-recheck-code.md`, which records each quote with
the repository and commit it was read at. KAFKA = apache/kafka `docs/design/design.md`; SK = Spring for Apache Kafka
reference `annotation-error-handling.adoc`; PL123 = jabrena/plinth `123-kafka-event-driven-patterns.md`; SBS =
rrezartprebreza/spring-boot-skills `idempotency-patterns`, `event-driven-messaging`; ADDY = addyosmani/agent-skills
`api-and-interface-design`. `68f § ID — title` is a heading of `research/68f-neutral-code.md`.

## Good / Bad

### MS6 — Safe to run twice: claim the work atomically in the change's transaction

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
(Pair: 68f § MS6 — Safe to run twice: claim the work atomically in the change's transaction. Real evidence: ledger row
MS6.)

## Decided edges

None: no source in r48 states an exception to these rules.

## Review checks

Walk every changed message consumer, scheduled job and state-changing service method.

- [ ] MS6 — For each one, find the atomic claim. A check for "already done" followed by a separate act (`SELECT` then
  `INSERT` or update) with no unique constraint or row lock in the same transaction as the change is a finding.
- [ ] MSN1 — For each consumer, find where it acknowledges or commits the offset
  (`grep -rnE "acknowledge\(|commitSync|commitAsync|enable[.-]auto[.-]commit"`). An ack or commit that can run before
  the state change commits, such as an ack inside the transaction or auto-commit, is a finding.
- [ ] MSN2 — For each method that writes to the database, look for a broker send in the same flow
  (`grep -rnE "(kafkaTemplate|rabbitTemplate|jmsTemplate|streamBridge)\.(send|convertAndSend)"`). A send beside the
  write, instead of an outbox row in its transaction, is a finding.
- [ ] MS4 — For each consumer, find the path a deserialization failure takes. A retry of it is a finding, and so is a
  failure neither sent to a dead-letter topic nor logged with its topic, partition and offset.
