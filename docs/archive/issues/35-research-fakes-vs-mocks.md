# R20 · Fakes vs mocks in integration tests — industry position

Type: wayfinder:research (AFK) · Status: closed · Assignee: claude · Blocked by: —
Part of: ../map.md · Informs: G9a

## Question

What do primary sources say about replacing collaborators in Spring integration tests: Spring Framework/Boot reference docs on @MockitoBean / @MockBean (context caching cost), Spring team blog posts, Google Testing Blog (fakes over mocks, 'Software Engineering at Google' ch. 13 test doubles), Martin Fowler 'Mocks Aren't Stubs' and 'TestDouble', Kent Beck / Uncle Bob, Testcontainers guides. Facts on context-cache fragmentation from @MockitoBean. Verdict: does the industry back 'fake ports, never @MockitoBean' (IT4)?

## Resolution (2026-10-02)

`../research/24-fakes-vs-mocks.md`. Verdict: PARTLY backed — "prefer a fake at the outbound port" is backed (SWE at Google
ch. 13, Fowler, Google "Don't Overuse Mocks", Testcontainers WireMock guide); "never @MockitoBean" as an absolute is not.
Context cache key includes every bean override (@TestBean, @MockitoBean, @MockitoSpyBean) → distinct override sets fragment
the cache (default 32, LRU). CORRECTION verified by the lead with a portable regex: 0 @MockitoBean annotations on master;
the 14 files only MENTION it in javadoc ("no @MockitoBean"); overrides are @TestBean (31 files) + @Import(FakePortsConfig).
Candidate decided edges E1–E7 for IT4.
