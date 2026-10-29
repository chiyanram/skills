# Smoke specs

How a Playwright smoke spec proves a user journey: it can fail, it stands alone, and it waits on state, never on time.
Read it when you write or review a Playwright spec, or a fixture that such specs import.

Contents: Rules · When X, use Y · Good / Bad (EA1–EA6) · Decided edges · Review checks

## Rules

- **EA1** — Give every test an assertion that fails without the feature; a poll is not one; a non-obvious `expect`
  carries a message, because a poll returns silently on timeout, so the test passes without the feature.
- **EA2** — Assert a landmark only the feature renders, found by role, then label or text, test-id last; never chrome,
  CSS class, XPath or dead route, because chrome or a shared CSS class renders on every page.
- **EA3** — Let nothing turn a failure green: no catch around act-and-assert, `|| true`, `?? []` before a check,
  `expect` only inside an `if`, or 2xx-or-4xx status set, because these turn an error into a pass.
- **EA4** — A test naming a dependency asserts its record by name and its success, or its approval pause when that is
  the subject; a reply never counts, because a reply does not show the dependency ran.
- **EA5** — A test that makes a dependency fail on purpose asserts the failure shape: a reply still arrives and no
  successful record exists for it, because a fake success for a dead dependency would stay green.
- **EA6** — Skip only on a named missing capability, with a reason; own failed setup throws; quarantine only with
  `test.fixme` naming an open issue, removed when it closes, because a swallowed setup failure hides why tests fail.
- **EB2** — Make every test pass when run alone; use `describe.serial` only for one expensive shared live call, with
  the reason above it, because in a serial chain one failure skips every later test.
- **EB3** — Use `beforeAll` only for read-only setup that throws on failure and that no test mutates, because a failed
  or mutated `beforeAll` surfaces later as an unrelated wrong status.
- **EB4** — Touch nothing we do not control: reach a dependency through its fake or a bundled local instance; real
  internet only in `@external` tests that skip when unreachable, because a third-party site then decides the result.
- **EC1** — In new code, never wait on time (`waitForTimeout`, sleeps, `networkidle`); wait on a web-first assertion,
  a response, a URL or `expect.poll` with a budget, because tests that wait on time are flaky.
- **EC2** — Check page state with retrying matchers (`toHaveText`, `toHaveAttribute`, `toBeVisible`), never
  `expect(await locator.x())`, because a one-shot read checks the page once, before it may settle.
- **EC3** — In new code, never use `.first()`, `.nth()` or `.last()` to escape a strictness error; narrow by role
  name, filter or chaining, because `.first()` picks whichever match comes first, which changes with the page.
- **EC4** — Await every Playwright call and `expect`, enforced by the `no-floating-promises` lint rule over the
  Playwright tests, because an un-awaited `expect` can end the test green before it checks.
- **EC5** — Raise a timeout only for a named slow dependency (live model) with a one-line reason; keep a poll budget
  below the test timeout, because a poll outlasting the test timeout dies without its failure message.
- **ED3** — In a feature's spec, drive its route in the UI at least once and assert every status the change
  introduces, refusal path included, because a spec never driving the route passes with the screen broken.

## When X, use Y

| situation | use | why |
|---|---|---|
| the test checks page state: text, an attribute, visibility | a retrying matcher: `toHaveText`, `toHaveAttribute`, `toBeVisible` | a one-shot read checks the page once, before it may settle (EC2, ledger :117) |
| the test waits for a state to arrive | a web-first assertion, a response, a URL, or `expect.poll` with a budget | tests that wait on time are flaky, as the Playwright docs warn (EC1, ledger :116) |
| the test locates a landmark | role, then label or text, test-id last | chrome or a shared CSS class renders on every page and proves nothing (EA2, ledger :107) |
| a locator matches more than one element | a role name, a filter or chaining | `.first()` picks whichever match comes first, which changes with the page (EC3, ledger :118) |
| setup that no test mutates | `beforeAll` that throws on failure | a failed or mutated `beforeAll` surfaces later as an unrelated wrong status (EB3, ledger :114) |
| one expensive shared live call | `describe.serial`, with the reason above it | in a serial chain one failure skips every later test (EB2, ledger :113) |
| a dependency we do not control | its fake, or a bundled local instance; what to replace: TM2 (`strategy.md`) | a third-party site then decides whether the test passes (EB4, ledger :115) |
| the test needs the real internet | an `@external` tag and a skip when it is unreachable | a third-party site then decides whether the test passes (EB4, ledger :115) |
| a capability the test needs is missing | a skip that names the capability and gives a reason | a swallowed setup failure makes later tests fail or skip for hidden reasons (EA6, ledger :111) |
| a test must be quarantined | `test.fixme` naming an open issue, removed when the issue closes | a swallowed setup failure makes later tests fail or skip for hidden reasons (EA6, ledger :111) |
| a named slow dependency (live model) | a raised timeout with a one-line reason; the poll budget below the test timeout | a poll that outlasts the test timeout dies without its failure message (EC5, ledger :120) |

`ledger :N` is line N of `research/19-approved-rules.md` in chiyanram/skills.

Test titles, one `test.step` per Given/When/Then and the issue annotation: GT1, GT2, GT4 (`scenario-to-tests.md`).
Which journeys get a smoke spec: S1 (`strategy.md`). A failure path for every acceptance criterion: GA5
(`acceptance-criteria.md`, planning).

## Good / Bad

