# Angular UI

How to type, structure and template an Angular component and the TypeScript around it. Read it when you write or
review a `.ts` or template file in an Angular app, or its `tsconfig`.

Contents: Rules · When X, use Y · Good / Bad (NGB3) · Decided edges · Review checks

## Rules

- **NGA1** — Keep `strict`, the extra strict flags and `strictTemplates`; never loosen a compiler flag to make code
  compile, because a loosened flag hides a type error, which leaves a latent runtime crash.
- **NGA2** — Use `unknown` and narrow it, never `any`, and never suppress `no-explicit-any` (CM7, `comments.md`),
  because `any` switches off the compiler's check on every property access.
- **NGA3** — Add a check or fix the type; never silence the compiler with a non-null `!` or an `as` cast, because
  each `!` or `as` hides a runtime crash the compiler could catch.
- **NGA5** — End a `switch` over a union with `const _exhaustive: never = x` in the default arm, because without it a
  new variant compiles with no case to handle it.
- **NGA6** — Narrow by discriminant, then `in`, then `typeof`, then an `isX` type guard that checks what it claims;
  use `satisfies`, not `as`, because a guard that lies hides its bug behind a name that says safe.
- **NGA7** — Derive frontend DTO types from the backend's OpenAPI schema, never a hand-written parallel type, because
  a hand-written copy of the shape drifts when the schema changes.
- **NGB1** — Write standalone components only, never an NgModule, and omit `standalone: true` (the v21 default),
  because agents copy the redundant `standalone: true` flag into new files.
- **NGB2** — Set `changeDetection: ChangeDetectionStrategy.OnPush` on every component and keep the app zoneless,
  because checking the whole tree on every change slows the app, and OnPush skips unchanged subtrees.
- **NGB3** — Hold component state in `signal()` and derived state in `computed()`; use `effect()` only for side
  effects, never to copy state, because a hand-synced copy stays stale when its source loads later.
- **NGC1** — Inject with `inject()` in a field initialiser, never through constructor parameters, because `inject()`
  reads better with many dependencies and infers types better than a long constructor list.
- **NGC3** — Bind a subscription that outlives one HTTP call (router events, an interval, SSE) with
  `takeUntilDestroyed()`, because an unbound subscription leaks memory until the page crashes.
- **NGD1** — Use `@if`, `@for (track)`, `@switch`, `[class.x]` and `[style.x]`, never `*ngIf`, `*ngFor`, `ngClass`,
  `ngStyle` or `CommonModule`, because NgClass and NgStyle cost performance and `@for` reuses views.
- **NGD2** — Make anything clickable a `<button type="button">`, or an `<a>` for navigation, never a clickable `div`,
  `span` or `tr`, because a clickable `div` cannot take focus, so keyboard users cannot use it.
- **NGD3** — Give an icon-only button an `aria-label`, not only a `title`, because a screen reader has no name to read
  for an icon-only button.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a value whose type the code cannot know | `unknown`, then narrow it (NGA2) | `any` switches off the check on every property access · 19:320 |
| a union to tell apart | the discriminant, then `in`, then `typeof`, then an `isX` guard (NGA6) | a guard that lies hides its bug behind a safe name · 19:324 |
| a value that must match a type | `satisfies`, not `as` (NGA6) | `as` hides a crash the compiler could catch (NGA3) · 19:324 |
| a `switch` over a union | `const _exhaustive: never = x` in the default arm (NGA5) | a new variant fails to compile · 19:323 |
| a frontend type for a backend DTO | a type derived from the OpenAPI schema (NGA7) | a hand-written copy drifts · 19:325 |
| a value computed from other state | `computed()` (NGB3) | a copy goes stale · 19:328 · angular.dev effect guide: copying state with an effect means use `computed()` |
| a side effect of a state change | `effect()`, never to copy state (NGB3) | 19:328 · angular.dev effect guide |
| a dependency in a component or service | `inject()` in a field initialiser (NGC1) | better readability and type inference · angular.dev style guide §inject · 31:44 |
| a subscription that outlives one HTTP call | `takeUntilDestroyed()` (NGC3) | it unsubscribes when the component is destroyed · 19:333 · angular.dev rxjs-interop |
| a conditional class or style | `[class.x]` or `[style.x]` (NGD1) | NgClass and NgStyle cost performance · angular.dev style guide · 31:46 |
| a list in a template | `@for` with `track` (NGD1) | `@for` reuses views · angular.dev control flow · 31:46 |
| a clickable element | `<a>` when it navigates, `<button type="button">` when it acts (NGD2) | a clickable `div` cannot take focus · 19:336 |
| a button whose only content is an icon | `aria-label` (NGD3) | a `title` gives a screen reader no name · 19:337 |

19 is `research/19-approved-rules.md` in this repo, the ledger; 31 is agent-factory `research/31-missing-reasons.md`.
`:N` is a line in that file. The reasons of NGA1, NGB2, NGC1 and NGD1 come from 31:39, :41, :44 and :46; their
ledger rows have none.

## Good / Bad

### NGB3 — State in `signal()`, derived state in `computed()`; `effect()` never copies

