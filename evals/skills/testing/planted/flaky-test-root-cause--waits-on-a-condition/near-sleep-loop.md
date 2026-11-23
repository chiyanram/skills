Loop: `10.times { if (outbox.messages()) return; Thread.sleep(100) }` then assert.
