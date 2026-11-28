# Program design

How a design shows the shape of the code before anyone writes it: call trees, file trees, types and signatures, the
build order and the proof of each step. Read it when you write or review a design's call trees, file trees, types and
signatures, or its build slices and their proof, or when the build needs to change what the design approved.

## Rules

- When a design adds, removes or reroutes a call, show the call tree as a fenced `diff` (`+` new call, `-` removed
  call), because a call change left unshown gets decided late, in code review. A call that moves to a new caller is a
  reroute, even with no new function.
- Show every new, modified and deleted file as a file-tree `diff`, test files included, each with a one-line purpose,
  because a design with no test file gives the reviewer nothing to grade. A change with behaviour shows its test file
  now, even when the tests come later.
- Write new types, interfaces and public signatures in the project's language with no bodies, the caller's usage
  first, because a type left out of the design gets settled ad hoc in code. A changed public signature shows the new
  signature and its caller.
- Plan the build as slices that each run end-to-end and can be tried (curl, UI, integration test), never one step per
  layer, because a layer-only step hides a defect until the last layer lands. A wide mechanical refactor that no
  slice can land green goes expand, migrate in batches, contract.
- Name for every slice the command and test filter that prove it, and the manual step, or "Manual: none" when the
  slice has no surface to try, because a check with no named command does not get run.
- For a slice that claims a speed, memory or load effect, name the metric, the probe command, the trunk baseline
  measured before the change and the value that fails, because a perf claim with no baseline cannot fail.
- Name for every slice the AC-n it delivers, and give every AC a slice, because an AC with no slice is found missing
  only after the build.
- Plan each pull request within 400 changed lines and 15 files, generated files not counted, and make a slice past
  either limit its own ticket, because one writer and one review handle that size well.
