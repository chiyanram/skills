# 31d · Good/Bad — smoke / e2e rules (EA1–EA6, EB1–EB4, EC1–EC6, ED1–ED5)

Reference file: `testing/references/smoke-specs.md`. Source: agent-platform `origin/master` (read via `git show`, 2026-10-02).
Spec paths are full repo paths. Line ranges printed and verified before use.

### EA1 — Every test asserts something that fails if the feature is removed; polls aren't assertions

**Good** (real)
```ts
        const msgs = await pollHistory(
          request, latencySessionId, token,
          m => assistantTurns(m).length > preCount,
          { maxWaitMs: 150_000, intervalMs: 5_000 },
        );
        latencies.push(Date.now() - t0);

        // The reply itself, first. pollHistory returns whatever it last read when the deadline
        // passes -- it does not throw (api-helpers.ts:135) -- so the poll condition asserts
        // nothing on its own, ...
        expect(
          assistantTurns(msgs).length,
          `Turn ${turn + 1} produced no ASSISTANT reply within the deadline`,
        ).toBeGreaterThan(preCount);
```
`aruvii-ui/playwright/e2e/smoke/smoke-78-stability.spec.ts:400-414` (comment lines 408-410 elided) — the poll's condition is re-asserted as an `expect` with a message; remove chat and it fails.

**Bad** (real)
```ts
    await apiRequest(request, 'POST', `/api/sessions/${judgeSessionId}/messages`, token, {
      userMessage: 'Ready?',
    });
    await pollHistory(request, judgeSessionId, token,
      (msgs) => assistantTurns(msgs).length > 0,
      { maxWaitMs: 120_000, intervalMs: 5_000 });
```
`aruvii-ui/playwright/e2e/smoke/smoke-56-agent-judge.spec.ts:85-90` — `pollHistory` does not throw on deadline; the poll is treated as proof the judge replied, but nothing asserts it.

### EA2 — Assert a feature-only landmark by role, then label/text, test-id last; no CSS

**Good** (real)
```ts
async function openNewAgentModal(page: Page): Promise<void> {
  await page.goto('/admin/agents');
  await expect(page.getByRole('heading', { name: 'Agents', exact: true, level: 1 })).toBeVisible({ timeout: 12_000 });
  await page.getByRole('button', { name: '+ New Agent' }).first().click();
  await expect(page.getByRole('heading', { name: 'New Agent' })).toBeVisible({ timeout: 5_000 });
}
```
`aruvii-ui/playwright/e2e/smoke/smoke-55-agent-create-form.spec.ts:16-21` — landmarks are headings only this page/modal renders, located by role + accessible name. (Its `.first()` at :19 is an EC3 Bad.)

**Bad** (real)
```ts
  test('the /guardrails page loads with the Guardrails heading and a control toggle', async ({ page }) => {
    await loginViaForm(page);
    await page.goto('/guardrails', { waitUntil: 'networkidle' });
    await expect(page.getByRole('heading', { name: 'Guardrails', exact: true, level: 1 })).toBeVisible({ timeout: 12_000 });
    await expect(page.locator('.toggle-wrap').first()).toBeVisible({ timeout: 8_000 });
```
`aruvii-ui/playwright/e2e/smoke/smoke-09-guardrails.spec.ts:12-16` — "a control toggle" is a CSS class shared by every settings page (also smoke-08:62); it proves no guardrail control rendered.

### EA3 — Nothing may turn a failure green (catch, `|| true`, `?? []`, if-guarded expect, status nets)

**Good** (real)
```ts
  test('C07: PUT /trigger accepts a malformed callback URL and stores it verbatim', async ({ request, activeAgent }) => {
    // Observed contract (REQ-072 D1): AgentTriggerController.upsert() hands the value straight to
    // TriggerService.configure(), which applies no URL-format validation, so this is a 200 and the
    // value round-trips. The old [200, 400, 422] net passed whether the platform validated or not,
    // which is precisely the question this test exists to answer.
    const resp = await apiRequest(request, 'PUT', `/api/agents/${activeAgent.agentId}/trigger`, activeAgent.token, { callbackUrl: 'not-a-url', enabled: true });
    expect(resp.status()).toBe(200);
    expect((await resp.json()).data.callbackUrl, 'the malformed value is stored as given').toBe('not-a-url');
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-58-agent-triggers-feedback.spec.ts:59-67` — the 2xx-or-4xx net was replaced by one exact status plus the stored value.

