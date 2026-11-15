# Writing specs

The steps and the rules for every job are in [SKILL.md](SKILL.md).

## A complete file

```ts
// tests/loans.spec.ts
import { expect } from '@playwright/test';
import { test } from './fixtures';

test.describe('loans', { tag: '@smoke' }, () => {
  test('a member returns a late book and sees the fine', async ({ page, lateLoan }) => {
    await page.goto(`/loans/${lateLoan.id}`);
    await expect(page.getByRole('heading', { name: lateLoan.title })).toBeVisible();

    await page.getByRole('button', { name: 'Return book' }).click();

    await expect(page.getByRole('status')).toHaveText('Returned');
    await expect(page.getByRole('row', { name: lateLoan.title })).toContainText('Fine: 2.00');
  });

  test('a member returns a book on time and pays no fine', async ({ page, onTimeLoan }) => {
    await page.goto(`/loans/${onTimeLoan.id}`);
    await expect(page.getByRole('heading', { name: onTimeLoan.title })).toBeVisible();

    await page.getByRole('button', { name: 'Return book' }).click();

    await expect(page.getByRole('status')).toHaveText('Returned');
    await expect(page.getByRole('row', { name: onTimeLoan.title })).not.toContainText('Fine');
  });
});
```

Each test opens its screen by path with data a fixture made, waits for the screen, does one thing, and checks the
outcome. Either test can run alone.

## Shape

- **One `test.describe` per feature**, named after it; a file holds one feature. Nest a `describe` only to share a
  hook, a tag or an option with some tests.
- **Arrange, act, assert**, in that order, with a blank line between them.
  - Arrange reaches the starting state: the saved sign-in, `page.goto` on the path, data from a fixture. End a long
    arrange with an assertion on the state it must reach, so a setup that did nothing fails there and not at the
    outcome check.
  - Act does the one thing under test.
  - Assert holds every `expect`, and nothing comes after it.
- **One behaviour per test.** The title names the outcome: `'a member returns a late book and sees the fine'` names
  one outcome, `'loans work'` names none. A second behaviour is a second test; when it starts from the first one's
  result, its arrange repeats the first one's act or seeds that result through the API.
- **Long journeys:** name each part with `test.step('Given a member with a late loan', ...)`, so the report shows
  which part failed.
- **Link the work item** with an annotation, `{ annotation: { type: 'issue', description: '#123' } }`, and name the
  acceptance criterion in the title, so a search for either finds the spec.

## Fixtures and test data

Make the data a screen needs through the API, in a fixture. Click through a creation flow only in the test that
covers that flow.

```ts
// tests/fixtures.ts
import { test as base, expect, type Page } from '@playwright/test';

type Loan = { id: string; title: string };

async function withLoan(page: Page, daysLate: number, use: (loan: Loan) => Promise<void>) {
  const title = `Dune ${Date.now()}`;                       // run-unique, so retries and workers never collide
  const created = await page.request.post('/api/test/loans', { data: { title, daysLate } });
  expect(created.ok(), await created.text()).toBeTruthy();   // a failed seed fails here, not 30 s later
  const loan: Loan = await created.json();
  await use(loan);
  await page.request.delete(`/api/test/loans/${loan.id}`);   // runs after a failure too
}

export const test = base.extend<{ lateLoan: Loan; onTimeLoan: Loan }>({
  lateLoan: async ({ page }, use) => withLoan(page, 7, use),
  onTimeLoan: async ({ page }, use) => withLoan(page, 0, use),
});
```

- Use `page.request` (or `context.request`) when the API needs the signed-in session: it sends the context's
  cookies. The `request` fixture has its own cookie store.
- Check the seed response in the fixture, with the body in the message.
- Give every record a run-unique name and delete it after `use()`.
- A fixture is set up only for the tests that ask for it; one that changes shared state belongs to a `test` of its
  own.

## Sign-in

Sign in once in a setup project, save the browser state, and start every other test signed in.

```ts
// tests/auth.setup.ts
import { test as setup, expect } from '@playwright/test';

const librarian = 'playwright/.auth/librarian.json';

setup('sign in as a librarian', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.E2E_LIBRARIAN_EMAIL!);
  await page.getByLabel('Password').fill(process.env.E2E_LIBRARIAN_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');     // prove the sign-in worked before saving it
  await page.context().storageState({ path: librarian });
});
```

The config runs the setup project first and gives its state to the others (`running.md`). Add `playwright/.auth` to
`.gitignore`: the file holds a live session. Credentials come from the environment, never the spec.

A test of the sign-in page itself, or of a signed-out user, opts out with
`test.use({ storageState: { cookies: [], origins: [] } })`.

## Locators

