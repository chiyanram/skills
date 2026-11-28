---
description: A new use case with two foreseeable refusals. The skill should return both refusals as cases of a sealed outcome type and map them in the controller with a switch that lists every case. Today's skill teaches this in "Errors" and "Types".
expected_outcome: HoldService.reserve returns a sealed HoldOutcome with a placed case and the two refusals; HoldController switches over it with no default and gives each refusal a 4xx status.
max_turns: 12
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

/rulebook:code Add the `reserve` use case below. Show the service method, its return type, and how `HoldController` maps the result to HTTP.

A member reserves a title. The product owner lists three outcomes:

- the hold is placed;
- the member already holds this title;
- the member already has 5 holds, which is the limit.

```java
@Service
class HoldService {
    private final HoldRepository holds;

    HoldService(final HoldRepository holds) {
        this.holds = holds;
    }

    // reserve(memberId, titleId) goes here
}

@RestController
class HoldController {
    private final HoldService service;

    HoldController(final HoldService service) {
        this.service = service;
    }

    @PostMapping("/members/{memberId}/holds")
    ResponseEntity<?> reserve(@PathVariable final long memberId, @RequestBody final HoldRequest request) {
        // map the outcome here
    }
}
```

`HoldRepository` has `countByMemberId(long)`, `existsByMemberIdAndTitleId(long, long)` and `save(Hold)`.
