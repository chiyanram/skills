# Angular UI

How to type, structure and template an Angular component and the TypeScript around it. Read it when you write or
review a `.ts` or template file in an Angular app, or its `tsconfig`.

Contents: Rules · When X, use Y · Good / Bad (NGB3) · Decided edges · Review checks

## Rules

- **NGA1** — Keep `strict` and `strictTemplates` on and fix the type error instead of setting any strict flag to
  `false`, because a disabled check lets null and type errors through to runtime.
- **NGA2** — Type a value of unknown shape as `unknown` and narrow it, never `any`, because `any` turns off type
  checking on every use of that value.
- **NGA3** — Add a check or fix the type; never silence the compiler with a non-null `!` or an `as` cast, because each
  `!` or `as` hides a runtime crash the compiler could catch.
- **NGA5** — End a `switch` over a union with `const _exhaustive: never = x` in the default arm, because without it a
  new variant compiles with no case to handle it.
- **NGA6** — Narrow a union by its discriminant, `in`, `typeof` or an `isX` type predicate, and check a value against
  a type with `satisfies`, not `as`, because `as` skips the check that `satisfies` performs.
- **NGA7** — Derive frontend DTO types from the backend's OpenAPI schema, never a hand-written parallel type, because
  a hand-written copy of the shape drifts when the schema changes.
- **NGB1** — Write standalone components, never an NgModule, and omit `standalone: true`, the default since v20,
  because NgModule declarations hide each component's dependencies and weaken tree-shaking.
- **NGB2** — Keep every component on OnPush (set it on Angular 21, omit it on 22+) and never add `Eager`, `Default` or
  Zone.js, because an eager component re-checks its whole subtree on every event.
- **NGB3** — Hold component state in `signal()` and derived state in `computed()`; use `effect()` only for side
  effects, never to copy state, because a hand-synced copy stays stale when its source loads later.
- **NGB4** — Declare inputs, outputs and two-way bindings with `input()`, `output()` and `model()`, queries with
  `viewChild()`, and host bindings in `host: {}`, never the
  `@Input`/`@Output`/`@ViewChild`/`@HostBinding`/`@HostListener` decorators, because decorator inputs are not signals
  that `computed()` can read.
- **NGC1** — Inject with `inject()` in a field initialiser, never through constructor parameters, because constructor
  injection does not work in functional guards, interceptors or field initialisers, so the code ends up with two DI
  styles.
- **NGC3** — Bind a subscription that outlives one HTTP call with `takeUntilDestroyed()`, or render it with the
  `async` pipe, because an unbound subscription keeps a destroyed component and its handlers alive.
- **NGD1** — Use `@if`, `@for` with `track`, `@switch`, `[class.x]` and `[style.x]`, never `*ngIf`, `*ngFor`,
  `ngClass`, `ngStyle` or `CommonModule`, because the directives add runtime cost and `@for` without a stable `track`
  rebuilds DOM.
- **NGD2** — Make anything clickable a `<button type="button">`, or an `<a>` for navigation, never a clickable `div`,
  `span` or `tr`, because a clickable `div` cannot take focus, so keyboard users cannot use it.
- **NGD3** — Give an icon-only button an `aria-label` or visually hidden text, not only a `title`, because `title` is
  a last-resort name that assistive technology exposes inconsistently and keyboard and touch users never see.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a `tsconfig*.json` | `strict` and `strictTemplates` on; fix the type error instead (NGA1) | "Use strict type checking" (ng-bp :5, r48 :1237) · strict "results in stronger guarantees of program correctness" (ts-hb strict.md :6, r48 :1239) |