**Bad** (real)
```ts
  test('DELETE a template → it disappears from the templates list', async ({ request, template }) => {
    // when — deleting the template
    expect([200, 204]).toContain((await apiRequest(request, 'DELETE', `/api/prompt-builder/templates/${template.templateId}`, template.token)).status());
    // then — it is no longer present in the list
    const json = await (await apiRequest(request, 'GET', '/api/prompt-builder/templates', template.token)).json();
    const templates: any[] = (json.data as { content?: any[] })?.content ?? (json.data as any[]) ?? [];
    expect(templates.some(t => t.name === template.templateName)).toBe(false);
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-07-prompt-builder.spec.ts:74-81` — `?? []` before a `.some(...).toBe(false)`: an error body or changed shape yields `[]` and "it disappeared" passes.

### EA4 — A test naming a tool asserts that tool's frame by name and its success

**Good** (real)
```ts
  test('T3: File tool — agent invokes file reading tool', async ({ request }) => {
    test.setTimeout(180_000);

    await apiRequest(request, 'POST', `/api/sessions/${windowSessionId}/messages`, token, {
      userMessage: `Read the file "test.txt" from /tmp using the ${fileToolName} tool.`,
    });

    const { frame, messages: msgs } = await pollForToolFrame(request, windowSessionId, token, fileToolName,
      { maxWaitMs: 150_000, intervalMs: 5_000, andAssistantReply: true });

    expect(frame, `TOOL frame for ${fileToolName} must appear — the file tool was not called`).toBeTruthy();
    expect(toolFrameSucceeded(frame), 'the file tool ran but returned an error').toBe(true);
    expect(hasAssistantReply(msgs)).toBe(true);
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-69-memory-tools-e2e.spec.ts:305-318` — frame matched by tool name, then `toolFrameSucceeded`; the reply is a third check, not the proof.

