Edit 1: `CartTotals.java` — remove the unused `locale` parameter from `sum`, and drop the `Locale.ROOT` argument in `total`. `sum` has one caller and reads `locale` nowhere, so the total is unchanged.

Report: removed one vestigial parameter; no other edit.