| a value whose type the code cannot know | `unknown`, then narrow it (NGA2) | "If the type is not known, using the safer `unknown` type" (tse no-explicit-any, r48 :1247) · `unknown` "does not allow dereferencing arbitrary properties" (gts :4276, r48 :1249) · "Using `any` disables all further type checking" (ts-hb Everyday Types :46, r48 :1250) |
| an `any` that a fix cannot remove | a suppression scoped to one declaration, with a comment saying why (NGA2; CM7, `comments.md`) | Google allows a suppression with a documented reason (gts :4302-4306, r48 :1253) |
| a value the compiler thinks may be null or of another type | a check or a fixed type, never `!` or `as` (NGA3) | assertions "only silence the TypeScript compiler … they can cause your program to crash at runtime" (gts :3056-3062, r48 :1260) · an assertion "is often a sign that code is not fully type-safe" (tse no-non-null-assertion, r48 :1261) |
| a `switch` over a union | `const _exhaustive: never = x` in the default arm (NGA5) | "rely on `never` turning up to do exhaustive checking in a `switch`" (ts-hb Narrowing :711-736, r48 :1269) · "`const _exhaustive: never = x;` in default arms" (ps-ts, r48 :1270) |
| a union to narrow | its discriminant, `in`, `typeof` or an `isX` type predicate (NGA6) | type predicates and a "discriminated union … can narrow out the members" (ts-hb Narrowing :420, :658, r48 :1277) · "Narrowing hierarchy" (ps-ts, r48 :1280) |
| a value that must match a type | `satisfies`, not `as` (NGA6) | `satisfies` validates "that the type of an expression matches some type" (ts-hb 4.9 :47, r48 :1278) · "`satisfies` over `as`" (ps-ts, r48 :1280) |
| a frontend type for a backend DTO | a type derived from the OpenAPI schema (NGA7) | "derive from it instead of hand-rolling a parallel type" (ps-types :13, r48 :1287) · "no manual typing" (oats openapi-fetch :44-48, r48 :1288) |
| a new component | a standalone component, with no `standalone: true` (NGB1) | "Always use standalone components over NgModules. Must NOT set `standalone: true`" (ng-bp :11-12, r48 :1295) · standalone components "enable better tree-shaking" (angular-eslint prefer-standalone, r48 :1296) |
| a component's change detection | OnPush, never `Eager` (NGB2) | with `Eager` "the framework executes change detection on the entire component tree" (ng-onpush :20, r48 :1305) · "Use OnPush change detection strategy" (jf-angular, r48 :1309) |
| a value computed from other state | `computed()` (NGB3) | instead of copying signals with an effect, "use `computed()` or `linkedSignal()`" (ng-effect :19, r48 :1316) · "Derive instead of sync" (ps-reader :14, r48 :1319) |
| a side effect of a state change | `effect()`, never to copy state (NGB3) | "Avoid using effects for propagation of state changes" (ng-effect :29, r48 :1317) |
| a component input, output, two-way binding, query or host binding | `input()`, `output()`, `model()`, `viewChild()`, `host: {}` (NGB4) | Angular best practices (ng-bp :16, :28-29, r48 :1380) · signal APIs "integrate seamlessly with computed" (angular-eslint prefer-signals, r48 :1381) |
| a dependency in a component or service | `inject()` in a field initialiser (NGC1) | "Prefer using the `inject` function over injecting constructor parameters" (ng-sg :113-117, r48 :1326) · `inject()` is "required for using many modern Angular features like functional guards, interceptors" (angular-eslint prefer-inject, r48 :1327) |
| a subscription that outlives one HTTP call | `takeUntilDestroyed()`, or the `async` pipe (NGC3) | it unsubscribes "when a component or directive is destroyed" (ng-tud :5, r48 :1334) · "use `takeUntilDestroyed` or `async` pipe" (jf-angular, r48 :1335) |
| a conditional class or style | `[class.x]` or `[style.x]` (NGD1) | "`NgClass` and `NgStyle` directives incur an additional performance cost" (ng-sg :243, r48 :1347) · class bindings have "better performance than ngClass" (angular-eslint prefer-class-binding, r48 :1350) |
| a list in a template | `@for` with `track` (NGD1) | `track` in `@for` (ng-cf :55, :63, r48 :1348) · control flow is "more readable, performant, and type-safe" (angular-eslint prefer-control-flow, r48 :1349) |
| a clickable element | `<a>` when it navigates, `<button type="button">` when it acts (NGD2) | "NEVER use div/span as buttons" (addy-a11y :66, r48 :1357) · a `role="button"` element must be made focusable by hand (mdn-btn :31, r48 :1359) · buttons "default to `type="submit"`" (angular-eslint button-has-type, r48 :1363) |
| a button whose only content is an icon | `aria-label` or visually hidden text (NGD3) | `title` is a "last resort" source of an accessible name (apg-names :132, r48 :1369) · `title` is problematic for touch, keyboard and screen-reader users (mdn-title :103-111, r48 :1371) · "Icon-only buttons have `aria-label`" (addy-a11y :28, r48 :1373) |

Sources: `r48 :N` is the line in agent-factory `research/48-industry-recheck-code.md` that quotes the source; §5.1 of
that file names each key's repository and file. One key group is one organisation.

