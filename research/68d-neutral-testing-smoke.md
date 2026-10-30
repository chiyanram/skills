# 68d — Neutral Good/Bad pairs: smoke / e2e specs, Playwright TypeScript (#99, map #9)

Source: research/31d-v2.md (fixes for ED5 from research/47-good-rewrites.md). Domain: ordering + billing (#99 brief). Stand-ins: `adminToken` → `clerkToken` fixture; `loginViaForm(page)` in a Good → `clerkPage` fixture (a page signed in as CLERK, from fixtures.ts — EB1); fake-llm / `scriptedAgent` → `fakeGateway` (FakePaymentGateway fixture: `declineNext`, `goOffline`, `requests`, `assertConsumed`, `url`); TOOL frame / `toolFrameSucceeded` → a Payment record for a named gateway with `outcome === 'APPROVED'`; unreachable MCP server → FakePaymentGateway set offline; live Ollama call → payment-provider sandbox confirmation (external, slow); `@model:scripted` / `@model:real` / `@llm` → `@gateway:fake` / `@gateway:real` / `@external`; `defaultWorkspaceId` → `seededCustomerId` (by seeded email, throws if absent); workspace `data[0]` → customer `data[0]`; domain tags `@chat` / `@agents` / `@approvals` → `@orders` / `@billing`; open-meteo + trusted-cert probe → external tax-rate host `TAX_RATE_HOST`; public `httpbin.org` kept as the third-party site; `make smoke` / `make smoke FULL=1` / `npm run smoke` kept (the rule names them). Added terms: Payment.gateway, Payment.outcome APPROVED|DECLINED; routes `/orders`, `/orders/{id}`, `/invoices`; endpoints `/api/customers`, `/api/invoices/{id}/payments`, `/api/payment-gateway/test-connection`, `/api/tax-rates/probe`, `/api/tax-rates/sources`; fixtures `clerkToken`, `clerkPage`, `placedOrder`, `draftOrder`, `invoice`, `sandbox`, `taxSource`, `goldCustomerId`; helpers `apiRequest`, `pollInvoice`, `invoiceStatus`, `pollForPayment`, `placeOrder`, `seededCustomerId`, `canReach`; UI labels "New order", "View invoice", "Due date", "Save", "Customer" / "Status" comboboxes.
Skipped: ED1 — DROPPED (2026-10-04, duplicate of GT1/GT2/GT4).

### EA1 — A poll is not an assertion

**Bad** (neutral)
```ts
await apiRequest(request, 'POST', `/api/invoices/${invoiceId}/payments`, token, {
  amount: { amount: '42.00', currency: 'EUR' },
});
await pollInvoice(request, invoiceId, token,
  (inv) => inv.status === 'PAID',
  { maxWaitMs: 30_000, intervalMs: 1_000 });
```
What goes wrong: the poll returns silently at its deadline, so the test passes when the invoice never becomes PAID.

**Good** (neutral)
```ts
await test.step('Then the invoice reaches PAID within the deadline', async () => {
  await expect
    .poll(() => invoiceStatus(request, clerkToken, placedOrder.invoiceId), {
      timeout: 20_000,
      message: `invoice ${placedOrder.invoiceId} was not PAID within 20 s`,
    })
    .toBe('PAID');
});
```
Why: `expect.poll` makes the condition an assertion with a message and a budget below the test timeout, so removing payments makes the test fail.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-56-agent-judge.spec.ts:85-90` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:46 · fix from research/31d-v2.md:26

### EA2 — Assert a feature-only landmark by role, not a shared CSS class

**Bad** (neutral)
```ts
test('the invoice list loads with the Invoices heading and a status filter', async ({ clerkPage }) => {
  await clerkPage.goto('/invoices');
  await expect(clerkPage.getByRole('heading', { name: 'Invoices', exact: true, level: 1 })).toBeVisible();
  await expect(clerkPage.locator('.toggle-wrap')).toBeVisible();
```
What goes wrong: `.toggle-wrap` is a CSS class every settings page renders, so it proves no invoice filter rendered.

**Good** (neutral)
```ts
test(
  'should show the invoice list with its status filter',
  { annotation: { type: 'issue', description: '#123 AC-1' } },
  async ({ clerkPage }) => {
    await test.step('When the clerk opens the invoice list', async () => {
      await clerkPage.goto('/invoices');
    });
    await test.step('Then the list heading and its status filter render', async () => {
      await expect(clerkPage.getByRole('heading', { name: 'Invoices', exact: true, level: 1 })).toBeVisible();
      await expect(clerkPage.getByRole('combobox', { name: 'Status' })).toBeVisible();
    });
  },
);
```
Why: the heading and the named combobox render only on the invoice list, and both are found by role and name.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-09-guardrails.spec.ts:12-16` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:72 · fix from research/31d-v2.md:60

### EA3 — No status net or `?? []` default before a check

**Bad** (neutral)
```ts
test('DELETE a draft order → it disappears from the orders list', async ({ request, draftOrder }) => {
  // when — deleting the draft order
  expect([200, 204]).toContain((await apiRequest(request, 'DELETE', `/api/orders/${draftOrder.id}`, draftOrder.token)).status());
  // then — it is no longer present in the list
  const json = await (await apiRequest(request, 'GET', '/api/orders?status=DRAFT', draftOrder.token)).json();
  const orders: any[] = (json.data as { content?: any[] })?.content ?? (json.data as any[]) ?? [];
  expect(orders.some(o => o.id === draftOrder.id)).toBe(false);
});
```
What goes wrong: an error body or a changed shape becomes `[]`, so "it disappeared" passes without a deletion.

**Good** (neutral)
```ts
test(
  'should remove a deleted draft order from the orders list',
  async ({ request, clerkToken, draftOrder }) => {
    const resp = await test.step('When the draft order is deleted', () =>
      apiRequest(request, 'DELETE', `/api/orders/${draftOrder.id}`, clerkToken));
    await test.step('Then it is gone from the orders list', async () => {
      expect(resp.status()).toBe(204);
      const list = await apiRequest(request, 'GET', '/api/orders?status=DRAFT', clerkToken);
      expect(list.status()).toBe(200);
      const orders: Order[] = (await list.json()).data.content;
      expect(orders.map((o) => o.id)).not.toContain(draftOrder.id);
    });
  },
);
```
Why: one exact status each, and the list shape is read without a default, so an error cannot look like an empty list.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-07-prompt-builder.spec.ts:74-81` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:105 · fix from research/31d-v2.md:85

### EA4 — A test naming a dependency asserts that dependency's record and its success

**Bad** (neutral)
```ts
const { payment, emails } = await pollForPayment(request, invoiceId, token, 'card-gateway',
  { maxWaitMs: 60_000, andReceiptEmail: true });
expect(payment, `payment via card-gateway must appear — the gateway was never called`).toBeTruthy();
expect(emails.some(m => m.to === customer.email && m.subject?.trim())).toBe(true);
```
What goes wrong: the payment record exists but its outcome is never checked, so a declined charge plus an email passes.

**Good** (neutral)
```ts
await test.step('Then the card gateway took this payment and approved it', async () => {
  const cardPayment = async () => {
    const resp = await apiRequest(request, 'GET', `/api/invoices/${invoice.id}/payments`, clerkToken);
    const payments: Payment[] = (await resp.json()).data;
    return payments.find((p) => p.gateway === 'card-gateway');
  };
  await expect
    .poll(cardPayment, {
      timeout: 15_000,
      message: 'a card-gateway payment must appear — the gateway was never called',
    })
    .toBeDefined();
  const payment = await cardPayment();
  expect(payment?.outcome, 'the gateway was called but declined').toBe('APPROVED');
  expect(payment?.amount, 'the payment must carry this invoice total').toEqual(invoice.total);
});
```
Why: `expect.poll` waits for the record matched by gateway name, then its approval and the amount this test set up are asserted.

Evidence: `.claude/skills/smoke-spec/SKILL.md:119-122` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:139 · fix from research/31d-v2.md:121

### EA5 — A deliberate dependency failure asserts the failure shape

**Bad** (neutral)
```ts
test('pay invoice with the gateway offline', async ({ clerkPage, invoice, fakeGateway }) => {
  fakeGateway.goOffline();
  await clerkPage.goto(`/invoices/${invoice.id}`);
  await clerkPage.getByRole('button', { name: 'Pay invoice' }).click();
  await expect(clerkPage.getByRole('alert')).toBeVisible();
});
```
What goes wrong: only a reply is checked, so a regression that records an approved payment for a dead gateway stays green.

**Good** (neutral)
```ts
await test.step('Then the toast says declined and no payment is approved', async () => {
  await expect(clerkPage.getByRole('alert')).toHaveText('Payment declined');
  const resp = await apiRequest(request, 'GET', `/api/invoices/${invoice.id}/payments`, clerkToken);
  expect(resp.status()).toBe(200);
  const payments: Payment[] = (await resp.json()).data;
  expect(
    payments.some((p) => p.outcome === 'APPROVED'),
    'an offline gateway must never produce an approved payment',
  ).toBe(false);
});
```
Why: both halves are asserted — the clerk still gets an answer, and no successful payment exists.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-65-e2e-llm-tools.spec.ts:320-352` @origin/master 2026-10-02, no sha in source (Bad, adapted) · source research/31d-v2.md:170 · fix from research/31d-v2.md:151

### EA6 — Own setup failure throws; skip only on a named missing capability

**Bad** (neutral)
```ts
try {
  const probe = await apiRequest(request, 'POST', '/api/tax-rates/probe', token,
    { uri: TAX_RATE_HOST }, { timeout: 15_000 });
  if (probe.status() === 200) {
    const save = await apiRequest(request, 'POST', '/api/tax-rates/sources', token, { uri: TAX_RATE_HOST });
    if ([200, 201].includes(save.status())) taxSourceId = (await save.json()).data.id;
  }
} catch {
  // Host blocked — no source to register; proceed without.
}
```
What goes wrong: the fixture's own setup fails silently, so later tests fail or skip for a reason the report never shows.

**Good** (neutral)
```ts
const test = base.extend<{ taxSource: TaxSource }>({
  taxSource: async ({ request, clerkToken }, use) => {
    const externalReachable = await canReach(TAX_RATE_HOST);
    const resp = await apiRequest(request, 'POST', '/api/tax-rates/sources', clerkToken, {
      uri: TAX_RATE_HOST,
    });
    expect(resp.status(), 'the tax-rate source must be registered for this test').toBe(201);
    await use({ id: (await resp.json()).data.id, externalReachable });
  },
});
// in each @external test:
test.skip(!taxSource.externalReachable, 'External internet not reachable from this Docker environment');
```
Why: the setup fails loud at its source, and a test skips only on one named capability with its reason.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-41-http-tool.spec.ts:46-63` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:203 · fix from research/31d-v2.md:186

### EB1 — Users and seeded data come from fixtures; never `data[0]`

**Bad** (neutral)
```ts
test.beforeAll(async ({ request }) => {
  // Shared setup runs in beforeAll (not a per-test fixture) because the orders are
  // shared across the serial tests. Each create asserts its status — setup fails loud.
  token = await apiLogin(request);

  const custResp = await apiRequest(request, 'GET', '/api/customers', token);
  customerId = (await custResp.json()).data[0].id;
```
What goes wrong: `data[0]` returns the newest customer, often another worker's, and the hand-rolled login bypasses the shared fixtures.

**Good** (neutral)
```ts
test(
  'should list a new order under the seeded GOLD customer',
  { annotation: { type: 'issue', description: '#123 AC-3' } },
  async ({ clerkPage, request, clerkToken }) => {
    const customerId = await seededCustomerId(request, clerkToken, SEEDED_GOLD_EMAIL);
    const order = await test.step('Given a placed order for the seeded GOLD customer', () =>
      placeOrder(request, clerkToken, customerId, [ONE_LINE]));
    await test.step('When the orders page is filtered to that customer', async () => {
      await clerkPage.goto('/orders');
      await clerkPage.getByRole('combobox', { name: 'Customer' }).selectOption({ label: SEEDED_GOLD_EMAIL });
    });
    await test.step('Then the order has its own row', () =>
      expect(clerkPage.getByRole('row', { name: new RegExp(order.id) })).toBeVisible());
  },
);
```
Why: token and page come from fixtures, and the seeded customer is found by its email, so it is always the same one.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-16-chat-live-ollama.spec.ts:28-34` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:244 · fix from research/31d-v2.md:224

### EB2 — `describe.serial` only for one expensive shared call, reason above it

**Bad** (neutral)
```ts
// describe.serial + shared beforeAll state is deliberate: T1, T2, T3 and T4 pay against one
// shared invoice, and payments sent to one invoice concurrently interleave, so a test could read
// another test's payment. The cost is that a failure in one skips the rest of the chain.
test.describe.serial('[SMOKE] Partial payments', { tag: ['@billing'] }, () => {
```
What goes wrong: four separate payments are chained through one invoice; an invoice per test removes the interleaving, so serial is not needed.

**Good** (neutral)
```ts
/*
 * describe.serial is deliberate: the one sandbox settlement run is expensive (60-900 s).
 * Running it once and asserting it three ways is the whole point — making each test
 * self-contained would start three settlement runs for no added coverage. The shared
 * invoice and settlement therefore live in beforeAll, and tests run in order against them.
 */
test.describe.serial(
  '[SMOKE] Invoice settlement — payment sandbox',
  { tag: ['@billing', '@external', '@gateway:real'] },
  () => {
    // …
```
Why: one expensive external call is made once and read three ways, and the reason sits above the block.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-69-memory-tools-e2e.spec.ts:36-41` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:272 · fix from research/31d-v2.md:259

### EB3 — Setup that tests mutate is a per-test fixture that asserts its create

**Bad** (neutral)
```ts
test.beforeAll(async ({ request }) => {
  const token = await apiLogin(request);
  const mk = async (tier: string) => {
    const r = await apiRequest(request, 'POST', '/api/customers', token, { email: `smoke-${tier}-${Date.now()}@example.com`, tier });
    const d = (await r.json()).data;
    createdCustomerIds.push(d.id);
    return d;
  };
  const gold = await mk('GOLD');
  goldCustomerId = gold.id ?? gold.customerId ?? gold.uuid;
```
What goes wrong: the create status is never checked and the `??` chain hides a missing id, so a failed setup shows up later as a wrong 404.

**Good** (neutral)
```ts
const test = base.extend<{ goldCustomerId: string }>({
  goldCustomerId: async ({ request, clerkToken }, use) => {
    const body = { email: `smoke-gold-${Date.now()}@example.com`, tier: 'GOLD' };
    const resp = await apiRequest(request, 'POST', '/api/customers', clerkToken, body);
    expect(resp.status(), 'GOLD customer must be created for this test').toBe(201);
    const customerId = (await resp.json()).data.id as string;
    await use(customerId);
    await apiRequest(request, 'DELETE', `/api/customers/${customerId}`, clerkToken).catch(() => {
      /* gone */
    });
  },
});
```
Why: each test gets its own customer, the create fails loud at its source, and teardown deletes it afterwards.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-06-admin.spec.ts:131-140` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:300 · fix from research/31d-v2.md:283

### EB4 — Touch nothing we do not control

**Bad** (neutral)
```ts
test('F12: POST /api/payment-gateway/test-connection (dry-run) → 200 with {success, latencyMs}', async ({ request, clerkToken }) => {
  const resp = await apiRequest(request, 'POST', '/api/payment-gateway/test-connection', clerkToken, { baseUrl: 'https://httpbin.org', path: '/get' });
  expect(resp.status()).toBe(200);

  const data = (await resp.json()).data;
  expect(typeof data.success).toBe('boolean');
  expect(typeof data.latencyMs).toBe('number');
  expect(data.success ? true : Boolean(data.message), 'a failed probe must say why').toBe(true);
});
```
What goes wrong: a public third-party site decides which branch runs, in a test that is not `@external` and has no skip.

**Good** (neutral)
```ts
test(
  'should report a reachable payment gateway in the dry-run connection test',
  async ({ request, clerkToken, fakeGateway }) => {
    const resp = await test.step('When the gateway connection is tested against the fake', () =>
      apiRequest(request, 'POST', '/api/payment-gateway/test-connection', clerkToken, {
        baseUrl: fakeGateway.url,
      }));
    await test.step('Then it answers with success and a latency', async () => {
      expect(resp.status()).toBe(200);
      expect((await resp.json()).data).toMatchObject({ success: true, latencyMs: expect.any(Number) });
    });
  },
);
```
Why: the target is the FakePaymentGateway the suite runs, so one outcome is expected and asserted exactly.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-59-tool-error-paths.spec.ts:157-170` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:336 · fix from research/31d-v2.md:318

### EC1 — Wait on state with `expect.poll`, never on a sleep loop

**Bad** (neutral)
```ts
async function pollInvoiceUntil(request: any, invoiceId: string, token: string, pred: (status: string) => boolean, maxWaitMs = 60_000): Promise<string> {
  const deadline = Date.now() + maxWaitMs;
  let status = '';
  while (Date.now() < deadline) {
    const resp = await apiRequest(request, 'GET', `/api/invoices/${invoiceId}`, token);
    status = (await resp.json()).data.status;
    if (pred(status)) return status;
    await new Promise(r => setTimeout(r, 2_000));
  }
  return status;
}
```
What goes wrong: a hand-written sleep loop waits on time and returns silently at its deadline.

**Good** (neutral)
```ts
await test.step('Then the invoice reaches OVERDUE', async () => {
  const invoiceStatus = async () => {
    const resp = await apiRequest(request, 'GET', `/api/invoices/${invoice.id}`, clerkToken);
    return (await resp.json()).data.status;
  };
  // OverdueReminder runs every 10 s on the test profile, so 25 s covers two runs inside the test timeout
  await expect.poll(invoiceStatus, { timeout: 25_000, intervals: [1_000] }).toBe('OVERDUE');
});
```
Why: `expect.poll` waits on the state that matters, with a named budget below the test timeout, and fails if the state never arrives.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-44-webhook-retry.spec.ts:18-28` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:373 · fix from research/31d-v2.md:356

### EC2 — Check page state with a retrying matcher

**Bad** (neutral)
```ts
test('order page links to its invoice', async ({ clerkPage, placedOrder }) => {
  await clerkPage.goto(`/orders/${placedOrder.id}`);
  const invoiceLink = clerkPage.getByRole('link', { name: /view invoice/i });
  await expect(invoiceLink).toBeVisible();
  expect(await invoiceLink.getAttribute('href')).toContain(`/invoices/${placedOrder.invoiceId}`);
});
```
What goes wrong: `getAttribute` reads the page once, before the link may have its final target.

**Good** (neutral)
```ts
test(
  'should link a placed order to its invoice',
  { annotation: { type: 'issue', description: '#123 AC-5' } },
  async ({ clerkPage, placedOrder }) => {
    await test.step('When the clerk opens the placed order', async () => {
      await clerkPage.goto(`/orders/${placedOrder.id}`);
    });
    await test.step('Then its invoice link points at the order invoice', async () => {
      const invoiceLink = clerkPage.getByRole('link', { name: 'View invoice' });
      await expect(invoiceLink).toHaveAttribute('href', `/invoices/${placedOrder.invoiceId}`);
    });
  },
);
```
Why: `toHaveAttribute` retries until the link has the expected target, so it is the wait and the assertion together.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-33-agent-studio-gallery.spec.ts:95-101` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:407 · fix from research/31d-v2.md:392

### EC3 — No `.first()` to escape strictness; narrow by name and chaining

**Bad** (neutral)
```ts
const row = page.getByRole('row').filter({ hasText: invoice.id }).first();
await row.getByRole('button').first().click();
await page.getByRole('menuitem').first().click();

// then — the Pay invoice dialog opens
const dialog = page.getByRole('dialog').first();
```
What goes wrong: four `.first()` calls hide strictness errors; "first menu item" is Pay invoice only until the menu order changes.

**Good** (neutral)
```ts
const row = clerkPage.getByRole('row', { name: new RegExp(invoice.id) });
await test.step('When Pay invoice is clicked on the invoice row', async () => {
  await expect(row).toBeVisible();
  await row.getByRole('button', { name: 'Pay invoice' }).click();
});
await test.step('Then the payment dialog names the invoice total', async () => {
  const dialog = clerkPage.getByRole('dialog', { name: 'Pay invoice' });
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText('EUR 42.00');
});
```
Why: the row is narrowed by this test's own invoice id, and the button is chained inside it by its name.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-04-tools.spec.ts:78-84` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:437 · fix from research/31d-v2.md:422

### EC4 — Every Playwright call and web-first expect is awaited

**Bad** (neutral)
```ts
test('UI: /invoices loads without error', async ({ clerkPage }) => {
  await clerkPage.goto('/invoices');
  expect(clerkPage.getByRole('heading', { name: 'Invoices', exact: true })).toBeVisible();
});
```
What goes wrong: nobody awaits the `toBeVisible` promise, so the test ends green before the check runs.

**Good** (neutral)
```ts
test(
  'should show the invoice list heading',
  { annotation: { type: 'issue', description: '#123 AC-6' } },
  async ({ clerkPage }) => {
    await test.step('When the clerk opens the invoice list', async () => {
      await clerkPage.goto('/invoices');
    });
    await test.step('Then the invoice list heading is visible', async () => {
      await expect(clerkPage.getByRole('heading', { name: 'Invoices', exact: true, level: 1 })).toBeVisible();
    });
  },
);
```
Why: the navigation, the step and the web-first matcher are all awaited, so the test cannot finish before the check.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-17-tool-types.spec.ts:31-39` @origin/master 2026-10-02, no sha in source (Bad, adapted) · source research/31d-v2.md:465 · fix from research/31d-v2.md:452

### EC5 — Raise a timeout only for a named slow dependency; poll budget below it

**Bad** (neutral)
```ts
test('B01: 3 sequential invoices are paid without a declined payment (latency logged)', async ({ request }) => {
  test.setTimeout(600_000);
```
What goes wrong: a 10-minute timeout with no reason; a reader must work out the poll budget from the loop below.

**Good** (neutral)
```ts
test(
  'should mark an invoice PAID once the payment sandbox confirms it',
  { tag: '@external', annotation: { type: 'issue', description: '#123 AC-7' } },
  async ({ request, clerkToken, sandbox }) => {
    test.skip(!sandbox.reachable, 'Payment sandbox not reachable from this Docker environment');
    test.setTimeout(900_000); // payment sandbox confirms in batches; the poll below stops at 840 s
    // … Given (open invoice) and When (payment sent to the sandbox) steps
    await test.step('Then the invoice is PAID', async () => {
      const status = () => invoiceStatus(request, clerkToken, invoiceId);
      await expect.poll(status, { timeout: 840_000, intervals: [10_000] }).toBe('PAID');
    });
  },
);
```
Why: the slow dependency is named on the line, and the poll ends before the test timeout, so its failure message reports.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-78-stability.spec.ts:376-377` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:497 · fix from research/31d-v2.md:477

### EC6 — Fix a flake at its cause, never with a longer timeout

**Bad** (neutral)
```ts
test('pay an invoice after changing its due date', async ({ clerkPage, invoice }) => {
  // Extended timeout: under full-suite load Pay invoice sometimes fails, then passes on retry.
  // Passes in ~5s alone; budget 6x headroom for worst-case load.
  test.setTimeout(180_000);
  await clerkPage.goto(`/invoices/${invoice.id}`);
  await clerkPage.getByRole('textbox', { name: 'Due date' }).fill('2026-11-30');
  await clerkPage.getByRole('button', { name: 'Save', exact: true }).click();
  await clerkPage.getByRole('button', { name: 'Pay invoice' }).click();
```
What goes wrong: the timeout was raised for suite load, which hides the real cause: paying before the save has landed.

**Good** (neutral)
```ts
// Pay invoice reads the SAVED invoice: paying while the PUT is in flight fails under load
await test.step('Given the new due date is saved', async () => {
  await clerkPage.getByRole('textbox', { name: 'Due date' }).fill('2026-11-30');
  const isInvoiceSave = (r: Response) =>
    r.request().method() === 'PUT' && /\/api\/invoices\/[^/]+$/.test(new URL(r.url()).pathname);
  const saved = clerkPage.waitForResponse(isInvoiceSave);
  await clerkPage.getByRole('button', { name: 'Save', exact: true }).click();
  expect((await saved).status(), 'the invoice save must succeed before paying').toBe(200);
});
await test.step('When the clerk pays the invoice', async () => {
  await clerkPage.getByRole('button', { name: 'Pay invoice' }).click();
});
```
Why: the race with the save is removed at its cause, so no retry or longer timeout is needed.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-69-memory-tools-e2e.spec.ts:244-247` @origin/master 2026-10-02, no sha in source (Bad, real; neutral Bad hides a save race, not queue contention) · source research/31d-v2.md:520 · fix from research/31d-v2.md:506 (real fix at `aruvii-ui/playwright/e2e/smoke/smoke-45-agent-tabs.spec.ts:115-121`)

### ED2 — Tests reaching an external dependency tag fake or real, and a fake test asserts recorded requests

**Bad** (neutral)
```ts
const gwResp = await apiRequest(request, 'POST', '/api/payment-gateway', token, { name: `smoke-gw-${uid}`, type: 'CARD', config: { apiKey: 'sk-smoke' } });
// …
test.describe('[SMOKE-05] Invoice payment', { tag: ['@billing'] }, () => {
// …
  test('POST a payment → 200/202 and it is persisted on the invoice', async ({ request, invoice }) => {
    // when — a payment is posted
    const resp = await apiRequest(request, 'POST', `/api/invoices/${invoice.id}/payments`, invoice.token, { amount: { amount: '42.00', currency: 'EUR' } });
    expect([200, 202]).toContain(resp.status());
```
What goes wrong: the payment goes to a real card gateway with a dummy key, yet the spec has no `@gateway:*` or `@external` tag.

**Good** (neutral)
```ts
// describe — tag: ['@billing', '@gateway:fake']
await test.step('Then both payments persist and the gateway was sent both amounts', async () => {
  expect(payments, 'both payments must be persisted').toHaveLength(2);
  const sent = await fakeGateway.requests(invoice.id);
  expect(sent, 'one gateway call per payment').toHaveLength(2);
  const charged = sent.map((r) => r.amount.amount);
  expect(charged, 'the second charge must carry the remaining balance').toEqual(['30.00', '12.00']);
  await fakeGateway.assertConsumed(invoice.id);
});
```
Why: the tag says the gateway is the fake, and the test asserts what the fake received, never its scripted reply.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-05-sessions.spec.ts:24,47,68-71` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:593 · fix from research/31d-v2.md:576

### ED3 — The spec drives its route in the UI and asserts the refusal path

**Bad** (neutral)
```ts
test('UI: pay invoice dialog is interactive — first field accepts input', async ({ clerkPage }) => {
  await clerkPage.goto('/invoices');
  await expect(clerkPage.getByRole('heading', { name: /invoices/i })).toBeVisible();
  // The page should present a form with a text field
  const field = clerkPage.getByRole('textbox');
  await expect(field).toBeVisible();
  await field.click();
  await field.fill('Smoke test amount');
  // Verify the value was accepted
  await expect(field).toHaveValue('Smoke test amount');
```
What goes wrong: Pay invoice is never clicked; a text box that accepts text proves nothing about paying an invoice.

**Good** (neutral)
```ts
test(
  'should show Payment declined when the gateway declines the payment',
  { annotation: { type: 'issue', description: '#123 AC-8' } },
  async ({ clerkPage, invoice, fakeGateway }) => {
    const row = clerkPage.getByRole('row', { name: new RegExp(invoice.id) });
    await test.step('Given the payment gateway declines the next charge', () => fakeGateway.declineNext());
    await test.step('When the clerk pays the invoice from the invoice list', async () => {
      await clerkPage.goto('/invoices');
      await row.getByRole('button', { name: 'Pay invoice' }).click();
    });
    await test.step('Then the toast says Payment declined', async () => {
      await expect(clerkPage.getByRole('alert')).toHaveText('Payment declined');
    });
  },
);
```
Why: the test drives the real Pay invoice route in the UI and asserts its refusal outcome; the PAID path gets a sibling test.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-24-prompt-builder-run.spec.ts:116-126` @origin/master 2026-10-02, no sha in source (Bad, real) · source research/31d-v2.md:625 · fix from research/31d-v2.md:609 (refusal-path shape; moved from API to UI)

### ED4 — Exactly one domain tag per spec

**Bad** (neutral)
```ts
test.describe.serial('[SMOKE] Order checkout — pay and email the invoice', { tag: ['@orders', '@billing', '@external', '@core'] }, () => {
```
What goes wrong: two domain tags, and `@external` with `@core` on a spec outside the core-config whitelist.

**Good** (neutral)
```ts
test.describe(
  '[SMOKE-74] Invoice payment — payment sandbox cycle',
  { tag: ['@billing', '@external', '@gateway:real', '@core'] },
  () => {
    // …
```
Why: one domain tag; `@external` with `@core` is allowed only because this spec is on the core-config whitelist.

Evidence: `aruvii-ui/playwright/e2e/smoke/smoke-56-agent-judge.spec.ts:25` @origin/master 2026-10-02, no sha in source (Bad, adapted) · source research/31d-v2.md:652 · fix from research/31d-v2.md:644

### ED5 — `make smoke` while developing, `make smoke FULL=1` as the gate

**Bad** (neutral)
```ts
// Full suite: npm run smoke          (all specs, DoD gate)
// Core suite: npm run smoke:core     (this config, the @core tier, daily dev gate)
```
What goes wrong: `npm run smoke` deploys nothing, so the named gate can pass against stale containers.

**Good** (neutral)
```ts
// Development loop: make smoke          (deploys, then this config: the @core tier)
// Gate (Done means): make smoke FULL=1  (deploys, then every spec; the report must read 0 failed)
// npm run smoke* deploys nothing, so on its own it tests whatever containers are running.
```
Why: both commands go through `make`, which deploys first, and the comment says why the npm scripts are not the gate.

Evidence: `aruvii-ui/playwright.core.config.ts:14-15` @772736bf (Bad, real) · source research/31d-v2.md:670 · fix from research/47-good-rewrites.md:764
