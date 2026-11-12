---
description: A design plans its build as one step per layer and does not link slices to acceptance criteria. The review should ask for vertical slices and an AC-n for each slice.
expected_outcome: The review asks for end-to-end slices that can be tried (PD4) and for each slice to name its AC-n, with every AC covered (PD11).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With planning, review the build plan of this design and give a corrected plan.

```text
Spec ACs:
  AC-1 — should confirm a booking when the deposit is paid
  AC-2 — should keep a booking pending when the deposit is declined
  AC-3 — should email the guest when a booking is confirmed

## Build plan
Slice 1: add the bookings table and migration
Slice 2: add BookingRepository and BookingService
Slice 3: add BookingController and the confirmation email
```