**Bad** (real — the skill's own "GOOD" example)
```ts
const { frame, messages } = await pollForToolFrame(request, sessionId, token, httpToolName,
  { maxWaitMs: 240_000, andAssistantReply: true });
expect(frame, `TOOL frame for ${httpToolName} must appear — the tool was never called`).toBeTruthy();
expect(messages.some(x => x.role?.toUpperCase() === 'ASSISTANT' && x.content?.trim())).toBe(true);
```
`.claude/skills/smoke-spec/SKILL.md:119-122` — frame exists but success is never asserted; a tool that ran and returned `{"error"}` passes.

### EA5 — Deliberate dependency failure asserts the failure shape: reply arrives, no successful frame

**Good** (real)
```ts
      const messages = await pollHistory(request, sessionId, tools.token,
        msgs => hasAssistantReply(msgs),
        { maxWaitMs: POLL_BUDGET_MS });
      expect(assistantReply(messages),
        `a non-empty ASSISTANT reply must be present within ${POLL_BUDGET_MS / 1000}s`).toBeTruthy();

      const mcpFrame = toolFrameFor(messages, tools.mcpFnName);
      expect(mcpFrame?.content ?? '{"error":"not called"}',
        'an unreachable MCP server must never produce a successful tool result').toContain('error');
```
`aruvii-ui/playwright/e2e/smoke/smoke-65-e2e-llm-tools.spec.ts:339-347` — both halves asserted: the platform still answers, and the unreachable tool never yields success.

**Bad** (adapted from smoke-65 N08 — NEEDS COMPILE CHECK)
```ts
  test('N08: MCP agent with an unreachable server', async ({ request, tools }) => {
    const mcpAgentId = await tools.createAgent(`smoke-n08-agent-${TS}`, [tools.mcpToolId], 'Answer directly.');
    const sessionId = await tools.createSession(mcpAgentId, `smoke-n08-session-${TS}`);
    await apiRequest(request, 'POST', `/api/sessions/${sessionId}/messages`, tools.token, { userMessage: 'Say hello.' });
    const messages = await pollHistory(request, sessionId, tools.token, msgs => hasAssistantReply(msgs),
      { maxWaitMs: POLL_BUDGET_MS });
    expect(assistantReply(messages)).toBeTruthy();
  });
```
`adapted from aruvii-ui/playwright/e2e/smoke/smoke-65-e2e-llm-tools.spec.ts:320-352` — reply only; a regression that returns a fake success frame for a dead server stays green. No real instance on master (N08 was repaired).

### EA6 — Skip only on a named missing capability; own setup failure throws; fixme names an open issue

**Good** (real)
```ts
  test('POST /api/tools/:id/test-connection — weather forecast host is reachable', async ({ request, weather }) => {
    test.skip(!weather.externalReachable, 'External internet not reachable from this Docker environment');
    const resp = await apiRequest(request, 'POST', `/api/tools/${weather.toolId}/test-connection`, weather.token);
    expect(resp.status()).toBe(200);
```
`aruvii-ui/playwright/e2e/smoke/smoke-41-http-tool.spec.ts:168-171` — skip keyed on one named capability (external internet), with the reason in the report.

**Bad** (real)
```ts
    try {
      const probeResp = await apiRequest(request, 'POST', '/api/platform/trusted-certificates/probe', token,
        { uri: 'https://api.open-meteo.com' }, { timeout: 15_000 });
      if (probeResp.status() === 200) {
        ...
          if ([200, 201].includes(saveResp.status())) trustedCertId = (await saveResp.json()).data.id;
        }
      }
    } catch {
      // Non-MITM or TCP-blocked — no cert to register; proceed without.
    }
```
`aruvii-ui/playwright/e2e/smoke/smoke-41-http-tool.spec.ts:46-63` (lines 50-57 elided) — the fixture's own setup (cert save) can fail at any step and is swallowed; later tests fail or skip for a reason the report never shows. No `test.fixme` exists on master today (`git grep` 0), so the quarantine half has no instance either way.

### EB1 — Users/workspaces/providers come from fixtures.ts; seeded workspace via defaultWorkspaceId, never data[0]

**Good** (real)
```ts
  test('UI: /settings/db-connections lists the created connection', async ({ page, request, adminToken }) => {
    // The page defaults its workspace selector to the NEWEST workspace (GET /api/workspaces is
    // createdAt DESC), so one created by a concurrently-running spec can steal the selection between
    // the fixture's write and the page load. Two halves, both needed: resolve the seeded 'Default'
    // rather than data[0] (#163), and pin the selector to it rather than trusting the page default.
    const workspaceId = await defaultWorkspaceId(request, adminToken);
```
`aruvii-ui/playwright/e2e/smoke/smoke-81-database-tool.spec.ts:197-202` — token from the `adminToken` fixture; seeded workspace resolved by name (helper throws if absent, `support/api-helpers.ts:95-105`).

**Bad** (real)
```ts
  test.beforeAll(async ({ request }) => {
    // Shared setup runs in beforeAll (not a per-test fixture) precisely because the session is
    // shared across the serial tests. Each create asserts its status — setup fails loud, never skips.
    token = await apiLogin(request);

    const wsResp = await apiRequest(request, 'GET', '/api/workspaces', token);
    workspaceId = (await wsResp.json()).data[0].id;
```
`aruvii-ui/playwright/e2e/smoke/smoke-16-chat-live-ollama.spec.ts:28-34` — hand-rolled `apiLogin` and `data[0]` (newest workspace = another worker's, the #309 flake); the comment's "each create asserts" is false for this read.

### EB2 — Every test passes alone; describe.serial only for one expensive shared live call, reason above

**Good** (real)
```ts
 * describe.serial is deliberate (taxonomy B5): the one live inference is expensive (60-900s on
 * CPU). Sending it once and asserting it three ways is the whole point — making each test
 * self-contained would fire three cold Ollama calls for no added coverage. The shared provider/
 * agent/session therefore live in beforeAll, and tests run in order against them.
...
test.describe.serial('[SMOKE] Live Chat — Ollama', { tag: ['@chat', '@llm', '@core'] }, () => {
```
`aruvii-ui/playwright/e2e/smoke/smoke-16-chat-live-ollama.spec.ts:8-11,20` — one live call, three read-only views of it; the reason sits above the block.

**Bad** (real)
```ts
// describe.serial + shared beforeAll state is deliberate (taxonomy B5): T1, T2, T3 and T4 send turns to
// one WINDOW session, and turns sent to one session concurrently interleave, so a test could read
// another test's reply. The cost is that a failure in one skips the rest of the chain. ...
test.describe.serial('[SMOKE-69] Memory & Tools E2E', { tag: ['@chat', '@llm', '@model:real', '@core'] }, () => {
```
`aruvii-ui/playwright/e2e/smoke/smoke-69-memory-tools-e2e.spec.ts:36-41` (39-40 elided) — four separate live calls chained through one session; the interleaving is self-inflicted (a session per test removes it), so this is not "one expensive shared call".

### EB3 — beforeAll only for read-only setup that throws on failure, never mutated by tests

**Good** (real)
```ts
  test.beforeAll(async ({ request }) => {
    const token = await apiLogin(request);
    const resp = await apiRequest(request, 'POST', '/api/tools', token, {
      name: `smoke-sheet-${TS}`,
      description: 'Spreadsheet smoke test fixture for BACKLOG-TO05.',
      type: 'SPREADSHEET', scope: 'PLATFORM',
      config: { maxRows: 1000, allowWrite: true },
    });
    expect(resp.status(), 'SPREADSHEET tool must be created for this block').toBe(201);
    toolId = (await resp.json()).data.id;
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-51-spreadsheet-tool.spec.ts:29-39` — one shared tool, creation asserted with a message, so a broken setup fails loud at the source. (The `apiLogin` is an EB1 miss.)

**Bad** (real)
```ts
  test.beforeAll(async ({ request }) => {
    const token = await apiLogin(request);
    const mk = async (scope: string) => {
      const r = await apiRequest(request, 'POST', '/api/auth/api-keys', token, { name: `smoke-${scope}-${Date.now()}`, scope, role: 'SUPER_ADMIN' });
      const d = (await r.json()).data;
      createdKeyIds.push(d.id);
      return d;
    };
    const read = await mk('READ');
    readKeyRaw = read.key ?? read.rawKey ?? read.token;
```
`aruvii-ui/playwright/e2e/smoke/smoke-06-admin.spec.ts:131-140` — create status never checked and `??` chain hides a missing key; a failed setup surfaces later as a wrong 401/403 in the tests.

### EB4 — Touch nothing we do not control: fake-llm or bundled Ollama; internet only in @external with skip

**Good** (real)
```ts
      const agent = await scriptedAgent({
        toolIds: [toolId],
        steps: [
          { type: 'toolCall', name: toolName, arguments: { path: fileName } },
          { type: 'text', content: 'I read the file.' },
        ],
      });
      agentId = agent.agentId;
      sessionId = await openSession(request, adminToken, agentId);

      // when — the user asks, and the worker plays the script through the real OllamaChatAdapter
      await send(request, adminToken, sessionId, `Read ${fileName}.`);
```
`aruvii-ui/playwright/e2e/smoke/smoke-92-scripted-model.spec.ts:87-98` — model is the `scriptedAgent` fixture over fake-llm; the tool reads a file the test wrote into the worker container. Nothing external.

**Bad** (real)
```ts
  test('F12: POST /api/tools/test-connection (dry-run) → 200 with {success, latencyMs}', async ({ request, adminToken }) => {
    ...
    const resp = await apiRequest(request, 'POST', '/api/tools/test-connection', adminToken, { type: 'HTTP', config: { baseUrl: 'https://httpbin.org', method: 'GET', path: '/get', authType: 'NONE' } });
    expect(resp.status()).toBe(200);

    const data = (await resp.json()).data;
    expect(typeof data.success).toBe('boolean');
    expect(typeof data.latencyMs).toBe('number');
    expect(data.success ? true : Boolean(data.message), 'a failed probe must say why').toBe(true);
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-59-tool-error-paths.spec.ts:157-170` (158-162 elided) — hits public httpbin.org from a `@core`, non-`@external` block (describe at :67) with no skip; the internet decides which branch runs.

### EC1 — Never wait on time or networkidle; wait on web-first assertion, response, URL, or expect.poll

**Good** (real)
```ts
    // REQ-259 AC-24: bounded poll. No LLM call is involved — there are no cases — so this is fast.
    await expect.poll(async () => {
      const r = await apiRequest(request, 'GET', `/api/agents/${activeAgent.agentId}/eval/runs/${queued.id}`, activeAgent.token);
      return (await r.json()).data.status;
    }, { timeout: 60_000, intervals: [1_000] }).toBe('COMPLETED');
```
`aruvii-ui/playwright/e2e/smoke/smoke-58-agent-triggers-feedback.spec.ts:101-105` — waits on the state that matters, with a named budget, and fails if it never arrives. (`smoke-45-agent-tabs.spec.ts:118-121` shows the `waitForResponse` form.)

**Bad** (real)
```ts
async function pollJobUntil(request: any, jobId: string, token: string, pred: (status: string) => boolean, maxWaitMs = 60_000): Promise<string> {
  const deadline = Date.now() + maxWaitMs;
  let status = '';
  while (Date.now() < deadline) {
    const resp = await apiRequest(request, 'GET', `/api/webhooks/jobs/${jobId}`, token);
    status = (await resp.json()).data.status;
    if (pred(status)) return status;
    await new Promise(r => setTimeout(r, 2_000));
  }
  return status;
}
```
`aruvii-ui/playwright/e2e/smoke/smoke-44-webhook-retry.spec.ts:18-28` — hand sleep-loop that returns silently on deadline; `expect.poll` does both jobs. The common form is `page.goto(url, { waitUntil: 'networkidle' })` (e.g. `smoke-09-guardrails.spec.ts:14`): **154 uses in 73 files**.

### EC2 — Check page state with retrying matchers; never `expect(await locator.x())`

**Good** (real)
```ts
  test('/auth/sso/complete with no token redirects to /login?error=sso_failed', async ({ page }) => {
    await page.goto('/auth/sso/complete');
    // Written as an expect on the URL rather than a bare waitForURL: the wait alone left this test
    // body with no assertion at all (REQ-072 R14), and an expect states the route as the outcome
    // rather than as a precondition for reaching the end of the function.
    await expect(page).toHaveURL(/\/login.*error=sso_failed/, { timeout: 8_000 });
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-31-sso.spec.ts:145-151` — retrying `toHaveURL` is both the wait and the assertion.

**Bad** (real)
```ts
  test('shell nav shows the "Agent Studio" link for the admin user', async ({ page }) => {
    await loginViaForm(page);
    await page.goto('/dashboard', { waitUntil: 'networkidle' });
    const studioLink = page.getByRole('link', { name: /agent studio/i });
    await expect(studioLink).toBeVisible({ timeout: 10_000 });
    expect(await studioLink.getAttribute('href')).toContain('admin/agents');
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-33-agent-studio-gallery.spec.ts:95-101` — one-shot `getAttribute` read; should be `await expect(studioLink).toHaveAttribute('href', /admin\/agents/)`. Same at :108.

### EC3 — New code: no .first()/.nth()/.last() to escape strictness; narrow by name, filter, chaining

**Good** (real)
```ts
    const row = page.getByRole('row', { name: new RegExp(provider.name) });
    await expect(row).toBeVisible({ timeout: 12_000 });
    await row.getByTestId('remove-pin-btn').click();

    // then — the confirmation names the effect, not a generic "are you sure"
    const dialog = page.getByRole('alertdialog');
    await expect(dialog).toBeVisible({ timeout: 6_000 });
    await expect(dialog).toContainText(/widens what this provider will trust/i);
```
`aruvii-ui/playwright/e2e/smoke/smoke-91-provider-trust-scope.spec.ts:133-140` — row narrowed by its accessible name (the test's own unique provider), button chained inside it; strict and unambiguous.

**Bad** (real)
```ts
    const row = page.locator('tr, [data-testid="tool-row"]').filter({ hasText: tool.toolName }).first();
    await row.locator('.row-actions button').click();
    await page.locator('.row-menu').first().waitFor({ state: 'visible', timeout: 4_000 });
    await page.locator('.row-menu .row-menu-item').first().click();

    // then — the Edit tool modal opens
    const modal = page.locator('.modal-overlay .modal, .modal').first();
```
`aruvii-ui/playwright/e2e/smoke/smoke-04-tools.spec.ts:78-84` — four `.first()` calls silence strictness over CSS unions; "first menu item" happens to be Edit today. Codebase: **109 `.first()/.last()/.nth()` in 52 files**.

### EC4 — Every Playwright call and expect is awaited; enforced by no-floating-promises over playwright/

**Good** (real)
```ts
    await expect(saveError, 'the conflict names the taken tool, not a generic failure')
      .toContainText(toolPair.takenName, { timeout: 10_000 });
    await page.screenshot({ path: 'playwright/screenshots/smoke-04-tool-rename-conflict.png', fullPage: true });

    // and — the taken name is still held by exactly one tool
    await page.keyboard.press('Escape');
    await page.getByPlaceholder('Search by name', { exact: false }).fill(toolPair.takenName);
    await expect(
      page.locator('tr, [data-testid="tool-row"]').filter({ hasText: toolPair.takenName }),
      'the rejected rename did not leave two tools sharing one name',
    ).toHaveCount(1, { timeout: 10_000 });
```
`aruvii-ui/playwright/e2e/smoke/smoke-04-tools.spec.ts:150-160` — every action and web-first matcher awaited, including the multi-line ones a grep would miss.

**Bad** (adapted — NEEDS COMPILE CHECK)
```ts
  test('UI: /tools loads without error', async ({ page }) => {
    await loginViaForm(page);
    await page.goto('/tools');
    expect(page.getByRole('heading', { name: 'Tools', exact: true })).toBeVisible();
  });
```
`adapted from aruvii-ui/playwright/e2e/smoke/smoke-17-tool-types.spec.ts:31-39` — the un-awaited `toBeVisible` returns a promise nobody reads; the test ends green before the check runs. No instance found on master (grep for un-awaited web-first matchers: 0), but nothing prevents one: ESLint covers `src/**/*.ts` only (`aruvii-ui/eslint.config.js:38`).

### EC5 — Raise a timeout only for a named slow dependency, with reason; poll budget below test timeout

**Good** (real)
```ts
  test('E2E: no raw email ever appears in a live chat over the column-policy tool', async ({ request, policy }) => {
    test.setTimeout(900_000); // live model + tool round-trip; poll up to ~15 min
    ...
      const { frame, messages } = await pollForToolFrame(request, sessionId, policy.token, TOOL_NAME,
        { maxWaitMs: 840_000, intervalMs: 10_000, andAssistantReply: true });
```
`aruvii-ui/playwright/e2e/smoke/smoke-82-db-column-policy.spec.ts:136-137,156-157` — dependency named on the line, and the 840 s poll ends before the 900 s test timeout, so the poll's message is what reports.

**Bad** (real)
```ts
  test('B01: 3 sequential turns complete without ERROR frames (latency logged)', async ({ request }) => {
    test.setTimeout(600_000);
```
`aruvii-ui/playwright/e2e/smoke/smoke-78-stability.spec.ts:376-377` — 10-minute timeout with no reason; the budget (3 × 150 s polls at :403) is derivable only by reading the loop.

### EC6 — A pass on retry is a flake: fix the cause; never add retries, serial or timeouts

**Good** (real)
```ts
    // given — the webhook enabled and saved. Wait for the PUT to land: rotate-secret operates on the
    // saved trigger row, so firing it while the save is still in flight fails under suite load.
    await webhookToggle(page).click();
    const saved = page.waitForResponse(
      (r) => /\/api\/agents\/[^/]+\/trigger$/.test(new URL(r.url()).pathname) && r.request().method() === 'PUT');
    await page.getByRole('button', { name: 'Save', exact: true }).click();
    expect((await saved).status()).toBeLessThan(400);
```
`aruvii-ui/playwright/e2e/smoke/smoke-45-agent-tabs.spec.ts:115-121` — a load-only flake fixed at its cause (a race with the save), not with a retry or a longer timeout.

**Bad** (real)
```ts
  test('T1: HTTP tool — agent fetches live weather via open-meteo', { tag: '@external' }, async ({ request }) => {
    // Extended timeout: in the full suite Ollama may be queued behind many prior LLM calls.
    // T1 takes ~25s in isolation; budget 3x headroom for worst-case queue depth.
    test.setTimeout(360_000);
```
`aruvii-ui/playwright/e2e/smoke/smoke-69-memory-tools-e2e.spec.ts:244-247` — the timeout was raised for suite contention (a 25 s test given 360 s), which hides the queueing instead of fixing it.

### ED1 — Title = scenario title; each Given/When/Then a test.step; issue annotation

**Good** (adapted from smoke-92 — NEEDS COMPILE CHECK)
```ts
  test('the memory window sends the first turn again with the second', {
    annotation: { type: 'issue', description: '#576 AC-6b' },
  }, async ({ request, adminToken, scriptedAgent, fakeLlm }) => {
    const agent = await test.step('Given a WINDOW-memory agent scripted for two plain replies', () =>
      scriptedAgent({ steps: [{ type: 'text', content: 'Noted.' }, { type: 'text', content: 'You told me earlier.' }] }));
    const sessionId = await openSession(request, adminToken, agent.agentId);
    const firstTurn = `Remember the code ALPHA-92-${agent.key.slice(-8)}.`;
    await test.step('When two turns are sent, the second after the first reply', async () => {
      await send(request, adminToken, sessionId, firstTurn);
      await pollHistory(request, sessionId, adminToken, (m) => assistantReplies(m).length >= 1, { maxWaitMs: 15_000 });
      await send(request, adminToken, sessionId, 'What was the code?');
    });
    await test.step('Then the second model call resends the first user turn', async () => {
      const sent = await fakeLlm.requests(agent.key);
      expect(messagesOf(sent[1]).filter((m) => m.role === 'user').map((m) => m.content)).toContain(firstTurn);
    });
```
`adapted from aruvii-ui/playwright/e2e/smoke/smoke-92-scripted-model.spec.ts:140-181` (try/finally cleanup omitted) — steps carry the scenario's words into the report; the annotation links the AC. Master has **0 `test.step` and 0 `annotation`** under `aruvii-ui/playwright`.

**Bad** (real)
```ts
  test('revoking an API key removes it (or marks it revoked)', async ({ request, adminToken }) => {
    // given — a key this test owns (self-contained, not created by a previous test)
    const created = await apiRequest(request, 'POST', '/api/auth/api-keys', adminToken, { name: `smoke-revoke-${Date.now()}`, scope: 'READ' });
    const keyId = (await created.json()).data.id;

    // when — it is revoked
    const resp = await apiRequest(request, 'DELETE', `/api/auth/api-keys/${keyId}`, adminToken);
    expect([200, 204]).toContain(resp.status());

    // then — it is gone from the list, or present but flagged revoked
    const listResp = await apiRequest(request, 'GET', '/api/auth/api-keys', adminToken);
    const revoked = ((await listResp.json()).data as any[]).find(k => k.id === keyId);
    expect(revoked === undefined || revoked.revoked === true).toBe(true);
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-06-admin.spec.ts:80-93` — GWT lives in comments the report never shows, no issue link, and an "or" title that is not one scenario (the either/or expect at :92 follows from it).

### ED2 — Model-reaching tests tag @model:scripted (assert recorded requests) or @model:real + @llm

**Good** (real)
```ts
      // then — recall is asserted from what the platform SENT, not from what a model said (#576 AC-6b)
      expect(assistantReplies(history), 'both scripted replies must be persisted').toHaveLength(2);
      const sent = await fakeLlm.requests(agent.key);
      expect(sent).toHaveLength(2);
      const secondCallUserTurns = messagesOf(sent[1])
        .filter((m) => m.role === 'user')
        .map((m) => m.content);
      expect(secondCallUserTurns, 'WINDOW memory must resend the first user turn').toContain(firstTurn);
      expect(secondCallUserTurns).toContain('What was the code?');
      await fakeLlm.assertConsumed(agent.key);
```
`aruvii-ui/playwright/e2e/smoke/smoke-92-scripted-model.spec.ts:172-181` (describe tagged `@model:scripted` at :54) — asserts the fake's recorded requests and the persisted history count, not the scripted words. (Same file :112 does assert scripted text — `toContain('I read the file.')` — a minor slip.)

**Bad** (real)
```ts
    const provResp = await apiRequest(request, 'POST', '/api/providers', token, { name: `smoke-sess-prov-${uid}`, providerType: 'OPENAI', config: { apiKey: 'sk-smoke' } });
...
test.describe('[SMOKE-05] Session lifecycle', { tag: ['@chat'] }, () => {
...
  test('POST a message → 200/202 and it is persisted in the session history', async ({ request, session }) => {
    // when — a user message is posted
    const resp = await apiRequest(request, 'POST', `/api/sessions/${session.sessionId}/messages`, session.token, { userMessage: 'Smoke test message — please ignore' });
    expect([200, 202]).toContain(resp.status());
```
`aruvii-ui/playwright/e2e/smoke/smoke-05-sessions.spec.ts:24,47,68-71` — posting a message sends it to a real OPENAI provider with a dummy key, yet the spec carries no `@model:*` or `@llm` tag (also an EB4 break). Only **3 of 94** spec files carry any `@model:` tag; 21 carry `@llm`.

### ED3 — The spec drives its route in the UI once and asserts every introduced status incl. refusal

**Good** (real)
```ts
  test('uploading without auth returns 401', async ({ request }) => {
    // when — a file is uploaded with no Authorization / then — 401
    const resp = await request.post(`${apiBase()}/api/tools/${toolId}/files`, {
      multipart: { file: { name: 'x.csv', mimeType: 'text/csv', buffer: Buffer.from(CSV) } },
    });
    expect(resp.status()).toBe(401);
  });

  test('listing files for an unknown tool returns 404', async ({ request, adminToken }) => {
    // when — files are listed for an unknown tool / then — 404
    const resp = await apiRequest(request, 'GET', `/api/tools/${UNKNOWN_ID}/files`, adminToken);
    expect(resp.status()).toBe(404);
  });
```
`aruvii-ui/playwright/e2e/smoke/smoke-51-spreadsheet-tool.spec.ts:110-122` — each refusal status gets its own exact test beside the 201 happy path; `:124-130` then drives `/tools` in the UI to the SPREADSHEET badge.

**Bad** (real)
```ts
  test('UI: prompt builder wizard step is interactive — first field accepts input', async ({ page }) => {
    await loginViaForm(page);
    await page.goto('/prompt-builder');
    await expect(page.getByRole('heading', { name: /prompt builder/i })).toBeVisible({ timeout: 12_000 });
    // The builder should present a form with at least one textarea or input
    const firstField = page.locator('textarea, input[type="text"]').first();
    await expect(firstField).toBeVisible({ timeout: 8_000 });
    await firstField.click();
    await firstField.fill('Smoke test prompt content');
    // Verify the value was accepted
    await expect(firstField).toHaveValue('Smoke test prompt content');
```
`aruvii-ui/playwright/e2e/smoke/smoke-24-prompt-builder-run.spec.ts:116-126` — the "Test Run" spec's only UI drive types into whichever input comes first; the test-run route is never driven in the UI, and a text box accepting text proves nothing about the feature.

### ED4 — Exactly one domain tag per spec; @llm with @core only for the core-config whitelist

**Good** (real)
```ts
test.describe('[SMOKE-74] Human-approval — live E2E cycle', { tag: ['@approvals', '@llm', '@core'] }, () => {
```
`aruvii-ui/playwright/e2e/smoke/smoke-74-human-approval.spec.ts:191` — one domain (`@approvals`); `@llm`+`@core` allowed because smoke-74's live cycle is named in the whitelist at `aruvii-ui/playwright.core.config.ts:22-28`.

**Bad** (adapted — NEEDS COMPILE CHECK)
```ts
test.describe.serial('[SMOKE] Agent Judge — LLM-as-judge eval scoring', { tag: ['@agents', '@chat', '@llm', '@core'] }, () => {
```
`adapted from aruvii-ui/playwright/e2e/smoke/smoke-56-agent-judge.spec.ts:25` — two domain tags, and `@llm`+`@core` on a spec outside the whitelist. No real instance on master: every tagged spec has exactly one domain tag (checked per file), and `@llm`+`@core` appears only on 16, 65, 69, 74 — the whitelist.

### ED5 — make smoke while developing, make smoke FULL=1 as the gate; @core only after a 0-failed full run

**Good** (real)
```ts
// Membership is the `@core` tag, not a hand-maintained file list (E10 / #41). A spec
// earns `@core` only after it passes full smoke with 0 failures (CLAUDE.md promotion
// rule) — promotion = adding the tag to its describe(s). `grep: /@core/` below selects
// them; there is no list to drift.
```
`aruvii-ui/playwright.core.config.ts:17-20` — promotion rule stated where the tier is defined, and membership is the tag the config greps.

**Bad** (real)
```ts
// Full suite: npm run smoke          (all specs, DoD gate)
// Core suite: npm run smoke:core     (this config, the @core tier, daily dev gate)
```
`aruvii-ui/playwright.core.config.ts:14-15` — names `npm run smoke` as the DoD gate; it does not deploy, so it can test stale containers. The gate is `make smoke FULL=1`, the dev loop `make smoke`.

---

## Counts

| | real | adapted | missing |
|---|---|---|---|
| Good | 20 | 1 (ED1) | 0 |
| Bad | 18 | 3 (EA5, EC4, ED4) | 0 |

## Rules with no real Good on master

- **ED1** — 0 `test.step`, 0 `annotation` under `aruvii-ui/playwright`; GWT lives in comments everywhere.

## Rules the codebase widely breaks (origin/master, 94 smoke spec files)

| rule | break | count |
|---|---|---|
| EC1 | `networkidle` | 154 uses in 73 files |
| EA2 | `page.locator('<css/tag>')` instead of role/label | 130 calls in 58 files (incl. `body`, `nav`, `textarea`) |
| EC3 | `.first()` / `.last()` / `.nth()` | 109 in 52 files |
| ED1 | no `test.step` / issue annotation | 94 of 94 files |
| ED2 | no `@model:*` tag | 91 of 94 files untagged (model-reaching subset not counted; 21 carry `@llm`) |
| EB1 | hand `apiLogin(` instead of fixture | 44 calls in 18 files |
| EB1 | workspace from `data[0]` (#309) | 7 sites in 6 files (16, 32×2, 41, 56×2, 71) |
| EA3 | `?? []` | 40 lines in 25 files (some are comments recording repairs) |
| EC4 | ESLint covers `src/**` only — `playwright/` unlinted | whole tree (`eslint.config.js:38`) |

Extra Bads seen in passing (not used above): `smoke-56-agent-judge.spec.ts:266-273` — expect only inside `if (await runBtn.isVisible().catch(() => false))`, over a CSS `.or(...).first()` (EA3 + EA2 + EC3 at once). `smoke-81-database-tool.spec.ts:210` — `page.locator('select').first()` (EA2/EC3). `smoke-69:244` — `@external` with no reachability skip (EB4).
