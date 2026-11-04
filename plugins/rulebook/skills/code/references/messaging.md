# Messaging

How a consumer, a job or any state-changing operation survives a rerun, and what a consumer does with a message it
cannot read. Read it when you write or review a message consumer, a scheduled job, or an operation that can run twice.
The timeout, retry and idempotency-key rules for the remote calls a consumer makes are CC3, CC8 and CC9 in
`concurrency.md`.

Contents: Rules · When X, use Y · Good / Bad (MS6) · Decided edges · Review checks

## Rules

- **MS6** — Make each state-changing consumer or job safe to run twice: claim the work atomically with a unique
  constraint or row lock in the same transaction as the change, because delivery is at-least-once.
- **MS4** — Send a record that fails deserialization to a dead-letter topic, or log its topic, partition and offset and
  skip it; retry only transient failures, because a poison record fails every retry and blocks its partition.
- **MSN1** — Acknowledge or commit the offset only after the state change has committed, because acking first loses the
  message if the consumer crashes in between.
- **MSN2** — When a database change must also publish an event, write the event to an outbox in the same
  transaction and publish from there, because publishing beside the write loses or invents events on a crash.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a consumer or job that changes state | processing that is safe to run twice (MS6) | delivery is at-least-once: a crash before the offset is saved redelivers the record |
| a check for "already done" followed by the act | one atomic claim: a unique constraint or a row lock in the same transaction as the change (MS6) | a check followed by a separate act is a race |
| a step that leaves something behind: a lock, a temporary file, a half-written record, a claimed job | a marker the next run can judge stale, such as a temporary path renamed into place (MS6) | a marker the next run cannot judge turns every crash into manual cleanup |
| a record that fails deserialization | a dead-letter topic, or a log of its topic, partition and offset, with no retry (MS4) | a poison record fails every retry and blocks its partition |
| a transient failure | a retry (MS4) | it may succeed on the next attempt |
| a consumer that acknowledges or commits an offset | the ack after the state change commits (MSN1) | acking first loses the message on a crash in between |
| a database change that must also publish an event | an outbox row in the same transaction, published from there (MSN2) | publishing beside the write loses or invents events on a crash |

## Good / Bad

### MS6 — Safe to run twice: claim the work atomically

**Bad**
```java
@KafkaListener(topics = "charge-requests")
void onChargeRequested(final ChargeRequested event) {
    if (!chargeLog.existsByKey(event.chargeKey())) {
        gateway.charge(event.chargeKey(), event.amount());
        chargeLog.insert(event.chargeKey());
    }
}
```
Two deliveries of the same record both read "not seen" and both charge. A crash between the charge and the insert
leaves no trace, so the redelivery charges again.

**Good**
```java
@KafkaListener(topics = "charge-requests")
void onChargeRequested(final ChargeRequested event) {
    try {
        chargeLog.insertInProgress(event.chargeKey(), event.requestHash());
    } catch (final DuplicateKeyException alreadyClaimed) {
        replayOrReconcile(event);
        return;
    }
    final ChargeResult result = gateway.charge(event.chargeKey(), event.amount());
    chargeLog.markSucceeded(event.chargeKey(), result);
}
```
The unique key picks one winner. A rerun finds the row: SUCCEEDED replays the stored result, and IN_PROGRESS is the
marker a crash left, so `replayOrReconcile` asks the gateway about that key.

## Decided edges

- **Skip** the same-transaction claim **when** the change is a call outside the database, such as a payment gateway:
  claim with a unique key first, record the call's result after it, and on a rerun reconcile a claim left in progress
  (MS6). — **Do not skip when** every write of the operation can commit in one transaction: then the claim joins it,
  and a crash leaves nothing to reconcile (MS6). — **Confidence** medium

## Review checks

Walk every changed message consumer, scheduled job and state-changing service method.

- [ ] MS6 — For each one, find the atomic claim. A check for "already done" followed by a separate act (`SELECT` then
  `INSERT` or update) with no unique constraint or row lock in the same transaction as the change is a finding. A
  leftover the next run cannot judge stale is a finding.
- [ ] MS4 — For each consumer, find the path a deserialization failure takes. A retry of it is a finding, and so is a
  failure neither sent to a dead-letter topic nor logged with its topic, partition and offset.
- [ ] MSN1 — For each consumer, find where it acknowledges or commits the offset
  (`grep -rnE "acknowledge\(|commitSync|commitAsync|enable[.-]auto[.-]commit"`). An ack or commit that can run before
  the state change commits, such as an ack inside the transaction or auto-commit, is a finding.
- [ ] MSN2 — For each method that writes to the database, look for a broker send in the same flow
  (`grep -rnE "(kafkaTemplate|rabbitTemplate|jmsTemplate|streamBridge)\.(send|convertAndSend)"`). A send beside the
  write, instead of an outbox row in its transaction, is a finding.
