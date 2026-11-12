---
type: llm
---

Check SC21: a method with a proxied annotation is called only from another bean, because a `this` call bypasses the proxy and the transaction never starts.

PASS if the review says `confirmAll` calls `confirmOne` on `this`, so `@Transactional` does not apply, and recommends moving it to a second bean.

FAIL if the self-call is not flagged, or the review says the transaction works.
