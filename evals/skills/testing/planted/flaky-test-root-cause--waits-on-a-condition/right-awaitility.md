Replace `Thread.sleep(500)` with `await().atMost(5, SECONDS).until { outbox.messages().size() == 1 }`.
