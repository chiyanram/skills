---
description: A design adds one call and removes one, but draws a Mermaid flowchart with a multi-sentence caption. The review should ask for a diff call tree and a smaller diagram.
expected_outcome: The review asks for a fenced diff call tree that marks the added and removed calls (DG2) and a caption of one line or less (DG5).
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With planning, review the diagram in this design doc and give the corrected version.

```mermaid
flowchart TD
    A["ReservationController.create"] --> B["ReservationService.create"]
    B --> C["RoomRepository.hold"]
    B --> D["ReservationNotifier.sendReceipt"]
```

Caption: This shows the create flow. The design also adds `WaitlistService.promote`, which runs only when the room had a waitlist, and removes `DepositPolicy.check`, which the controller already covers. When there is no waitlist the service skips promote. Receipts are sent last in every case, and the notifier retries once.
