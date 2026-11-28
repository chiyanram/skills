`reserve` returns `Optional<Hold>`: empty when the member already holds the title or has 5 holds. The controller returns 409 when it is empty and 201 otherwise.
