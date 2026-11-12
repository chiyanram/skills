# Stack notes

The traps a model falls into on these stacks. The general rules are in [SKILL.md](SKILL.md).

## Spock

- Write each feature in labelled blocks: `given:`, `when:`, `then:`, `expect:` for a pure function, `where:` for a
  table. Name it as a plain behaviour sentence.
- A call that must return a value and be verified is one interaction: `1 * repo.save(_) >> saved`. A stub in
  `given:` plus a count in `then:` returns null.
- Never give a `Stub()` a call count; use a `Mock()`.
- In an argument closure, put each check on its own top-level line or use `verifyAll`. A check inside a nested
  closure such as `every {}` is never asserted.
- Declare a variable an interaction uses before `when:`. Interactions in `then:` are set up before `when:` runs.
- Check several fields with `verifyAll(obj) {}`, never Groovy `obj.with {}`.
- Bind an expected exception, `def e = thrown(T)`, and assert on it. A bare `thrown()` passes for any exception.
- A `where:` table reads only `@Shared` or static fields; build mocks in `given:`. Test one rule per table: no `if` on
  a column, and throwing cases in their own feature.
- Use `@Shared` only for an expensive read-only resource.
- Never spy the class under test. Extract the method into a collaborator and double that.
- In `cleanup:`, write `resource?.close()`; it runs after a failure, when the resource may be null.

## Spring Boot integration tests

- Call the API with `RestTestClient` against the real server on `RANDOM_PORT`, never MockMvc: MockMvc skips the
  servlet stack, filters and error pages.
- Take every container from one shared singleton, never per class with `@Container`; a cached context outlives a
  per-class container.
- Put shared properties in that singleton, not a per-class `@DynamicPropertySource`, and give a bean overridden in
  several classes the same field name. Each difference forks another cached context.
- Swap an outbound port for an in-memory fake bean, never `@MockitoBean` or `@SpringBean`. Never fake a repository:
  the query is what the test proves.
- Run one contract spec against each fake and its real adapter, so the fake cannot drift.
- Isolate data with a shared reset, never `@Transactional` rollback. Server work commits on another thread.
- In `@DataJpaTest`, call `em.flush()` before asserting a constraint, and set
  `@AutoConfigureTestDatabase(replace = NONE)` so the slice uses real Postgres.
- For each dependency the system must survive, write one Toxiproxy test with latency, a timeout and a cut. Assert a
  predictable failure, the log and the recovery.
- Write a one-line reason beside every `@DirtiesContext`.

## Playwright

- Find elements by role, then label or text, test id last; never a CSS class or XPath. Assert something only this
  feature renders.
- Check page state with retrying matchers (`toHaveText`, `toBeVisible`), never `expect(await locator.textContent())`.
- Never `waitForTimeout` or `networkidle`; wait on an assertion, a response or a URL.
- Never use `.first()` or `.nth()` to escape a strictness error; narrow the locator.
- Await every call and `expect`, enforced by the `no-floating-promises` lint rule.
- Reach dependencies through a fake or a local instance. Real internet only in tests tagged `@external` that skip
  when it is unreachable.
- Skip only for a named missing capability. Quarantine with `test.fixme` naming an open issue.
