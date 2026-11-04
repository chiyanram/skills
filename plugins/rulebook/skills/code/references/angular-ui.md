# Angular UI

How to type, structure and template an Angular component and the TypeScript around it. Read it when you write or review
an Angular component, a `.ts` or template file in an Angular app, or its `tsconfig`.

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
| a `tsconfig*.json` | `strict` and `strictTemplates` on; fix the type error instead (NGA1) | a disabled check lets null and type errors through to runtime |
| a value whose type the code cannot know | `unknown`, then narrow it (NGA2) | `any` turns off type checking on every use of that value |
| an `any` that a fix cannot remove | a suppression scoped to one declaration, with a comment saying why (NGA2; CM7, `comments.md`) | a bare or wide suppression hides the next real bug |
| a value the compiler thinks may be null or of another type | a check or a fixed type, never `!` or `as` (NGA3) | each `!` or `as` hides a runtime crash the compiler could catch |
| a `switch` over a union | `const _exhaustive: never = x` in the default arm (NGA5) | a new variant then fails to compile until it has a case |
| a union to narrow | its discriminant, `in`, `typeof` or an `isX` type predicate (NGA6) | the compiler checks each narrowed branch |
| a value that must match a type | `satisfies`, not `as` (NGA6) | `as` skips the check that `satisfies` performs |
| a frontend type for a backend DTO | a type derived from the OpenAPI schema (NGA7) | a hand-written copy drifts when the schema changes |
| a new component | a standalone component, with no `standalone: true` (NGB1) | NgModule declarations hide each component's dependencies and weaken tree-shaking |
| a component's change detection | OnPush, never `Eager` (NGB2) | an eager component re-checks its whole subtree on every event |
| a value computed from other state | `computed()` (NGB3) | a hand-synced copy stays stale when its source loads later |
| a side effect of a state change | `effect()`, never to copy state (NGB3) | an effect that copies state is a hand-synced copy |
| a component input, output, two-way binding, query or host binding | `input()`, `output()`, `model()`, `viewChild()`, `host: {}` (NGB4) | decorator inputs are not signals that `computed()` can read |
| a dependency in a component or service | `inject()` in a field initialiser (NGC1) | constructor injection does not work in functional guards or interceptors, so the code ends up with two DI styles |
| a subscription that outlives one HTTP call | `takeUntilDestroyed()`, or the `async` pipe (NGC3) | an unbound subscription keeps a destroyed component and its handlers alive |
| a conditional class or style | `[class.x]` or `[style.x]` (NGD1) | `ngClass` and `ngStyle` add runtime cost |
| a list in a template | `@for` with `track` (NGD1) | `@for` without a stable `track` rebuilds DOM |
| a clickable element | `<a>` when it navigates, `<button type="button">` when it acts (NGD2) | a clickable `div` cannot take focus, and a bare `<button>` submits its form |
| a button whose only content is an icon | `aria-label` or visually hidden text (NGD3) | `title` is a last-resort name that assistive technology exposes inconsistently |

## Good / Bad

### NGB3 — State in `signal()`, derived state in `computed()`; `effect()` never copies

**Bad**
```ts
readonly shipments = signal<Shipment[]>([]);
readonly carrier = signal('all');
readonly visibleShipments = signal<Shipment[]>([]);

onCarrierChange(carrier: string): void {
  this.carrier.set(carrier);
  this.visibleShipments.set(
    this.shipments().filter((shipment) => carrier === 'all' || shipment.carrier === carrier),
  );
}
```
`visibleShipments` is a copy that one handler syncs. When the shipments load after the user picks a carrier, the list
stays empty until the next pick. An `effect()` that calls `.set()` here makes the same copy.

**Good**
```ts
readonly shipments = signal<Shipment[]>([]);
readonly carrier = signal('all');
readonly visibleShipments = computed(() =>
  this.shipments().filter(
    (shipment) => this.carrier() === 'all' || shipment.carrier === this.carrier(),
  ),
);

onCarrierChange(carrier: string): void {
  this.carrier.set(carrier);
}
```
The list is derived from both signals, so it is correct whichever value changes first.

## Decided edges

- **Skip when** a `no-explicit-any` suppression is scoped to one declaration and its comment says why the `any` is safe
  (NGA2; CM7, `comments.md`). — **Do not skip when** the suppression is bare, or covers a block or a file: it is a
  finding (NGA2). — **Confidence** high
- **Skip when** the app runs Angular 22 or later: omit `changeDetection`, because OnPush is the default there (NGB2).
  — **Do not skip when** a component carries `ChangeDetectionStrategy.Eager`, which the v22 migration adds: remove it
  (NGB2). — **Confidence** high

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
