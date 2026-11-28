## Consumers outside the diff

| consumer | effect |
|---|---|
| `MemberLookupService.java:57` | Normalizes the input to `+…`, but the stored rows hold `00…`, so lookups of existing members return nothing. |
| `MemberImport.java:28` | New rows are written as `+…`; old rows stay `00…`. |
| `SmsSender.java:41` | Sends `+…`. The gateway accepts E.164, so this one is safe. |

## Ask

- Migrate `members.phone` to the new format in the same change.
- Update the description: three consumers change behaviour.

Verdict: request changes.
