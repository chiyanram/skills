# Stack notes

The traps a model falls into on these stacks. The general rules are in [SKILL.md](SKILL.md).

## Spock

- Write each feature in labelled blocks: `given:`, `when:`, `then:`, `expect:` for a pure function, `where:` for a
  table. Name it as a plain behaviour sentence. The labels tell Spock which lines are assertions.
- A call that must return a value and be verified is one interaction. A stub in `given:` plus a count in `then:`
  makes the call return null, because the `then:` interaction replaces the stub:

  ```groovy
  // Bad: save() returns null
  given: repo.save(_) >> saved
  then:  1 * repo.save(_)
  // Good
  then:  1 * repo.save(_) >> saved
  ```

- In an argument closure, put each check on its own top-level line or use `verifyAll`. A check inside a nested
  closure is never asserted:

  ```groovy
  // Bad: the comparison inside each{} is never asserted, so any lines match
  1 * sink.write({ it.lines.each { l -> l.amount > 0 } })
  // Good
  1 * sink.write({
      verifyAll(it) {
          lines.size() == 2
          lines*.amount == [10, 20]
      }
  })
  ```

- Never give a `Stub()` a call count; Spock throws. Use a `Mock()` when the call must be verified.
- Declare a variable an interaction uses before `when:`, because interactions in `then:` are set up before `when:`
  runs.
- Check several fields with `verifyAll(obj) {}`, never Groovy `obj.with {}`, which reports one opaque failure.
- Bind an expected exception, `def e = thrown(T)`, and assert on it. A bare `thrown()` passes for any exception.
- A `where:` table reads only `@Shared` or static fields; build mocks in `given:`. Test one rule per table: no `if` on
  a column, and throwing cases in their own feature, or a failure names neither rule.
- Use `@Shared` only for an expensive read-only resource; shared mutable state makes features pass alone and fail
  together.
- Never spy the class under test. Extract the method into a collaborator and double that; a spied subject runs fakes,
  not its own code.
- In `cleanup:`, write `resource?.close()`; it runs after a failure, when the resource may be null.

## Spring Boot integration tests

- Call the API with `RestTestClient` against the real server on `RANDOM_PORT`, never MockMvc, because MockMvc skips
  the servlet stack, filters and error pages.
- Take every container from one shared singleton, never per class with `@Container`, because a cached context
  outlives a per-class container.
- Put shared properties in that singleton, not a per-class `@DynamicPropertySource`, and give a bean overridden in
  several classes the same field name. Each difference forks another cached context, which is slow and holds its own
  connection pool.
- Swap an outbound port for an in-memory fake bean, never `@MockitoBean`; a mock has no behaviour of its own. Never
  fake a repository: the query is what the test proves.
- Run one contract spec against each fake and its real adapter, so the fake cannot drift from what it replaces.
- Isolate data with a shared reset, never `@Transactional` rollback, because the server's work commits on another
  thread:

  ```groovy
  // Bad: the request's insert commits in the server thread; the rollback misses it
  @Transactional
  class OrderApiIT extends Specification { … }
  // Good
  def setup() { database.reset() }
  ```

- In `@DataJpaTest`, call `em.flush()` before asserting a constraint, because unflushed writes never reach the
  database check. Set `@AutoConfigureTestDatabase(replace = NONE)` so the slice uses real Postgres.
- For each dependency the system must survive, write one Toxiproxy test with latency, a timeout and a cut. Assert a
  predictable failure, the log and the recovery.
- Write a one-line reason beside every `@DirtiesContext`; it rebuilds the context for every later test.

## Playwright

- Find elements by role, then label or text, test id last; never a CSS class or XPath. Assert something only this
  feature renders, because shared chrome renders on every page.
- Check page state with retrying matchers, because a one-shot read runs before the page settles:

  ```ts
  // Bad: reads once
  expect(await page.getByRole('status').textContent()).toBe('Saved');
  // Good: retries until it holds or times out
  await expect(page.getByRole('status')).toHaveText('Saved');
  ```

- Never `waitForTimeout` or `networkidle`; wait on an assertion, a response or a URL.
- Never use `.first()` or `.nth()` to escape a strictness error; narrow the locator. The first match changes with the
  page.
- Await every call and `expect`, enforced by the `no-floating-promises` lint rule. An un-awaited `expect` can end the
  test green before it checks.
- Reach dependencies through a fake or a local instance. Real internet only in tests tagged `@external` that skip
  when it is unreachable, or a third-party site decides the result.
- Skip only for a named missing capability. Quarantine with `test.fixme` naming an open issue.