**Bad** (neutral)
```ts
customerId = '';
allInvoices = signal<InvoiceResponse[]>([]);
customerInvoices = signal<InvoiceResponse[]>([]);
…
        this.customerId = payment.customerId;
        this.filterInvoices(payment.customerId);
…
onCustomerChange(customerId: string) {
  this.filterInvoices(customerId);
  this.allocations.update((allocations) => allocations.map((allocation) => ({ ...allocation, invoiceId: '' })));
}

private filterInvoices(customerId: string) {
  this.customerInvoices.set(this.allInvoices().filter((invoice) => invoice.customerId === customerId && invoice.status === 'OPEN'));
}
```
The open-invoice list is a hand-synced copy. If the payment loads before the invoices, it filters an empty list and
stays empty.

**Good** (neutral)
```ts
readonly customerId = signal('');
readonly allInvoices = signal<InvoiceResponse[]>([]);
readonly customerInvoices = computed(() =>
  this.allInvoices().filter(
    (invoice) => invoice.customerId === this.customerId() && invoice.status === 'OPEN',
  ),
);
// on load: this.customerId.set(payment.customerId);  — nothing to re-filter

onCustomerChange(customerId: string): void {
  this.customerId.set(customerId);
  this.allocations.update((allocations) =>
    allocations.map((allocation) => ({ ...allocation, invoiceId: '' })),
  );
}
```
The filtered list is derived from both signals, so it is right whichever request lands first, and `filterInvoices`
is deleted. (Real evidence: ledger row NGB3.)

## Decided edges

- **Skip when** an existing `!` sits on a line the change does not touch: leave it (NGA3; 19:321). — **Do not skip
  when** the change touches that line: add the check or fix the type there. — **Confidence** high
- **Skip when** the suppressed lint rule is style-only (CM7, `comments.md`). — **Do not skip when** the rule is
  `no-explicit-any`: it is never suppressed, even with a stated reason (NGA2; X6, 19:377). — **Confidence** high
- **Skip when** the app runs Angular 22 or later: do not set `changeDetection: ChangeDetectionStrategy.OnPush`,
  because OnPush is the default there (NGB2; angular.dev `assets/context/best-practices.md:13`). — **Do not skip
  when** the app runs Angular 21: set it on every component (NGB2). — **Confidence** high
- **Skip when** the code builds a form on Angular 21: this file has no forms rule. — **Do not skip when** the app
  runs Angular 22 or later: new forms use Signal Forms (OQ-NG1, 19:396). — **Confidence** high

## Review checks

Walk every changed `.ts` file, template and `tsconfig*.json` in the Angular app.

- [ ] NGA1 — In each changed `tsconfig*.json`, find `strict`, every extra strict flag and `strictTemplates`. A flag
  removed, set to `false`, or loosened in the same change that makes code compile is a finding.
- [ ] NGA2 — `grep -nE "\bany\b"` on changed lines. An `any` type, or an `eslint-disable` naming `no-explicit-any`,
  is a finding.
- [ ] NGA3 — On each changed line, find every non-null `!` and every `as` cast. Each one is a finding, except a
  pre-existing `!` on an untouched line (Decided edges).
- [ ] NGA5 — For each `switch` over a union, find `const _exhaustive: never = x` in the default arm. A missing arm,
  or a default arm that returns or throws without it, is a finding.
- [ ] NGA6 — For each narrowing, the order is discriminant, `in`, `typeof`, then a guard. A guard not named `isX`, a
  guard that checks less than its type claims, or an `as` where `satisfies` fits, is a finding.
- [ ] NGA7 — A hand-written interface or type that mirrors a backend DTO, instead of one derived from the OpenAPI
  schema, is a finding.
- [ ] NGB1 — `grep -nE "@NgModule|standalone: true"` on changed files. Any hit is a finding.
- [ ] NGB2 — For each changed `@Component`, find `changeDetection: ChangeDetectionStrategy.OnPush`. A component
  without it is a finding, except on Angular 22 or later (Decided edges). A change that adds Zone.js change detection
  back is a finding.
- [ ] NGB3 — A plain field that holds component state, a `.set()` of a value derived from other state, or an
  `effect()` that copies state into a signal, is a finding.
- [ ] NGC1 — For each changed class, a constructor parameter that injects a dependency is a finding.
- [ ] NGC3 — For each `.subscribe(` on router events, an interval, SSE or any other source that outlives one HTTP
  call, find `takeUntilDestroyed()` in its pipe. A missing one is a finding.
- [ ] NGD1 — `grep -nE "\*ngIf|\*ngFor|ngSwitch|ngClass|ngStyle|CommonModule"` on changed files. Any hit is a
  finding, and so is a `@for` without `track`.
- [ ] NGD2 — `grep -nE "<(div|span|tr)[^>]*\(click\)"` on changed templates. Any hit is a finding, and so is a
  `<button>` without `type="button"` outside a form submit.
- [ ] NGD3 — For each button whose only content is an icon, find `aria-label`. A button with only a `title`, or with
  neither, is a finding.
