# Messaging

How a consumer, a job or any state-changing operation survives a rerun, and what a consumer does with a message it
cannot read, including Redis Streams consumer groups and pub/sub. Read it when you write or review a message consumer,
a stream producer, a scheduled job, or an operation that can run twice.
The timeout, retry and idempotency-key rules for the remote calls a consumer makes are CC3, CC8 and CC9 in
`concurrency.md`.

Contents: Rules · When X, use Y · Good / Bad (MS6, MS7) · Decided edges · Review checks

## Rules

- **MS6** — Make each state-changing consumer or job safe to run twice: claim the work atomically with a unique
  constraint or row lock in the same transaction as the change, because delivery is at-least-once.
- **MS4** — Send a record that fails deserialization to a dead-letter topic, or log its topic, partition and offset and
  skip it; retry only transient failures, because a poison record fails every retry and blocks its partition.
- **MSN1** — Acknowledge or commit the offset only after the state change has committed, because acking first loses the
  message if the consumer crashes in between.
- **MSN2** — When a database change must also publish an event, write the event to an outbox in the same
  transaction and publish from there, because publishing beside the write loses or invents events on a crash.
- **MS7** — Acknowledge a stream consumer-group message only after its change commits, never with auto-ack
  (`receiveAutoAck`, `NOACK`), because an auto-acked message is lost if the consumer dies before it finishes.
- **MS8** — On start and on a timer, reclaim pending stream entries idle longer than the processing time with
  `XAUTOCLAIM`, because a dead consumer's pending messages are otherwise never processed.
- **MS9** — Move a stream message whose delivery count passes a limit to a dead-letter stream and acknowledge it,
  because a poison message is otherwise redelivered forever.
- **MS10** — Cap every stream with `XADD … MAXLEN ~` or `MINID`, because a stream keeps every entry until it is
  trimmed and fills memory.
- **MS11** — Create a consumer group at `0` or a stored id, and read from the last consumed offset, never "latest",
  when no message may be missed, because "latest" skips messages added between polls.
- **MS12** — Never use Redis pub/sub for a message that must arrive; use a stream, because pub/sub is fire-and-forget
  and drops a message no subscriber is listening for.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a consumer or job that changes state | processing that is safe to run twice (MS6) | delivery is at-least-once: a crash before the offset is saved redelivers the record |
| a check for "already done" followed by the act | one atomic claim: a unique constraint or a row lock in the same transaction as the change (MS6) | a check followed by a separate act is a race |
| a step that leaves something behind: a lock, a temporary file, a half-written record, a claimed job | a marker the next run can judge stale, such as a temporary path renamed into place (MS6) | a marker the next run cannot judge turns every crash into manual cleanup |
| a record that fails deserialization | a dead-letter topic, or a log of its topic, partition and offset, with no retry (MS4) | a poison record fails every retry and blocks its partition |
| a transient failure | a retry (MS4) | it may succeed on the next attempt |
| a consumer that acknowledges or commits an offset | the ack after the state change commits (MSN1) | acking first loses the message on a crash in between |
| a Redis Streams consumer group | an explicit `acknowledge` after the change commits; no `receiveAutoAck` (MS7) | an auto-acked message is gone when the consumer dies mid-work |
| pending entries of a consumer that died | an `XAUTOCLAIM` sweep on start and on a timer, with a minimum idle time above the processing time (MS8) | nobody else reads another consumer's pending entries |
| a stream message delivered more times than the limit | a copy on a dead-letter stream, then an ack (MS9) | it would fail and be redelivered forever |
| a producer that adds to a stream | `XADD` with `MAXLEN ~ n` or `MINID` (MS10) | a stream keeps every entry until it is trimmed |
| a new consumer group, or a consumer restart | a group created at `0` or a stored id; reads from the last consumed offset (MS11) | "latest" skips messages added while no read was waiting |
| a message that must arrive | a stream with a consumer group, not pub/sub (MS12) | pub/sub delivers only to subscribers listening at that moment |
| a database change that must also publish an event | an outbox row in the same transaction, published from there (MSN2) | publishing beside the write loses or invents events on a crash |

