# Scheduling and batch jobs

How a scheduled or batch job runs once across instances, when it runs, how it splits large work, and how it deletes
data. Read it when you write or review a `@Scheduled` method, a CronJob, a lock on a job, a job that changes many rows,
or a job that deletes data.

Contents: Rules · When X, use Y · Good / Bad (SJ1, SJ3) · Decided edges · Review checks

A job that runs twice is safe only if each item is claimed with its change (MS6 in `messaging.md`). A job's
last-success gauge and in-flight timer are MXN3 in `metrics.md`.

## Rules

- **SJ1** — Guard each scheduled job on a multi-instance service with a cluster lock (ShedLock, a database lock) or a
  CronJob with `concurrencyPolicy: Forbid`, because every instance otherwise runs it at once.
- **SJ2** — Set ShedLock's `lockAtMostFor` well above the job's longest run, because a job that outlives its lock
  runs twice at once.
- **SJ3** — Process a large set in chunks, each committed in its own transaction, never one transaction over every
  row, because one long transaction holds locks, grows the persistence context and loses all work on failure.
- **SJ4** — Give the task scheduler more than one thread, or virtual threads, once a service has a second scheduled
  job, because Spring's default scheduler has one thread and a slow job delays the others.
- **SJ5** — Name the time zone of every cron schedule (`zone = "UTC"` on `@Scheduled`, `.spec.timeZone` on a CronJob),
  because the default is each host's zone, which differs between hosts and shifts with daylight saving.
- **SJ6** — Schedule a job off the hour and off midnight, such as at 03:17, because jobs that many teams start at
  minute 0 load shared systems together and are delayed or dropped.
- **SJ7** — In a job that deletes data, soft-delete first and destroy only after a delay, because a wrong filter
  otherwise destroys everything it matches before anyone notices.

## When X, use Y

| the job | use | why |
|---|---|---|
| runs on a service with more than one instance | `@SchedulerLock` (ShedLock) or a database lock; on Kubernetes, a CronJob with `concurrencyPolicy: Forbid` (SJ1) | a skipped run is easier to recover than a double run |
| holds a ShedLock lock | `lockAtMostFor` well above the longest run, read from the job's timer (SJ2, MXN3) | a lock that expires mid-run lets a second node start |
| changes more rows than fit in one short transaction | chunks of a few hundred to a few thousand rows, each in its own transaction (SJ3) | a failure loses one chunk, and locks and memory stay small |
| must stay in one transaction for a large set | `flush()` and `clear()` every chunk (SJ3) | the persistence context otherwise holds every entity until `OutOfMemoryError` |
| shares a scheduler with another job | `spring.task.scheduling.pool.size` above 1, or `spring.threads.virtual.enabled: true` (SJ4) | the default scheduler has one thread |
| runs on a cron schedule | an explicit zone, usually UTC (SJ5) | the host's zone differs between hosts and moves with daylight saving |
| needs a daily or hourly time | a minute other than 0, such as `0 17 3 * * *` in Spring (seconds first) or `17 3 * * *` in a CronJob (SJ6) | minute 0 is when every other job starts |
| deletes data | a soft-delete mark now, and destruction after a delay (SJ7) | a wrong filter can be undone while the data still exists |

## Good / Bad

### SJ1 — One instance runs the job

**Bad**
```java
@Scheduled(cron = "0 17 3 * * *", zone = "UTC")
void sendDueReminders() {
    reminders.sendDue();
}
```
With three instances, three copies start at 03:17 and race over the same reminders.

**Good**
```java
@Scheduled(cron = "0 17 3 * * *", zone = "UTC")
@SchedulerLock(name = "sendDueReminders", lockAtMostFor = "PT30M")
void sendDueReminders() {
    reminders.sendDue();
}
```
One instance takes the lock, and the others skip this run. The lock ends after 30 minutes at most, well above the
longest run, so a node that crashes does not block the next run.

### SJ3 — A transaction per chunk

**Bad**
```java
@Transactional
void accrueInterest() {
    accounts.streamOpen().forEach(account -> account.accrue(rates.today(account.product())));
}
```
One transaction covers every open account. The persistence context grows with each row, and a failure on the last
account rolls back all the others.

**Good**
```java
void accrueInterest() {
    Optional<Cursor> next = Optional.of(Cursor.start());
    while (next.isPresent()) {
        next = chunks.accrue(next.orElseThrow(), CHUNK_SIZE);
    }
}
```
`chunks.accrue` is a `@Transactional` method on another bean. It reads the next `CHUNK_SIZE` accounts after the cursor,
accrues each one, commits, and returns the cursor for the next chunk. A failure loses one chunk, and a rerun starts
after the last commit.

## Decided edges

- **Skip when** the law or a contract requires data to be destroyed within a deadline: destroy it within that
  deadline (SJ7). — **Do not skip when** the job only cleans up old or unused data. — **Confidence** high
- **Skip when** the service runs as exactly one instance by design and the deployment fixes it at one: no lock is
  needed (SJ1). — **Do not skip when** the instance count can scale above one. — **Confidence** high

## Review checks

Walk every `@Scheduled` method, CronJob manifest, ShedLock setting and batch job added or changed in the diff.

- [ ] SJ1 — `grep -rn "@Scheduled"`. On a service that can run more than one instance, a scheduled method with no
  `@SchedulerLock` or other cluster lock is a finding, and so is a CronJob with no `concurrencyPolicy: Forbid`.
- [ ] SJ2 — `grep -rnE "lockAtMostFor|defaultLockAtMostFor"`. A value not well above the job's longest run, or a lock
  with neither a value nor a default, is a finding.
- [ ] SJ3 — For each job that changes many rows, find its transaction boundary. One `@Transactional` over the whole
  run is a finding, unless it flushes and clears every chunk.
- [ ] SJ4 — With two or more `@Scheduled` methods in one service, no `spring.task.scheduling.pool.size` above 1, no
  `spring.threads.virtual.enabled: true` and no custom scheduler bean is a finding.
- [ ] SJ5 — `grep -rnE "@Scheduled\(.*cron"` and `grep -rn "kind: CronJob"`. A cron with no `zone`, or a CronJob with
  no `timeZone`, is a finding.
- [ ] SJ6 — For each cron expression, read its minute field (the second field in Spring, the first in a CronJob). A
  minute of 0 is a finding.
- [ ] SJ7 — For each job that deletes data, find a soft-delete mark and a later step that destroys only marked rows
  older than a set delay. A job that destroys rows when it first matches them is a finding.
