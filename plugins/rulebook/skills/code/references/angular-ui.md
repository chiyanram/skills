# Angular UI

How to type, structure and template an Angular component and the TypeScript around it. Read it when you write or
review a `.ts` or template file in an Angular app, or its `tsconfig`.

Contents: Rules · When X, use Y · Good / Bad (NGB3) · Decided edges · Review checks

## Rules

- **NGA1** — Keep `strict`, the extra strict flags and `strictTemplates`; never loosen a compiler flag to make code
  compile, because a loosened flag hides a type error, which leaves a latent runtime crash.
- **NGA2** — Use `unknown` and narrow it, never `any`; suppress `no-explicit-any` only with a one-line reason that
  names the untyped library, because `any` switches off the compiler's check on every property access.
- **NGA3** — Add a check or fix the type; never silence the compiler with a non-null `!` or an `as` cast, because
  each `!` or `as` hides a runtime crash the compiler could catch.
- **NGA5** — End a `switch` over a union with `const _exhaustive: never = x` in the default arm, because without it a
  new variant compiles with no case to handle it.
- **NGA6** — Check a value against a type with `satisfies`, not `as`, because `satisfies` validates the value
  without widening it, while `as` hides a mismatch the compiler could catch.
- **NGA7** — Derive frontend DTO types from the backend's OpenAPI schema, never a
  hand-written parallel type, because a hand-written copy of the shape drifts when the schema changes.
- **NGB1** — Write standalone components only, never an NgModule, and omit `standalone: true`, because standalone is
  the default from Angular v20, so the flag and an NgModule only add declarations the framework no longer needs.
- **NGB2** — Set `changeDetection: ChangeDetectionStrategy.OnPush` on every component and keep the app zoneless,
  because ZoneJS runs change detection more often than state changes, and OnPush is Angular's step towards zoneless.
- **NGB3** — Hold component state in `signal()` and derived state in `computed()`; use `effect()` only for side
  effects, never to copy state, because a hand-synced copy stays stale when its source loads later.
- **NGC1** — Inject with `inject()` in a field initialiser, never through
  constructor parameters, because `inject()` reads better with many dependencies and infers types better than a long
  constructor list.
- **NGC3** — Bind a subscription that outlives one HTTP call (router events, an interval, an event stream) with
  `takeUntilDestroyed()`, because an unbound subscription leaks memory until the page crashes.
- **NGD1** — Use `@if`, `@for (track)`, `@switch`, `[class.x]` and `[style.x]`, never `*ngIf`, `*ngFor`, `ngClass`,
  `ngStyle` or `CommonModule`, because Angular's guidance replaces them, and `track` maps each item to its DOM
  nodes, which speeds list rendering.
- **NGD2** — Make anything clickable a `<button type="button">`, or an `<a>` for navigation, never a clickable `div`,
  `span` or `tr`, because a clickable `div` cannot take focus, so keyboard users cannot use it.
- **NGD3** — Give an icon-only button an `aria-label`, not only a `title`, because a screen reader has no name to read
  for an icon-only button.

## When X, use Y

| the code has | use | why |
|---|---|---|
| a value whose type the code cannot know | `unknown`, then narrow it (NGA2) | `any` switches off the check on every property access · angular.dev best practices "use `unknown` when type is uncertain"; Google TypeScript Style Guide §Using unknown over any; pstack typescript-best-practices "External data is `unknown`" |
| an untyped library that forces `any` | a `no-explicit-any` suppression with a one-line reason naming the library (NGA2) | Google TypeScript Style Guide §Suppressing any lint warnings "document why it is legitimate" |
| a value that must match a type | `satisfies`, not `as` (NGA6) | `as` hides a crash the compiler could catch (NGA3) · TypeScript 4.9 release notes §satisfies; pstack typescript-best-practices "`satisfies` over `as`"; Jeffallan typescript-pro |
| a `switch` over a union | `const _exhaustive: never = x` in the default arm (NGA5) | a new variant fails to compile · TypeScript handbook §Exhaustiveness checking; pstack typescript-best-practices; Jeffallan typescript-pro |
| a frontend type for a backend DTO | a type derived from the OpenAPI schema (NGA7) | a hand-written copy drifts · operator preference; pstack `references/patterns.md` "derive from the generated types instead of duplicating" |
| a value computed from other state | `computed()` (NGB3) | a copy goes stale · angular.dev effect guide "Always prefer computed()"; angular.dev best practices; pstack principle-minimize-reader-load "Derive instead of sync" |
| a side effect of a state change | `effect()`, never to copy state (NGB3) | angular.dev effect guide "Effects should be the last API you reach for" |
| a dependency in a component or service | `inject()` in a field initialiser (NGC1) | operator preference · angular.dev style guide §Prefer the inject function over constructor parameter injection |
| a subscription that outlives one HTTP call | `takeUntilDestroyed()` (NGC3) | it unsubscribes when the component is destroyed · angular.dev rxjs-interop `takeUntilDestroyed`; Jeffallan angular-architect "Forget to unsubscribe" |
| a conditional class or style | `[class.x]` or `[style.x]` (NGD1) | angular.dev best practices "Do NOT use `ngClass`, use `class` bindings instead" |
| a list in a template | `@for` with `track` (NGD1) | `track` maps items to DOM nodes and speeds rendering · angular.dev control flow §Why is track in @for blocks important; Jeffallan angular-architect `references/components.md` |
| a clickable element | `<a>` when it navigates, `<button type="button">` when it acts (NGD2) | a clickable `div` cannot take focus · WCAG 2.1.1 Keyboard; addyosmani accessibility-checklist "NEVER use div/span as buttons" |
| a button whose only content is an icon | `aria-label` (NGD3) | a screen reader needs a name · WCAG 4.1.2 Name, Role, Value; addyosmani accessibility-checklist "Icon-only buttons have `aria-label`" |

