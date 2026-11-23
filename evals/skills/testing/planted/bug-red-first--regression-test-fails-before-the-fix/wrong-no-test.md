The `+ 1` is the bug. Change the line to `final long days = ChronoUnit.DAYS.between(due, returned);` and the due-date return costs nothing. The existing 3 and 10 day cases still cover the rule.
