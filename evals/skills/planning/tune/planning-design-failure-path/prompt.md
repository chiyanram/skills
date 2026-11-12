---
description: A design for a booking service describes only the happy path of a step that charges a card and writes a booking, and names no alternative. The review should flag the missing failure behaviour and the missing alternative.
expected_outcome: The review flags the missing failure, rerun and crash-halfway behaviour (SR11) and the missing rejected alternative and accepted tradeoff (SR10).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With planning, review this design section before the approval gate and list your findings.

```text
## Design: confirm a booking
BookingService.confirm(bookingId):
  1. PaymentGateway.charge(booking.deposit)
  2. BookingRepository.save(booking.confirmed())
  3. ConfirmationMailer.send(booking.guestEmail)

We use a single service method because it is simple and fits the existing code style.
```
