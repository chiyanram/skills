# Async jobs

Read this when you write or review a message consumer or producer, a scheduled or batch job, or any state-changing
operation that can run twice.

The timeouts, retries and idempotency keys of the remote calls a consumer makes are in
[concurrency.md](concurrency.md).

## Work that can run twice

- Make each state-changing consumer, job or retried operation safe to run twice, because delivery is at-least-once
  and a job can overlap its own last run. Claim the work in one atomic step: a unique constraint or a row lock, in the
  same transaction as the change. A check for "already done" followed by a separate act is a race, and two runs both
  pass the check.
- Leave nothing behind that the next run cannot judge. A lock, a temporary file, a half-written record or a claimed
  job carries a marker the next run can call stale, such as a temporary path renamed into place, because otherwise
  every crash needs manual cleanup.

**Bad**: two runs that start before either commits both pass the check, and the member pays twice.
```java
@Transactional
public FeeOutcome chargeLateFee(final LoanId loanId) {
    if (fees.findChargedFor(loanId).isPresent()) {
        return new FeeOutcome.AlreadyCharged();
    }
    fees.charge(loanId);
    return new FeeOutcome.Charged();
}
```
**Good**: the row lock makes the second run wait, then see the fee. One transaction means a crash leaves nothing to
reconcile.
```java
@Transactional
public FeeOutcome chargeLateFee(final LoanId loanId) {
    jdbc.queryForObject("SELECT id FROM loans WHERE id = ? FOR UPDATE", UUID.class, loanId.value());
    final FeePlan plan = FeePolicy.plan(fees.stateOf(loanId));
    plan.writes().forEach(fees::apply);
    return plan.outcome();
}
```

## Consumers

- Acknowledge a message or commit its offset only after the state change commits, because an ack before it loses the
  message if the consumer crashes in between. Auto-commit and an ack inside the transaction both ack too early.
- Send a record that fails deserialization to a dead-letter topic, or log its topic, partition and offset and skip
  it. Retry only transient failures, because a poison record fails every retry and blocks its partition.

## Producers

- When a database change must also publish an event, write the event to an outbox row in the same transaction and
  publish from the outbox, because a broker send beside the write loses or invents events on a crash.

## Redis Streams and pub/sub

- Never use pub/sub for a message that must arrive; use a stream with a consumer group, because pub/sub delivers only
  to subscribers listening at that moment. Pub/sub is fine for a hint that may be lost, such as a "cache changed"
  signal backed by a TTL.
- Read a consumer group without auto-ack (`autoAcknowledge()`, `receiveAutoAck`, `NOACK`), and ack each message after
  its change commits, because an auto-acked message is lost if the consumer dies mid-work.
- Create a consumer group at `0` or at a stored id, and read from the last consumed offset, never "latest" (`$`,
  `ReadOffset.latest()`), because "latest" skips messages added between polls. "Latest" is fine only for live data
  that may be missed, such as a dashboard feed.
- On start and on a timer, reclaim pending entries idle longer than the processing time (`XAUTOCLAIM`, or `XPENDING`
  and `XCLAIM`), because no other consumer reads a dead consumer's pending entries. The sweep may run on every
  instance without a cluster lock, because a claim moves ownership atomically. Lock it if it also deletes or moves
  entries.
- Move a message whose delivery count passes a limit to a dead-letter stream, then ack it, because a poison message
  is otherwise redelivered forever.
- Cap every stream with `XADD … MAXLEN ~ n` or `MINID`, or trim it with a job, because a stream keeps every entry
  until it is trimmed and fills memory.

**Bad**: the read acks every message as it arrives. If the worker dies after the read, those returns never get a fee.
```java
final var messages = redis.opsForStream().read(
        Consumer.from("fees", "worker-1"),
        StreamReadOptions.empty().autoAcknowledge(),
        StreamOffset.create("returns", ReadOffset.lastConsumed()));
messages.forEach(lateFees::chargeFor);
```
**Good**: each message is acked after its fee commits. A crash leaves it pending, and the reclaim sweep hands it to
another worker.
```java
final var messages = redis.opsForStream().read(
        Consumer.from("fees", "worker-1"),
        StreamReadOptions.empty().count(50),
        StreamOffset.create("returns", ReadOffset.lastConsumed()));
messages.forEach(message -> {
    lateFees.chargeFor(message);
    redis.opsForStream().acknowledge("fees", message);
});
```

## Scheduled jobs

- Guard each scheduled job that changes shared data on a multi-instance service with a cluster lock: ShedLock
  (`@SchedulerLock` with `@EnableSchedulerLock` and a `LockProvider` bean), a database lock, or a CronJob with
  `concurrencyPolicy: Forbid`. Every instance otherwise runs it at once, and a skipped run is easier to recover than a
  double run. A job on its own instance's memory or disk, such as a local cache refresh, runs unlocked. A service
  that runs exactly one instance with a `Recreate` rollout needs no lock; one that can scale, or rolls out with
  overlap, does.
- Set ShedLock's `lockAtMostFor` to at least twice the job's longest run, because a job that outlives its lock runs
  twice at once. Set `lockAtLeastFor` to a minute or more, because a short job on a node whose clock lags otherwise
  lets that node start a second run.
- Give the task scheduler more than one thread once a service has a second scheduled job
  (`spring.task.scheduling.pool.size` above 1, `spring.threads.virtual.enabled: true`, or a `ThreadPoolTaskScheduler`
  bean), because Spring's default scheduler has one thread and a slow job delays the others.
- Name the time zone of every cron schedule, usually UTC (`zone = "UTC"` on `@Scheduled`, `.spec.timeZone` on a
  CronJob), because the default is the zone of whatever host runs it.
- Schedule at a minute other than 0, such as `0 17 3 * * *` in Spring (seconds first) or `17 3 * * *` in a CronJob.
  Use no `@hourly`, `@daily` or `@midnight` macro, and no minute list or step that includes 0, because jobs that many
  teams start at minute 0 load shared systems together and are delayed or dropped.

## Batch jobs

- Process a large set in chunks of a few hundred to a few thousand rows, each committed in its own transaction, never
  one transaction over every row, because one long transaction grows the persistence context and a failure loses all
  the work. The chunk method is `@Transactional` on another bean, and the caller has no transaction, because a chunk
  that joins an outer transaction commits nothing until the end. When every row gets the same new value, use one
  bulk update per id range, each in its own transaction, not one statement over the whole table.

**Bad**: each chunk joins the outer transaction. Nothing commits until the last chunk, and a failure there rolls back
every other chunk.
```java
@Transactional
void chargeOverdueFees() {
    final var today = LocalDate.now(clock);
    while (chunks.chargeNext(today, CHUNK_SIZE)) { }
}
```
**Good**: `chunks.chargeNext` is `@Transactional` on another bean. It reads up to `CHUNK_SIZE` overdue loans not yet
charged for `today`, ordered by id, charges each, and stamps the date in the same transaction. A failure loses one
chunk, and a rerun skips the stamped loans.
```java
void chargeOverdueFees() {
    final var today = LocalDate.now(clock);
    while (chunks.chargeNext(today, CHUNK_SIZE)) { }
}
```

## Deleting data

- In a job that deletes data, mark rows as deleted first, and destroy only marked rows older than a set delay,
  because a wrong filter otherwise destroys everything it matches before anyone notices. When the law or a contract
  sets a deadline to destroy data, destroy it within that deadline.
