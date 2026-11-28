# Stuck

How you step in when the work in this session goes round in a loop. This runs once the person says they are stuck,
or when `chief-of-staff` is already loaded in the session and one of the signals below shows.

## The signals

Step in on any one of these, and name it:

- The person corrects the same thing twice.
- The same check fails twice, for the same reason, after a change meant to fix it.
- The person says it is not working, or says the same thing failed before.

An expected red is not a signal: a bug reproduction, or a test in `crq`'s red-test stage. Inside a `crq` run the loop
is `crq`'s, so step in there only at `crq`'s fourth stop, a loop still red after 3 rounds.

## Steps

1. **Name the loop.** Say what repeated, with its `#N` and context and its `file:line`. Done when the person can see
   the repeat in one line.
2. **Give the likely cause.** Name the mechanism. Done when the cause names a symbol, a file or a value.
3. **Pick one way out.** Offer one, and say it is your pick. Done when the message holds exactly one way out:
   - A different process: diagnose by `testing`'s diagnose notes instead of a retry; grill by `grilling` instead of a
     build; split the ticket by `planning`'s program-design notes; or stop and ask the person.
   - A fix, with its `file:line`.
4. **Wait for the yes.** Start the way out only on the person's yes. Hand every way out that edits code, diagnose
   included, to `/crq <ticket>`. Run a grill by `grilling` yourself. You edit no code and no ticket, because one
   change has one driver. Done when the person said yes and the work sits with its driver.

Put the loop, the cause and the way out in one message.

## Good / Bad

### Step out of the loop

**Bad**
```text
$ ./gradlew test --tests RefundServiceTest
FAILED: NullPointerException at RefundService.java:41
$ ./gradlew test --tests RefundServiceTest
FAILED: NullPointerException at RefundService.java:41
Let me run it once more.
```
Two runs failed the same way. A third run repeats the loop and learns nothing.

**Good**
```text
The same test failed twice with the same NullPointerException at RefundService.java:41.
Likely cause: the refund reason is null when the order has no payment.
Way out: run diagnose to build a red loop. Start it?
```
The message names the loop, the cause and one way out, and waits for the yes.

## Review

Walk the message that steps in. Each line is a blocker unless marked (warning).

- A step-in with no named signal, or a step-in on an expected red.
- More than one way out, or a way out with no pick.
- A way out started, a code edit or a ticket edit before the person's yes.