- When slices become tickets, publish each blocker before the tickets it blocks, and give each ticket `Blocked by: #<n>`
  or `Blocked by: none (can start now)`, because a `#<n>` can name only a ticket that exists, and two people who start
  dependent slices at once build on code that is not there. A blocked ticket may start as a PR stacked on its blocker's
  branch (`crq`'s pr-readiness notes, Stacked PRs). A refactor-first ticket blocks the slices it eases. The parent lists
  the tickets in landing order, which can start now and which wait for which, and the files each may touch.
- Change an internal API by moving every caller and deleting the old one in the same change, with no compatibility shim,
  when that change fits the pull-request size limit, because a kept old path is a second way to do the task. Past the
  limit, or when no slice lands green, go expand, migrate in batches, contract (the slices rule), and delete the old
  path in the contract step.
- Do a mechanical edit across many files with a rerunnable script or codemod. Prove it on one unit done by hand
  first, and commit it in the PR, because a reviewer can rerun a script but not a hand edit.
- Move each test of the old API to assert the same behaviour through the new one. Delete a test that pins only the
  old API's internals, and name it in the PR, so the reviewer sees each deleted test with its reason.
- Put file paths, signatures and trees in the design, and only behaviour in the spec, because paths and code in a
  spec go stale fast. A behaviour a user or an outside system sees belongs in the spec.
- Settle a question that paper cannot decide, such as a layout, a state flow or a timing, with a throwaway prototype on
  its own branch, and carry only its answer and evidence into the design, because prototype code is not built to ship.
  Write the question at the prototype's top, and build none without one. Keep its state logic in one module with no I/O,
  and print the whole state after each action, because the reader judges the state flow from that printout, not from a
  UI. Put the prototype's answer on the ticket with a link to the branch, because an answer nobody can find gets asked
  again. A question that code or docs answer needs no prototype.
- During the build, leave the approved design as it is, and post each changed type, signature or file placement as a
  `[writer] DEVIATION:` note on the PR, with what, why and `file:line`, because an edit to the design makes its
  approval stale. A change that alters what an AC observes is a spec change, not a deviation: stop and ask the human.

## Good / Bad

One domain: a library that lets a member reserve a book that is out on loan.

### Show a call change as a call tree

**Bad**
```text
Checkout now asks the reservation queue before it lends a book. The old hold check
is no longer used.
```
The reader cannot see which caller makes the new call, or what replaces the hold check.

**Good**
```diff
 checkoutRoute
   lendBook
+    ReservationQueue.nextHolder(bookId, today)
+      reservationRepository.findOpen(bookId)
+    rejectIfHeldForOther
-    legacyHoldCheck
```
Each new call and the removed call show at the place they run.

### Show every file, test files included

**Bad**
```text
Files: reservation-queue.ts, checkout-route.ts
```
No test file, no purpose, and the deleted hold check is missing.

**Good**
```diff
 src
 └── reservation
+    ├── reservation-queue.ts      # NEW - picks the next member for a returned book
+    ├── reservation-queue.test.ts # NEW - covers queue order and expired reservations
~    ├── checkout-route.ts         # MODIFIED - asks the queue before it lends
-    └── legacy-hold-check.ts      # DELETED - replaced by the queue
```
The reviewer sees where each file lives, why it changes, and which test grades it.

### Write the usage, then the types with no bodies

**Bad**
```text
Add a reservation type with the book, the member and an expiry date.
The queue finds the next holder when a book comes back.
```
The prose leaves open what the queue returns when nobody waits. The build settles it ad hoc.

**Good**
```ts
const next = reservationQueue.nextHolder(bookId, today);

interface Reservation {
  bookId: BookId;
  memberId: MemberId;
  expiresOn: LocalDate;
}

type NextHolder =
  | { kind: 'member'; reservation: Reservation }
  | { kind: 'nobody' };

interface ReservationQueue {
  nextHolder(bookId: BookId, today: LocalDate): NextHolder;
}
```
The usage comes first. The return type names the "nobody waits" case before any code exists.

### Slice the build vertically

**Bad**
```text
Step 1: Add the reservations table
  Automated: npm test -- reservation-table
Step 2: Add the reservation service
  Automated: npm test -- reservation-service
Step 3: Add the reservation endpoints
  Automated: npm test -- reservation-endpoints
Step 4: Add the reserve button
  Automated: npm test -- reserve-button
```
Each step has a command, but no one can try a reservation until step 4. A defect in step 1 hides until then.

**Good**
```text
Slice 1: A member reserves a book that is out (table + service + endpoint + button)
  Delivers: AC-1, AC-2
  Automated: npm test -- reservation-queue
  Manual: curl -X POST /books/42/reservations, then see the reservation listed
Slice 2: A returned book goes to the first member in the queue
  Delivers: AC-3
  Automated: npm test -- checkout-route
  Manual: return book 42 in the UI, then see "held for you" for that member
```
Each slice runs through every layer, so a person can try it before the next slice starts.

### Name the command that proves each slice

**Bad**
```text
Slice 2: A returned book goes to the first member in the queue.
  Delivers: AC-3
  Verification: tests pass.
```
No command is named, so nobody knows which tests, and the check does not get run.

**Good**
```text
Slice 2: A returned book goes to the first member in the queue.
  Delivers: AC-3
  Automated: npm test -- checkout-route
  Manual: return book 42 in the UI, then see "held for you" for that member
```
A reviewer can run the same command and the same manual step.

## Review

Walk the whole design and every slice in it. During the build, also walk the diff against the design.

Each line is a finding, a blocker unless marked (warning).

- A call change told only in prose, with no `diff` call tree.
- A file the change touches missing from the file tree, a behaviour change with no test file, or a file with no
  purpose.
- A new type, interface or public signature the design does not show.
- A step that builds one layer alone (a table, a service, an endpoint or a screen), outside an expand-contract
  refactor.
- A slice that says only "tests pass", with no command, test filter, or manual step or "Manual: none".
- A slice with no AC-n, or an AC that no slice names.
- A plan over 400 lines or 15 files with no slice moved to its own ticket.
- A file path, signature or code block in the spec.
- Prototype code in the pull request's diff, or a prototype-backed decision with no answer and evidence.
- A prototype with no question at its top, or its answer not on the ticket.
- A ticket with no `Blocked by:` line, tickets published before their blockers, or a parent with no landing order.
- An internal API change that keeps the old path or a compatibility shim, outside an expand-contract refactor.
- A type, signature or placement in the diff that differs from the design with no `[writer] DEVIATION:` note, an edit
  to the approved design, or a note that changes what an AC observes.