- ng-bp, ng-sg, ng-effect, ng-cf, ng-tud, ng-onpush: angular/angular (`packages/core/resources/best-practices.md`,
  `adev/src/content/`).
- angular-eslint: angular-eslint/angular-eslint `packages/eslint-plugin{,-template}/docs/rules/`.
- ts-hb: microsoft/TypeScript-Website handbook and release notes · tse: typescript-eslint/typescript-eslint rule docs.
- gts: google/styleguide `tsguide.md` · oats: openapi-ts/openapi-typescript READMEs.
- ps-ts, ps-types, ps-reader: cursor/plugins `pstack/skills/` · jf-angular: Jeffallan/claude-skills
  `skills/angular-architect/SKILL.md` · addy-a11y: addyosmani/agent-skills accessibility checklist.
- apg-names: w3c/aria-practices · mdn-btn, mdn-title: mdn/content.

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

- **Skip when** a `no-explicit-any` suppression is scoped to one declaration and its comment says why the `any` is safe
  (NGA2; CM7, `comments.md`; gts :4302-4306, r48 :1253). — **Do not skip when** the suppression is bare, or covers a
  block or a file: it is a finding (NGA2). — **Confidence** high
- **Skip when** the app runs Angular 22 or later: omit `changeDetection`, because OnPush is the default there (NGB2;
  ng-onpush :9, r48 :1304). — **Do not skip when** a component carries `ChangeDetectionStrategy.Eager`, which the v22
  migration adds: remove it (NGB2; angular-eslint prefer-on-push-component-change-detection, r48 :1308). —
  **Confidence** high

## Review checks

Walk every changed `.ts` file, template and `tsconfig*.json` in the Angular app.

- [ ] NGA1 — In each changed `tsconfig*.json`, `grep -nE "\"strict[A-Za-z]*\"\s*:\s*false"`. Any hit is a finding,
  and so is a strict flag removed in the same change that makes code compile.
- [ ] NGA2 — `grep -nE "\bany\b"` on changed lines. An `any` type is a finding, except under a scoped suppression with
  a comment saying why (Decided edges).
- [ ] NGA3 — On each changed line, find every non-null `!` and every `as` cast. Each one is a finding.
- [ ] NGA5 — For each `switch` over a union, find `const _exhaustive: never = x` in the default arm. A missing arm,
  or a default arm that returns or throws without it, is a finding.
- [ ] NGA6 — On each changed line, an `as` that only checks a value against a type, where `satisfies` fits, is a
  finding, and so is a union narrowed by a cast instead of its discriminant, `in`, `typeof` or an `isX` predicate.
- [ ] NGA7 — A hand-written interface or type that mirrors a backend DTO, instead of one derived from the OpenAPI
  schema, is a finding.
- [ ] NGB1 — `grep -nE "@NgModule|standalone: true"` on changed files. Any hit is a finding.
- [ ] NGB2 — On Angular 21, each changed `@Component` without `changeDetection: ChangeDetectionStrategy.OnPush` is a
  finding. On any version, `grep -nE "ChangeDetectionStrategy\.(Eager|Default)|provideZoneChangeDetection|zone\.js"`;
  any hit is a finding.
- [ ] NGB3 — A plain field that holds component state, a `.set()` of a value derived from other state, or an
  `effect()` that copies state into a signal, is a finding.
- [ ] NGB4 — `grep -nE "@(Input|Output|ViewChild|HostBinding|HostListener)\("` on changed files. Any hit is a
  finding.
- [ ] NGC1 — For each changed class, a constructor parameter that injects a dependency is a finding.
- [ ] NGC3 — For each `.subscribe(` on router events, an interval, an event stream or any other source that
  outlives one HTTP call, find `takeUntilDestroyed()` in its pipe or the `async` pipe in the template. A missing one
  is a finding, and so is a `takeUntilDestroyed()` with no `DestroyRef` outside a constructor or field initialiser.
- [ ] NGD1 — `grep -nE "\*ngIf|\*ngFor|ngSwitch|ngClass|ngStyle|CommonModule"` on changed files. Any hit is a
  finding, and so is a `@for` without `track`.
- [ ] NGD2 — `grep -nE "<(div|span|tr)[^>]*\(click\)"` on changed templates. Any hit is a finding, and so is a
  `<button>` without `type="button"` outside a form submit.
- [ ] NGD3 — For each button whose only content is an icon, find `aria-label` or visually hidden text. A button with
  only a `title`, or with neither, is a finding.
