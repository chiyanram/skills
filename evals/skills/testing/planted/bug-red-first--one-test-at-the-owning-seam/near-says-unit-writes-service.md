The policy owns the rule, so the test belongs at its seam. Here is the test: `ReturnServiceSpec`: `when: service.returnBook(loanDueToday) then: loan.fee == Money.ZERO`.
