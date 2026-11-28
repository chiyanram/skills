## Verdicts

| # | claim | verdict | why |
|---|---|---|---|
| 1 | null `pickupBy` | does not hold | `Reservation`'s compact constructor calls `Objects.requireNonNull(pickupBy)`. |
| 2 | `sort` throws | does not hold | `toList()` collects into a new list, like `Collectors.toList()`, so sorting it is fine. |
| 3 | wrong zone | does not hold | The `Clock` is injected, so the zone is configured. |

None of the three findings needs action. The automated reviewer is noisy on this file; approve.
