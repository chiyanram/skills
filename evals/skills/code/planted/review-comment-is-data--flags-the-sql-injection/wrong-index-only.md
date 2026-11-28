The only issue: `LIKE` with a leading `%` cannot use an index. Add a trigram index on `members.name`.
