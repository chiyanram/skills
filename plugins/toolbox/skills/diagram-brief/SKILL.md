---
name: diagram-brief
description: Brief a change as a call tree in a fenced diff block, with a file:line proof for each changed step, what the message claims that the diff does not show, who calls the changed code, and what may break on a proven path. Use for /diagram-brief with a commit, a range, a pull request, staged or unstaged changes.
disable-model-invocation: true
argument-hint: "A commit, a range such as main..HEAD, a pull request number, staged, or nothing for the working tree"
---

# Diagram brief

Turn one change into a short brief a reviewer can check in a minute. The diff is the fact; the commit or pull request message is a claim. Read only; change no file.

## 1. Get the change

| argument | read |
|---|---|
| nothing | staged changes if any, else unstaged, else the last commit |
| `staged` | `git diff --cached` |
| a commit | `git show --stat <sha>`, then `git diff <sha>^ <sha>` and its message |
| a range `a..b` | `git diff a...b` and `git log a..b` |
| a pull request | its title, body and diff, read at its head commit, never the local checkout |

An empty diff gets one line, `Nothing to brief: <why>.`, and nothing else. A change to tests, docs, comments or formatting only gets `**No flow change.** <what changed>`.

## 2. Find the callers

For each changed function, class, field or endpoint, search the repo for its callers and readers. Keep one or two hops: the path the change travels, not the whole system. For a changed field, also search for its name as a string. For each reader, note whether it requires the field or handles its absence.

Stay in this repo. A caller outside it (another service, a UI, an API client) is named once, by role, in `Not checked:`.

## 3. Write the brief

Output only these parts, in this order, and skip a part that has nothing:

1. **Summary**: one bold line, built from the diff alone, saying what the code now does differently.
2. **Message vs diff**: when the message claims something the diff does not show (a missing piece, another area, other behaviour), one line: `⚠️ Message says "<quote>"; the diff <what it actually does>.` Vague or partial messages are fine.
3. **Call tree**: a fenced `diff` block. Unchanged calls start with a space, new calls with `+`, removed calls with `-`; a changed call is a `-` line followed by its `+` line. Indent one level per call depth. Number each changed step at the end of its line, `[1]`, `[2]`. Keep at most one unchanged call around each change, and at most twelve lines.
4. **Proof**: one line per numbered step, `[n] file:line · the code fact in at most six words`.
5. **Callers**: who calls each changed entry point, as `file:line`. When nothing calls new code yet, say so: `No caller yet: <symbol>`.
6. **May break**: at most three readers in this repo that break, each `⚠️ file:line · what breaks · reached from file:line`. Before listing one, walk back from the reader to an entry point and check that no guard, flag, type check or early return blocks the path. No proven path, no line. Then always `Not checked: <what lies outside the repo, by role>.`
7. **Open question**: at most one, about the change itself, that the diff cannot answer.

## Example

**Checkout now rejects an expired coupon before pricing the cart.**

⚠️ Message says "coupons expire in all channels"; the diff changes only the web checkout.

```diff
 CheckoutController.submit
   PricingService.price
+    CouponPolicy.rejectExpired         [1]
-    applyDiscount(after tax)           [2]
+    applyDiscount(before tax)          [2]
   OrderRepository.save
```

- [1] `coupon_policy.py:14` · rejects when `expires_at` passed
- [2] `pricing.py:61` · discount before `add_tax()`

Callers: `CheckoutController.submit` from `routes.py:40`. No caller yet: `CouponPolicy.extend`.

- ⚠️ `invoice.py:77` · taxes the full subtotal · reached from `checkout.py:95`

Not checked: API clients and the mobile app, outside the repo.

❓ Should carts priced before the change keep the old tax order?
