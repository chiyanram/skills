---
name: code
description: Use when you write or review production code - where logic goes, services and controllers, types, errors, names, smells and comments - and its notes on Java, Spring beans and configuration, JPA entities and repositories, Angular, concurrency, messaging and scheduled jobs, Redis, HTTP API design and security, running a code review, and proving a change done. Lists each code notes file and when to read it.
---

# Code

Code earns its place when the next change is easy and a test can reach every decision. Everything below serves that.

## Before you change code

1. Read the code around the change and the project's own rules. A project rule wins. Where it and a rule here
   disagree, fix the disagreement in the same change.
2. Look for a change that deletes a branch, mode or layer instead of adding one. A moved branch is two copies of one
   rule, and copies diverge.
3. Add nothing for a case no current caller has: no parameter, config key, hook or pattern, because every later change
   must carry unused generality.
4. Tidy only the lines the change touches. Propose a wider tidy as its own ticket, because a tidy outside the change
   mixes two reviews into one.

## Where logic goes

- Make each decision a function with no I/O, and keep I/O in a thin method that chooses no outcome, because a test
  cannot reach a decision tangled with I/O without the I/O.
- A controller binds, delegates and shapes the response. A branch that chooses an outcome goes in a service, because
  a test cannot reach it without the web framework. An exhaustive `switch` over an outcome the service returned is
  shaping.
- Put operations that must succeed or fail together, such as a change and its audit row, in one use-case method in one
  transaction, because two calls left to the caller let one commit without the other.
- Return a response type from a controller, never a persistence entity, because an entity leaks every field it owns
  and ties the API to the schema.
- Add an interface only where two implementations exist now (a test fake counts) or at a module boundary. Imagine
  deleting each pass-through method, single-caller wrapper or one-implementation adapter inside a module; if no
  complexity comes back in its callers, remove it, because it adds a layer to trace and hides nothing.
- When callers read two or more fields of a record to decide something, move that logic onto the record.
- Keep each method under the project's complexity gate, or cyclomatic 10 if none is set. A method with more than 7
  parameters, or a change that takes a file past 1000 lines, is a finding unless a structural reason is stated.

Example of a needless interface: [examples.md](examples.md#an-interface-with-one-implementation).

## Types

- Model a closed set (states, roles, modes, outcomes) as a sealed type or enum, never string or int constants. Switch
  over it with every case listed and no `default`, because a `default` lets a new case compile and be mishandled.
- Make a forbidden field combination unbuildable with sealed variants. Check in the constructor only what the variants
  cannot exclude.
- Add a case as a sealed variant, an enum case or a table row, never a one-off `if` or a second boolean, because two
  flags that must agree drift apart. A boolean parameter that picks the operation becomes two named methods.
- Return absence as `Optional` and an empty collection as empty, never `null`. Parse external data (request bodies,
  rows, config) into domain types in the adapter, so no `null` reaches logic.
- Strengthen a type only where partiality shows: a cast, a null check, a "never happens" throw. Wrap a primitive in a
  small record when two same-typed parameters could swap or the value carries an invariant.
- Hold money as a decimal or a `long` of minor units, never `float` or `double`, because 0.10 has no exact binary form
  and totals drift.
- Persist an enum by name, never by ordinal, because a reordered enum remaps every stored row.
- Declare a field `final` unless it is reassigned after construction, because a mutable field makes the object unsafe
  to share across threads.
- Build a simple value with its constructor or a static factory. Add a builder only for a type with many optional
  parts, because a builder is a second construction API to keep in step.

## Errors

- Return a foreseeable non-success (not found, already exists, over limit) as a case of a sealed, domain-named return
  type. Throw only faults, because a thrown expected case is not in the signature and callers skip it. Use no
  `Either`: its left side does not say what failed.
- Throw a fault as an unchecked exception with a code from the one error catalogue. Return 4xx for a client error and
  500 for a fault, never 2xx with an error. Put only the catalogue message in the body and the detail in the log,
  because an exception message, stack trace or SQL in a response shows an attacker the schema.
- Map exceptions to error responses in one global handler, such as one `@RestControllerAdvice`, and declare no
  exception handler in a controller, because a local handler runs first and skips the shared, sanitised error shape.
- Validate request input once, at the boundary, and trust the types inside, because a second check drifts from the
  first.
- Handle, rethrow or log every `catch`, and keep the cause on a rethrow. Catch the narrowest type. Catch a broad type
  only at a must-not-fail boundary, with a comment. A best-effort call (a metric, an audit) logs at WARN with the
  exception and continues.
- When you catch `InterruptedException`, rethrow it or call `Thread.currentThread().interrupt()`, because a lost
  interrupt leaves the thread impossible to cancel or shut down.
- Validate and compute before you mutate, so a method that fails leaves state as it was.

Example of an expected case in the type: [examples.md](examples.md#an-expected-case-in-the-type).

## Names and smells

- Name a thing for what it holds or does: no `data`, `result`, `temp` or `item`. When no honest name comes, reshape
  the code, because a vague name hides an unclear design. A `get` or `is` method never writes.
- A method that returns a value changes no visible state, except a modifier that returns its own outcome.
- Give one family of types one naming pattern and matching signatures, and solve one problem one way, so a reader who
  learns one member can predict the rest.
- Define the predicate or literal of a rule once and call it from every site. Leave two or three similar lines inline
  when they are not one rule, because a helper shared by unrelated callers grows a flag per caller.
- In review, report any other smell from Fowler's catalogue (Feature Envy, Data Clumps, Shotgun Surgery) as
  "possible <smell>" with its cure. A smell is a judgement, so a documented project rule wins. Skip a smell that a
  running gate already fails.

## Comments

- Try a rename, an extracted method or a type before a comment. Keep a comment only for what code cannot say: a
  non-obvious reason, an outside constraint, a contract.
- Write no comment that restates the code, no banner or divider, and no commented-out code.
- Check the claim of each comment against the code before it lands, because readers act on a false comment.
- Document the contract of a public interface method (nulls, errors, side effects). Write none on an override.
- Fix the code instead of suppressing a warning that guards correctness. Scope a proven-safe suppression to one
  declaration, with a comment that says why.

## When the change touches more

Read a note only when the change matches it:

- Java, Spring, JPA, a build file, or an Angular component, template or `tsconfig`: [stack.md](stack.md).
- Threads, async work, remote calls, retries, locks, pools or caches: [concurrency.md](concurrency.md).
- A message consumer or producer, a scheduled or batch job, or work that can run twice:
  [async-jobs.md](async-jobs.md).
- Redis: [redis.md](redis.md).
- A list endpoint, a change to a published request or response, an API version, or a client of another service:
  [http-api.md](http-api.md).
- Outside input, a secret, a token, a guard or the security filter chain: [security.md](security.md).
- Reviewing a PR's code or its edits to existing tests: [review.md](review.md).
- Running or tuning any review, its passes, buckets and rounds: [review-run.md](review-run.md).
- Calling a change done, its evidence, a red check, a conflict or a quarantine: [verify.md](verify.md).
