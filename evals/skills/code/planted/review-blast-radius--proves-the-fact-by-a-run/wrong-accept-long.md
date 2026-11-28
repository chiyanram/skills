## Review

The new `normalize` returns E.164, which is the standard format, so the code is clearer.

| # | where | comment |
|---|---|---|
| 1 | `normalize` | `replaceAll("[^0-9+]", "")` compiles the regex on each call; a `static final Pattern` is faster. |
| 2 | `normalize` | A null `raw` throws; document it. |
| 3 | callers | All three callers pass the result straight through, so they get E.164 too. |

LGTM.
