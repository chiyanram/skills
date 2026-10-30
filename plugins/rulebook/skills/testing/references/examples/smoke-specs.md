# Smoke specs — examples

Every approved neutral Good/Bad pair for the rules in [`../smoke-specs.md`](../smoke-specs.md), one pair per rule.
Read it when a rule there is unclear and its pair is not in the main file.

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
The poll returns silently at its deadline, so the test passes when the invoice never becomes PAID.

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
`expect.poll` makes the condition an assertion with a message and a budget below the test timeout, so removing payments
makes the test fail. (Real evidence: ledger row EA1.)

### EA2 — Assert a feature-only landmark by role, not a shared CSS class

**Bad** (neutral)
```ts
test('the invoice list loads with the Invoices heading and a status filter', async ({ clerkPage }) => {
  await clerkPage.goto('/invoices');
  await expect(clerkPage.getByRole('heading', { name: 'Invoices', exact: true, level: 1 })).toBeVisible();
  await expect(clerkPage.locator('.toggle-wrap')).toBeVisible();
```
`.toggle-wrap` is a CSS class every settings page renders, so it proves no invoice filter rendered.

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
The heading and the named combobox render only on the invoice list, and both are found by role and name. (Real evidence:
ledger row EA2.)

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
An error body or a changed shape becomes `[]`, so "it disappeared" passes without a deletion.

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
One exact status each, and the list shape is read without a default, so an error cannot look like an empty list. (Real
evidence: ledger row EA3.)

### EA4 — A test naming a dependency asserts that dependency's record and its success

**Bad** (neutral)
```ts
const { payment, emails } = await pollForPayment(request, invoiceId, token, 'card-gateway',
  { maxWaitMs: 60_000, andReceiptEmail: true });
expect(payment, `payment via card-gateway must appear — the gateway was never called`).toBeTruthy();
expect(emails.some(m => m.to === customer.email && m.subject?.trim())).toBe(true);
```
The payment record exists but its outcome is never checked, so a declined charge plus an email passes.

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
`expect.poll` waits for the record matched by gateway name, then its approval and the amount this test set up are
asserted. (Real evidence: ledger row EA4.)

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
Only a reply is checked, so a regression that records an approved payment for a dead gateway stays green.

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
Both halves are asserted — the clerk still gets an answer, and no successful payment exists. (Real evidence: ledger row
EA5.)

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
The fixture's own setup fails silently, so later tests fail or skip for a reason the report never shows.

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
The setup fails loud at its source, and a test skips only on one named capability with its reason. (Real evidence:
ledger row EA6.)

### EB2 — `describe.serial` only for one expensive shared call, reason above it

**Bad** (neutral)
```ts
// describe.serial + shared beforeAll state is deliberate: T1, T2, T3 and T4 pay against one
// shared invoice, and payments sent to one invoice concurrently interleave, so a test could read
// another test's payment. The cost is that a failure in one skips the rest of the chain.
test.describe.serial('[SMOKE] Partial payments', { tag: ['@billing'] }, () => {
```
Four separate payments are chained through one invoice; an invoice per test removes the interleaving, so serial is not
needed.

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
One expensive external call is made once and read three ways, and the reason sits above the block. (Real evidence:
ledger row EB2.)

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
The create status is never checked and the `??` chain hides a missing id, so a failed setup shows up later as a wrong
404.

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
Each test gets its own customer, the create fails loud at its source, and teardown deletes it afterwards. (Real
evidence: ledger row EB3.)

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
A public third-party site decides which branch runs, in a test that is not `@external` and has no skip.

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
The target is the FakePaymentGateway the suite runs, so one outcome is expected and asserted exactly. (Real evidence:
ledger row EB4.)

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
A hand-written sleep loop waits on time and returns silently at its deadline.

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
`expect.poll` waits on the state that matters, with a named budget below the test timeout, and fails if the state never
arrives. (Real evidence: ledger row EC1.)

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
`getAttribute` reads the page once, before the link may have its final target.

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
`toHaveAttribute` retries until the link has the expected target, so it is the wait and the assertion together. (Real
evidence: ledger row EC2.)

### EC3 — No `.first()` to escape strictness; narrow by name and chaining

**Bad** (neutral)
```ts
const row = page.getByRole('row').filter({ hasText: invoice.id }).first();
await row.getByRole('button').first().click();
await page.getByRole('menuitem').first().click();

// then — the Pay invoice dialog opens
const dialog = page.getByRole('dialog').first();
```
Four `.first()` calls hide strictness errors; "first menu item" is Pay invoice only until the menu order changes.

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
The row is narrowed by this test's own invoice id, and the button is chained inside it by its name. (Real evidence:
ledger row EC3.)

### EC4 — Every Playwright call and web-first expect is awaited

**Bad** (neutral)
```ts
test('UI: /invoices loads without error', async ({ clerkPage }) => {
  await clerkPage.goto('/invoices');
  expect(clerkPage.getByRole('heading', { name: 'Invoices', exact: true })).toBeVisible();
});
```
Nobody awaits the `toBeVisible` promise, so the test ends green before the check runs.

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
The navigation, the step and the web-first matcher are all awaited, so the test cannot finish before the check. (Real
evidence: ledger row EC4.)

### EC5 — Raise a timeout only for a named slow dependency; poll budget below it

**Bad** (neutral)
```ts
test('B01: 3 sequential invoices are paid without a declined payment (latency logged)', async ({ request }) => {
  test.setTimeout(600_000);
```
A 10-minute timeout with no reason; a reader must work out the poll budget from the loop below.

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
The slow dependency is named on the line, and the poll ends before the test timeout, so its failure message reports.
(Real evidence: ledger row EC5.)

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
Pay invoice is never clicked; a text box that accepts text proves nothing about paying an invoice.

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
The test drives the real Pay invoice route in the UI and asserts its refusal outcome; the PAID path gets a sibling test.
(Real evidence: ledger row ED3.)