Every rule's approved pair: [examples/smoke-specs.md](examples/smoke-specs.md).

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
  const invoice = await pollInvoice(
    request,
    placedOrder.invoiceId,
    clerkToken,
    (inv) => inv.status === 'PAID',
    { maxWaitMs: 30_000, intervalMs: 1_000 },
  );
  expect(invoice.status, `invoice ${placedOrder.invoiceId} was not PAID within 30 s`).toBe('PAID');
});
```
The polled condition is asserted again with a message, so removing payments makes the test fail. (Real evidence:
ledger row EA1.)

### EA2 — Assert a feature-only landmark by role, not a shared CSS class

**Bad** (neutral)
```ts
test('the invoice list loads with the Invoices heading and a status filter', async ({ page }) => {
  await loginViaForm(page);
  await page.goto('/invoices', { waitUntil: 'networkidle' });
  await expect(page.getByRole('heading', { name: 'Invoices', exact: true, level: 1 })).toBeVisible({ timeout: 12_000 });
  await expect(page.locator('.toggle-wrap').first()).toBeVisible({ timeout: 8_000 });
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
The heading and the named combobox render only on the invoice list, and both are found by role and name. (Real
evidence: ledger row EA2.)

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
  { annotation: { type: 'issue', description: '#123 AC-2' } },
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
One exact status each, and the list shape is read without a default, so an error cannot look like an empty list.
(Real evidence: ledger row EA3.)

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
  const { payment } = await pollForPayment(request, invoice.id, clerkToken, 'card-gateway', {
    maxWaitMs: 15_000,
    intervalMs: 1_000,
  });
  expect(payment, 'a card-gateway payment must appear — the gateway was never called').toBeTruthy();
  expect(payment?.outcome, 'the gateway was called but declined').toBe('APPROVED');
  expect(payment?.amount, 'the payment must carry this invoice total').toEqual(invoice.total);
});
```
The record is matched by gateway name, then its approval, then the amount this test set up. (Real evidence: ledger
row EA4.)

### EA5 — A deliberate dependency failure asserts the failure shape

**Bad** (neutral)
```ts
test('pay invoice with the gateway offline', async ({ page, invoice, fakeGateway }) => {
  fakeGateway.goOffline();
  await loginViaForm(page);
  await page.goto(`/invoices/${invoice.id}`);
  await page.getByRole('button', { name: 'Pay invoice' }).click();
  await expect(page.getByRole('alert')).toBeVisible();
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
Both halves are asserted: the clerk still gets an answer, and no successful payment exists. (Real evidence: ledger
row EA5.)

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

## Decided edges

- **Skip when** an existing `networkidle`, sleep, `.first()`, `.nth()` or `.last()` sits on a line the change does
  not add: EC1 and EC3 bind new code only (ledger :116, :118). — **Do not skip when** the change
  adds the line. — **Confidence** high
- **Skip when** a catch sits in fixture teardown after `use()` and wraps only the cleanup call: EA3 names a catch
  around act-and-assert (ledger :108), and the approved EB3 pair does this
  (`research/68d-neutral-testing-smoke.md` :290). — **Do not skip when** the catch wraps an action, a setup call or an
  `expect`. — **Confidence** high
- **Skip when** a spec has no named screenshot file: ED3 drops that mandate (ledger :124). — **Do not skip
  when** the spec never drives its route in the UI (ED3). — **Confidence** high

## Review checks

Walk every changed Playwright spec file and every changed fixture file those specs import. False-green checks first.

- [ ] EA1 — For each test, find an `expect` that fails if the feature is removed. A test whose only check is a poll,
  or a non-obvious `expect` with no message, is a finding.
- [ ] EA2 — For each landmark, check that only this feature renders it and that it is found by role, then label or
  text, then test-id. App chrome, a CSS class (`grep -n "locator('\."`), XPath or a dead route is a finding.
- [ ] EA3 — Grep each file for `catch`, `|| true`, `?? []` and `if (`. A catch around act-and-assert, a `|| true`, a
  `?? []` before a check, an `expect` only inside an `if`, or a status set mixing 2xx with 4xx is a finding.
- [ ] EA4 — For each test that names a dependency, find an `expect` on that dependency's record by name and one on its
  success or approval pause. A test that checks only the reply is a finding.
- [ ] EA5 — For each test that fails a dependency on purpose, find both halves: the reply arrives, and no successful
  record exists. A test with one half is a finding.
- [ ] EA6 — For each `test.skip`, find a named missing capability and a reason. For each own setup step, find a throw
  on failure. For each `test.fixme`, find an open issue. Anything else is a finding.
- [ ] EB2 — For each `describe.serial`, find one expensive shared live call and the reason above the block. A test
  that needs an earlier test to pass is a finding.
- [ ] EB3 — For each `beforeAll`, check that the setup is read-only, throws on failure and is mutated by no test. A
  `beforeAll` that fails any of the three is a finding.
- [ ] EB4 — For each URL or host a test reaches, find the suite's fake, a bundled local instance, or an `@external`
  tag with a skip when unreachable. Any other third-party call is a finding.
- [ ] EC1 — Grep the added lines for `waitForTimeout`, `setTimeout`, `sleep` and `networkidle`. Each hit is a finding.
- [ ] EC2 — Grep for `expect(await`. Each hit that reads page state from a locator is a finding.
- [ ] EC3 — Grep the added lines for `.first()`, `.nth(` and `.last()`. Each hit that escapes a strictness error is a
  finding.
- [ ] EC4 — Open the lint config and confirm `no-floating-promises` covers the Playwright tests. If it does not, every
  un-awaited Playwright call or `expect` is a finding.
- [ ] EC5 — For each raised timeout, find the named slow dependency and a one-line reason, and check that each poll
  budget in that test is below the test timeout. A timeout without both, or a poll at or above it, is a finding.
- [ ] ED3 — For the changed feature, find a test that drives its route in the UI, and one assertion for each status
  the change introduces, the refusal path included. A missing route or status is a finding.
