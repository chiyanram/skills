This needs the real database. Sketch: `given: repo.findOverdue(today) >> [loanDueYesterday] expect: service.overdue(today).size() == 1`.
