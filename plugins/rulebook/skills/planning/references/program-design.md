# Program design

How a design shows the shape of the code before anyone writes it: call trees, file trees, types and signatures, the
build order and the proof of each step. Read it when you write or review a design, or when the build phase needs to
change what the design approved.

Contents: Rules · When X, use Y · Good / Bad (PD1–PD5) · Decided edges · Review checks

## Rules

- **PD1** — When a design adds or reroutes a call path, show the call tree as a fenced `diff` (`+` new call, `-`
  removed call), because an unshown call change gets decided late, in code review.
- **PD2** — Show every new, modified and deleted file as a file-tree `diff`, test files included, each with a one-line
  purpose, because a design with no test file gives the reviewer nothing to grade.
- **PD3** — Write new types, interfaces and public signatures in the project's language with no bodies, the caller's
  usage first, because a type left out of the design gets settled ad hoc in code.
- **PD4** — Plan the build as slices that each run end-to-end and can be tried (curl, UI, integration test), never one
  step per layer, because a layer-only step hides a defect until the last layer lands.
- **PD5** — Name, for every slice, the command and test filter that prove it, plus any manual step, because a check
  with no named command does not get run.
- **PD6** — Put file paths, signatures and trees in the design, never in the spec, which states behaviour only, because
  file paths and code snippets in a spec go stale quickly.
- **PD7** — During the build phase, record a change to an approved type, signature or file placement in the design
  before you code past it, because an unrecorded deviation leaves the design check judging against a guess.

## When X, use Y

| the design | use | why |
|---|---|---|
| adds, removes or reroutes a call | a call tree in a fenced `diff` (PD1) | wsff :491-501 |
| adds, changes or deletes a file | a file-tree `diff`, test files included, one purpose per file (PD2) | wsff :507-515; addy-plan :93-95 lists test files with source files |
| adds a type, an interface or a public signature | the caller's usage, then signatures with no bodies (PD3) | wsff :517; architect :9 (`not implemented` bodies), :83 (usage first) |
| touches more than one layer | vertical slices, each one tried end-to-end (PD4) | wsff :542-551; to-tickets :31; addy-plan :61-77 |
| makes one mechanical change across the whole codebase (a wide refactor) | expand, migrate in batches, contract, instead of slices (PD4 edge) | to-tickets :40 |
| lists a slice | its command, its test filter and any manual step (PD5) | create-plan :226-234, :325; addy-plan :86-89 |
| needs a file path, a signature or a tree | the design, never the spec (PD6) | to-spec :55 |
| is found wrong during the build phase | a recorded change to the design, then code (PD7) | architect :57; addy-spec :214 |

`wsff` is HumanLayer `advanced-context-engineering-for-coding-agents/wsff.md` and `create-plan` is HumanLayer
`humanlayer/.claude/commands/create_plan.md`; both are one vendor and count as one source. `architect` is pstack
`skills/architect/SKILL.md`. `to-tickets` and `to-spec` are mattpocock `skills/engineering/to-tickets/SKILL.md` and
`skills/engineering/to-spec/SKILL.md`. `addy-plan` and `addy-spec` are addy `skills/planning-and-task-breakdown/SKILL.md`
and `skills/spec-driven-development/SKILL.md`. `:N` is the line. A pair label
`(from <alias> :<line>)` names the source lines the pair is adapted from.

Operator preference, 2026-10-31 (SRC2), in whole or in part: PD1, PD2, PD3 and PD6.

## Good / Bad

One neutral domain: a library that lets a member reserve a book that is out on loan.

### PD1 — Show a call change as a call tree

**Bad** (neutral)
```text
Checkout now asks the reservation queue before it lends a book. The old hold check
is no longer used.
```
The reader cannot see which caller makes the new call, or what replaces the hold check.

**Good** (from wsff :493-501)
```diff
 checkoutRoute
   lendBook
+    ReservationQueue.nextHolder(bookId, today)
+      reservationRepository.findOpen(bookId)
+    rejectIfHeldForOther
-    legacyHoldCheck
```
Each new call and the removed call show at the place they run.

### PD2 — Show every file, test files included

**Bad** (neutral)
```text
Files: reservation-queue.ts, checkout-route.ts
```
No test file, no purpose, and the deleted hold check is missing.