Operator preference, 2026-10-31 (SRC2), in whole or in part: NGA7 and NGC1.

## Good / Bad

### NGB3 — State in `signal()`, derived state in `computed()`; `effect()` never copies

**Bad** (neutral)
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

**Good** (neutral)
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

- **Skip when** an existing `!` sits on a line the change does not touch: leave it (NGA3). — **Do not skip
  when** the change touches that line: add the check or fix the type there. — **Confidence** high
- **Skip when** the suppressed lint rule is style-only (CM7, `comments.md`), or is `no-explicit-any` with a one-line
  reason that names the untyped library (NGA2; Google TypeScript Style Guide §Suppressing any lint warnings).
  — **Do not skip when** a `no-explicit-any` suppression is bare: it is a finding (NGA2). — **Confidence** high
- **Skip when** the app runs Angular 22 or later: do not set `changeDetection: ChangeDetectionStrategy.OnPush`,
  because OnPush is the default there (NGB2; angular.dev `assets/context/best-practices.md:13`). — **Do not skip
  when** the app runs Angular 21: set it on every component (NGB2). — **Confidence** high
- **Skip when** the code builds a form on Angular 21: this file has no forms rule. — **Do not skip when** the app
  runs Angular 22 or later: new forms use Signal Forms (angular.dev `assets/context/best-practices.md:33`). —
  **Confidence** high

## Review checks

Walk every changed `.ts` file, template and `tsconfig*.json` in the Angular app.

- [ ] NGA1 — In each changed `tsconfig*.json`, find `strict`, every extra strict flag and `strictTemplates`. A flag
  removed, set to `false`, or loosened in the same change that makes code compile is a finding.
- [ ] NGA2 — `grep -nE "\bany\b"` on changed lines. An `any` type is a finding, and so is an `eslint-disable`
  naming `no-explicit-any` without a one-line reason that names the untyped library.
- [ ] NGA3 — On each changed line, find every non-null `!` and every `as` cast. Each one is a finding, except a
  pre-existing `!` on an untouched line (Decided edges).
- [ ] NGA5 — For each `switch` over a union, find `const _exhaustive: never = x` in the default arm. A missing arm,
  or a default arm that returns or throws without it, is a finding.
- [ ] NGA6 — On each changed line, an `as` that only checks a value against a type, where `satisfies` fits, is a
  finding.
- [ ] NGA7 — A hand-written interface or type that mirrors a backend DTO, instead of one derived from the OpenAPI
  schema, is a finding.
- [ ] NGB1 — `grep -nE "@NgModule|standalone: true"` on changed files. Any hit is a finding.
- [ ] NGB2 — For each changed `@Component`, find `changeDetection: ChangeDetectionStrategy.OnPush`. A component
  without it is a finding, except on Angular 22 or later (Decided edges). A change that adds Zone.js change detection
  back is a finding.
- [ ] NGB3 — A plain field that holds component state, a `.set()` of a value derived from other state, or an
  `effect()` that copies state into a signal, is a finding.
- [ ] NGC1 — For each changed class, a constructor parameter that injects a dependency is a finding.
- [ ] NGC3 — For each `.subscribe(` on router events, an interval, an event stream or any other source that
  outlives one HTTP call, find `takeUntilDestroyed()` in its pipe. A missing one is a finding.
- [ ] NGD1 — `grep -nE "\*ngIf|\*ngFor|ngSwitch|ngClass|ngStyle|CommonModule"` on changed files. Any hit is a
  finding, and so is a `@for` without `track`.
- [ ] NGD2 — `grep -nE "<(div|span|tr)[^>]*\(click\)"` on changed templates. Any hit is a finding, and so is a
  `<button>` without `type="button"` outside a form submit.
- [ ] NGD3 — For each button whose only content is an icon, find `aria-label`. A button with only a `title`, or with
  neither, is a finding.