| Use | When |
|---|---|
| `getByRole(role, { name })` | first choice: buttons, links, headings, rows, dialogs, status |
| `getByLabel(text)` | form fields |
| `getByText(text)` | text with no role |
| `getByPlaceholder`, `getByAltText`, `getByTitle` | only when nothing above names it |
| `getByTestId(id)` | last; add an accessible name to the app before reaching for it |

- A locator must match exactly one element when you act on it. On a strictness error, narrow it: scope it under
  another locator (`page.getByRole('row', { name: 'Dune' }).getByRole('button', { name: 'Return' })`), or use
  `filter({ hasText })` or `filter({ has })`. Never `.first()` or `.nth()`: the first match changes with the page.
- Name matching is a substring by default. Pass `exact: true` when another element's name contains this one
  (`Save` and `Save draft`).
- When the app has no accessible name for a control, add one (`aria-label`, a label, a heading) instead of reaching
  for CSS.

## Waiting and actions

- Actions wait for the element to be visible, enabled and stable, and web-first assertions retry. Wait on a state
  only when the next line does not already wait for it.
- Start a wait before the action that triggers it. A fast reply arrives before a wait started after the click:

  ```ts
  // Bad: the response may come before the wait starts
  await page.getByRole('button', { name: 'Save' }).click();
  await page.waitForResponse('**/api/books');
  // Good
  const saved = page.waitForResponse('**/api/books');
  await page.getByRole('button', { name: 'Save' }).click();
  await saved;
  ```

  The same holds for `page.waitForEvent('popup')`, `page.waitForEvent('download')` and a dialog handler
  (`page.once('dialog', (dialog) => dialog.accept())`): register first, then click.
- `fill` sets the value with no key events. Use `pressSequentially` for an input that reacts to keys, such as an
  autocomplete or a masked field.
- Never `force: true`: it clicks through the overlay a real user cannot click through, and hides the bug.

## Assertions

- Use web-first matchers on locators and the page: `toHaveText`, `toContainText`, `toBeVisible`, `toBeHidden`,
  `toHaveValue`, `toHaveCount`, `toBeEnabled`, `toHaveURL`, `toHaveTitle`. They retry until the state holds or the
  timeout ends.
- A value that is not on a locator: `expect.poll(() => readIt()).toBe(...)`, or `expect(async () => {...}).toPass()`
  for a block of checks. A plain `expect(value)` checks once.
- Prove a locator matches before you negate it. A wrong locator matches nothing, so its negated assertion passes:

  ```ts
  // Bad: passes when the dialog's name is wrong, too
  await page.getByRole('button', { name: 'Confirm' }).click();
  await expect(page.getByRole('dialog', { name: 'Return book' })).not.toBeVisible();
  // Good: the same locator is seen first, then gone
  const dialog = page.getByRole('dialog', { name: 'Return book' });
  await expect(dialog).toBeVisible();
  await page.getByRole('button', { name: 'Confirm' }).click();
  await expect(dialog).toBeHidden();
  ```

- Assert what only this feature renders. A header, a footer or a shared layout renders on every page and proves
  nothing.
- `expect.soft` keeps checking after a failure; use it for several facts of one outcome, never to let a test pass.
- Give a non-obvious `expect` a message: `expect(locator, 'fine shown after a late return').toContainText(...)`.
- For text a model produced, assert the fact with `toContainText` or a pattern, never the exact sentence.

## Time

Fix the clock for anything that depends on today: due dates, fines, "3 days ago". Install the clock before the page
loads.

```ts
await page.clock.setFixedTime(new Date('2026-03-10T10:00:00Z'));
await page.goto('/loans');
```

Use `page.clock.install()` and `page.clock.fastForward('02:00')` to move time for a timer or a session expiry,
instead of waiting for it.

## Network

- Reach our own services for real; that is what the spec proves.
- Fake a third party at the network with `page.route('**/api.payments.example/**', (route) => route.fulfill({...}))`,
  or run its sandbox locally. A spec that reaches the internet fails when that site does.
- To test an outage, make the route fail (`route.abort()` or a 503) and assert what the user sees: a message, a
  retry button, no hang.

## Page objects

Use a page object only when several specs repeat one screen's locators and actions.

```ts
// tests/pages/loan-page.ts   (not *.spec.ts, so the runner does not collect it)
import { type Page, type Locator } from '@playwright/test';

export class LoanPage {
  readonly returnButton: Locator;
  readonly status: Locator;

  constructor(private readonly page: Page) {
    this.returnButton = page.getByRole('button', { name: 'Return book' });
    this.status = page.getByRole('status');
  }

  async open(loanId: string) {
    await this.page.goto(`/loans/${loanId}`);
  }
}
```

- Hand it out through a fixture, `loanPage: async ({ page }, use) => use(new LoanPage(page))`.
- Keep `expect` in the spec, not the page object, so the spec still shows what it checks.
- No `signIn()` method called in every test: the setup project signs in once. A method that only clicks through a
  flow to reach a screen becomes a `goto` on its path or an API fixture.