**Good** (from wsff :507-515)
```diff
 src
 └── reservation
+    ├── reservation-queue.ts      # NEW - picks the next member for a returned book
+    ├── reservation-queue.test.ts # NEW - covers queue order and expired reservations
~    ├── checkout-route.ts         # MODIFIED - asks the queue before it lends
-    └── legacy-hold-check.ts      # DELETED - replaced by the queue
```
The reviewer sees where each file lives, why it changes, and which test grades it.

### PD3 — Write the usage, then the types with no bodies

**Bad** (neutral)
```text
Add a reservation type with the book, the member and an expiry date.
The queue finds the next holder when a book comes back.
```
The prose leaves open what the queue returns when nobody waits. The build settles it ad hoc.

**Good** (from architect :9, :83)
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

### PD4 — Slice the build vertically

**Bad** (from addy-plan :61-67)
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

**Good** (from addy-plan :69-75)
```text
Slice 1: A member reserves a book that is out (table + service + endpoint + button)
  Automated: npm test -- reservation-queue
  Manual: curl -X POST /books/42/reservations, then see the reservation listed
Slice 2: A returned book goes to the first member in the queue
  Automated: npm test -- checkout-route
  Manual: return book 42 in the UI, then see "held for you" for that member
```
Each slice runs through every layer, so a person can try it before the next slice starts.

### PD5 — Name the command that proves each slice

**Bad** (neutral)
```text
Slice 2: A returned book goes to the first member in the queue.
  Verification: tests pass.
```
No command is named, so nobody knows which tests, and the check does not get run.

**Good** (from create-plan :226-234)
```text
Slice 2: A returned book goes to the first member in the queue.
  Automated: npm test -- checkout-route
  Manual: return book 42 in the UI, then see "held for you" for that member
```
A reviewer can run the same command and the same manual step.

## Decided edges

- **Skip when** the change adds, removes and reroutes no call (a text, style or data-only change): no call tree. —
  **Do not skip when** an existing call moves to a new caller, even with no new function (PD1). — **Confidence** high
- **Skip when** the change has no behaviour (documents, formatting): the file tree holds no test file. — **Do not skip
  when** the change has behaviour and the design says tests come later: the test file goes in the tree now (PD2). —
  **Confidence** high
- **Skip when** the change adds no type, interface or public signature (only private code inside a body): no signature
  block. — **Do not skip when** an existing public signature changes: show the new signature and its caller (PD3). —
  **Confidence** high
- **Skip when** the change is a wide refactor that no slice can land green: sequence it as expand, migrate in
  batches, contract (to-tickets :40). — **Do not skip when** the layers only seem independent: slice it (PD4). —
  **Confidence** high
- **Skip when** a slice has no surface a person can try (a pure library function): name the command and write
  "Manual: none". — **Do not skip when** the command runs only in a pipeline: name it anyway (PD5). — **Confidence**
  medium
- **Skip when** the spec names a behaviour a user or an outside system sees (a request, a message, a screen). —
  **Do not skip when** the text names where our code lives or how a function is typed: it goes in the design, although
  addy puts a project-structure section in the spec (addy-spec :96) (operator preference, PD6). — **Confidence** high
- **Skip when** the build changes only code inside a body, and every approved type, signature and file placement holds.
  — **Do not skip when** a function needs a parameter the design did not show: record it first (architect :57, PD7). —
  **Confidence** high

## Review checks

Walk the whole design and every slice in it. During the build phase, also walk the diff against the design.

- [ ] PD1 — For each added, removed or rerouted call, find it in a fenced `diff` call tree. A call change told only in
  prose is a finding.
- [ ] PD2 — Compare the file-tree `diff` with the files the change touches. A missing file, a missing test file for a
  behaviour change, or a file with no purpose is a finding.
- [ ] PD3 — Each new type, interface and public signature appears in the design with no body, after the caller's usage.
  A type the design does not show is a finding.
- [ ] PD4 — Each slice runs end-to-end and can be tried. A step that builds one layer only (a table, a service, an
  endpoint or a screen alone) is a finding, unless it is part of an expand–contract wide refactor.
- [ ] PD5 — Each slice names a command with its test filter, and a manual step or "Manual: none". A slice that says
  only "tests pass" is a finding.
- [ ] PD6 — Search the spec for file paths, signatures and code blocks. Each one is a finding: move it to the design.
- [ ] PD7 — Compare each type, signature and file placement in the diff with the approved design. A difference that
  the design does not record is a finding.
