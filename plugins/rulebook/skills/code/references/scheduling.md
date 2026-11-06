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
  row, because one long transaction grows the persistence context and loses all work on failure.
- **SJ4** — Give the task scheduler more than one thread, or virtual threads, once a service has a second scheduled
  job, because Spring's default scheduler has one thread and a slow job delays the others.
- **SJ5** — Name the time zone of every cron schedule (`zone = "UTC"` on `@Scheduled`, `.spec.timeZone` on a CronJob),
  because the default is the scheduler's or host's zone, so the run time depends on where it runs.
- **SJ6** — Schedule a job at a minute other than 0, such as 03:17, because jobs that many teams start at minute 0
  load shared systems together and are delayed or dropped.
- **SJ7** — In a job that deletes data, soft-delete first and destroy only after a delay, because a wrong filter
  otherwise destroys everything it matches before anyone notices.

## When X, use Y

| the job | use | why |
|---|---|---|
| runs on a service with more than one instance | `@SchedulerLock` with `@EnableSchedulerLock` and a `LockProvider` bean, or a database lock; on Kubernetes, a CronJob with `concurrencyPolicy: Forbid` (SJ1) | a skipped run is easier to recover than a double run |
| holds a ShedLock lock | `lockAtMostFor` at least twice the longest run on the job's timer (SJ2, MXN3), and `lockAtLeastFor` of a minute or more | a lock that expires mid-run, or a short job on a node whose clock lags, lets a second node start |
| changes more rows than fit in one short transaction | chunks of a few hundred to a few thousand rows, each in its own transaction (SJ3) | a failure loses one chunk, and the persistence context stays small |
| shares a scheduler with another job | `spring.task.scheduling.pool.size` above 1, `spring.threads.virtual.enabled: true`, or a `ThreadPoolTaskScheduler` bean with more than one thread (SJ4) | the default scheduler has one thread |
| runs on a cron schedule | an explicit zone, usually UTC (SJ5) | the default zone is wherever the scheduler runs |
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
@SchedulerLock(name = "sendDueReminders", lockAtMostFor = "PT30M", lockAtLeastFor = "PT1M")
void sendDueReminders() {
    reminders.sendDue();
}
```
One instance takes the lock, and the others skip this run. The lock lasts at least a minute, so a node whose clock
lags cannot start a second run, and at most 30 minutes, so a node that crashes does not block the next run.
`reminders.sendDue` claims each reminder with its change (MS6) and records the job's meters (MXN3).

### SJ3 — A transaction per chunk

**Bad**
```java
@Transactional
void accrueInterest() {
    final var today = LocalDate.now(clock);
    while (chunks.accrueNext(today, CHUNK_SIZE)) {
        // each chunk joins this one transaction
    }
}
```
Each `accrueNext` call joins the outer transaction, so nothing commits until the last chunk. The persistence context
holds every account, and a failure on the last chunk rolls back all the others.

**Good**
```java
void accrueInterest() {
    final var today = LocalDate.now(clock);
    while (chunks.accrueNext(today, CHUNK_SIZE)) {
        // each call commits one chunk
    }
}
```
`chunks.accrueNext` is a `@Transactional` method on another bean. It reads up to `CHUNK_SIZE` accounts not yet
accrued for `today`, ordered by id, accrues each one, stamps the date in the same transaction (MS6), and returns
whether rows remain. A failure loses one chunk, and a rerun skips the stamped accounts. The job's meters (MXN3) sit
in the scheduled method that calls it.

## Decided edges

- **Skip when** the job acts only on its own instance's memory or disk, such as a local cache refresh: every instance
  runs it, unlocked (SJ1). — **Do not skip when** the job changes shared data. — **Confidence** high
- **Skip when** the service runs as exactly one instance and its rollout never overlaps instances (a `Recreate`
  strategy): no lock is needed (SJ1). — **Do not skip when** the instance count can scale above one, or a rolling
  deploy briefly runs two. — **Confidence** medium
- **Skip when** every row gets the same new value: one `@Modifying` statement per id range, each in its own
  transaction (SJ3, PS9 in `persistence.md`). — **Do not skip when** one statement covers every row of a large
  table. — **Confidence** high
- **Skip when** the law or a contract requires data to be destroyed within a deadline: destroy it within that
  deadline (SJ7). — **Do not skip when** the job only cleans up old or unused data. — **Confidence** high

## Review checks

Walk every `@Scheduled` method, CronJob manifest, ShedLock setting and batch job added or changed in the diff.

- [ ] SJ1 — `grep -rn "@Scheduled"`. On a service that can run more than one instance, a scheduled method that
  changes shared data with no `@SchedulerLock` or other cluster lock is a finding, and so is a CronJob with no
  `concurrencyPolicy: Forbid`. A `@SchedulerLock` with no `@EnableSchedulerLock` and no `LockProvider` bean is a
  finding.
- [ ] SJ2 — `grep -rnE "lockAtMostFor|defaultLockAtMostFor"`. A value below twice the longest run on the job's timer,
  or a lock with neither a value nor a default, is a finding.
- [ ] SJ3 — For each job that changes many rows, find its transaction boundary. One `@Transactional` over the whole
  run, or a chunk method that joins an outer transaction, is a finding.
- [ ] SJ4 — With two or more `@Scheduled` methods in one service, no `spring.task.scheduling.pool.size` above 1, no
  `spring.threads.virtual.enabled: true` and no `ThreadPoolTaskScheduler` bean with more than one thread is a finding.
- [ ] SJ5 — `grep -rn -A3 "@Scheduled"`, `grep -rn "new CronTrigger("` and `grep -rn "kind: CronJob"`, and read each
  hit. A cron with no zone, or a CronJob with no `timeZone`, is a finding.
- [ ] SJ6 — For each cron expression, read its minute field (the second field in Spring, the first in a CronJob). A
  macro (`@hourly`, `@daily`, `@midnight`), a minute of 0, or a minute list or step that includes 0 is a finding.
- [ ] SJ7 — For each job that deletes data, find a soft-delete mark and a later step that destroys only marked rows
  older than a set delay. A job that destroys rows when it first matches them is a finding.