## Good / Bad

### MS6 — Safe to run twice: claim the work atomically in the change's transaction

**Bad**
```java
@Override
@Transactional
public CancelOutcome cancel(final CancelRequest request) {
    final Optional<OrderCancellation> completed = cancellationPort.findCompletedByOrderId(request.orderId());
    if (completed.isPresent()) {
        return new CancelOutcome.AlreadyCancelled(completed.orElseThrow());
    }
    … // cancellation row, audit row, void the invoice, order CANCELLED, row COMPLETED
}
```
A redelivered or retried cancel that starts before the first run commits passes the same check-then-act guard, and
both runs cancel.

**Good**
```java
@Override
@Transactional
public CancelOutcome cancel(final CancelRequest request) {
    lockOrder(request.orderId());
    final CancelPlan plan = CancelPolicy.plan(cancellationPort.stateOf(request.orderId()), request);
    plan.writes().forEach(cancellationWriter::apply);
    return plan.outcome();
}

private void lockOrder(final UUID orderId) {
    jdbc.queryForObject("SELECT id FROM orders WHERE id = ? FOR UPDATE", UUID.class, orderId);
}
```
The row lock makes a second run wait and then see COMPLETED; one transaction means a crash leaves nothing to reconcile.
`CancelPolicy.plan` decides with no I/O, and `cancel` only locks, reads, writes the plan and returns (SEAM1).

### MS7 — Acknowledge after the change commits

**Bad**
```java
final var messages = redis.opsForStream().read(
        Consumer.from("billing", "worker-1"),
        StreamReadOptions.empty().autoAcknowledge(),
        StreamOffset.create("orders", ReadOffset.lastConsumed()));
messages.forEach(invoices::createFor);
```
The read acknowledges every message as it arrives. If the worker dies after the read, those orders never get an
invoice.

**Good**
```java
final var messages = redis.opsForStream().read(
        Consumer.from("billing", "worker-1"),
        StreamReadOptions.empty().count(50),
        StreamOffset.create("orders", ReadOffset.lastConsumed()));
messages.forEach(message -> {
    invoices.createFor(message); // claims the order with its change (MS6)
    redis.opsForStream().acknowledge("billing", message);
});
```
Each message is acknowledged after its invoice commits. A crash leaves it pending, and the `XAUTOCLAIM` sweep (MS8)
hands it to another worker.

## Decided edges

- **Skip when** a pub/sub message is a hint that may be lost, such as a "cache changed" signal backed by a TTL: pub/sub
  is fine (MS12). — **Do not skip when** losing the message loses work or data. — **Confidence** high

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
- [ ] MS7 — `grep -rnE "receiveAutoAck|autoAcknowledge\(|NOACK"`. A hit on a consumer that changes state is a finding,
  and so is an `acknowledge` that runs before the change commits.
- [ ] MS8 — For each consumer group, find an `XAUTOCLAIM` (or `XPENDING` and `XCLAIM`) sweep on start and on a timer.
  A group with none is a finding.
- [ ] MS9 — For each consumer group, find a delivery-count limit and a dead-letter stream. Either one missing is a
  finding.
- [ ] MS10 — `grep -rnE "\.add\(|XADD"` on stream producers. An add with no `MAXLEN` or `MINID`, and no trim job, is a
  finding.
- [ ] MS11 — For each consumer group, read where it is created and the offset it reads. A group created at `$` or a
  read at `ReadOffset.latest()` where no message may be missed is a finding.
- [ ] MS12 — `grep -rnE "convertAndSend|\.publish\(|PUBLISH|MessageListenerAdapter"`. Pub/sub carrying work or data
  that must arrive is a finding.
- [ ] MSN2 — For each method that writes to the database, look for a broker send in the same flow
  (`grep -rnE "(kafkaTemplate|rabbitTemplate|jmsTemplate|streamBridge)\.(send|convertAndSend)"`). A send beside the
  write, instead of an outbox row in its transaction, is a finding.
