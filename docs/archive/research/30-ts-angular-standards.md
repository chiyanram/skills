# R26 · TypeScript + Angular coding standards — ours vs sources (2026-10-02)

Ticket: chiyanram/skills#49 (part of #9 · feeds #33 G9b angular-ui, and #32 frontend-unit group).
Scope: standards only. Frontend **testing** is R18 (`22-playwright-frontend-testing.md`, F1–F10) — not redone here.
Baseline: `origin/master` @ `0aa04944` (2026-10-02). Nothing below is approved.

## Sources read

| source | what | date / ★ |
|---|---|---|
| ours `.claude/rules/angular-ui.md` (16 lines) | icon/select rule | master |
| ours `.claude/skills/aruvii-standards/references/angular-ui.md` (98 lines) | examples | master |
| ours `CLAUDE.md:246-255` | Angular block | master |
| ours `aruvii-ui/eslint.config.js` (133), `tsconfig*.json`, `package.json`, `angular.json`, `.prettierrc.json` | config | master |
| ours code sample: `shared/icon.component.ts`, `shared/select.component.ts`, `shared/async-state.ts`, `core/confirm.service.ts`, `core/agent.service.ts`, `features/agents/agent-list.component.ts`, `app.config.ts`, `app.routes.ts` + grep counts over all 120 non-spec `.ts` | | master |
| Angular `packages/core/resources/best-practices.md` (official LLM rules) | main @ f53b3b6e (2026-09-09, targets v22) **and** tag 21.0.3 (our major) | angular/angular 101k★ |
| angular.dev/style-guide (`adev/.../style-guide.md` @ cf70bcfe 2026-07-07) | | same |
| angular.dev guides: zoneless, signals/effect, rxjs-interop/take-until-destroyed | | fetched 2026-10-02 |
| angular-eslint README @ v21.3.1 (ours locks 21.4.0) + main; `docs/CONFIGURING_ESLINT.md` | rule sets, inline-template processor | 1.8k★ (tool we already run) |
| typescript-eslint.io/users/configs | recommended / strict / stylistic | 16.4k★ |
| typescriptlang.org/tsconfig | strict family | microsoft/TypeScript 111k★ |
| Google TypeScript Style Guide | | google/styleguide 39.6k★ |
| addy `skills/frontend-ui-engineering/SKILL.md` @ 2686b62 | a11y, states, red flags (React-flavoured) | addyosmani/agent-skills 100k★ |
| PatrickJS/awesome-cursorrules `rules/angular-typescript-cursorrules-prompt-file.mdc` | **rejected**: Angular 18, persona prose, project-specific (`forNext`, `smart-ngrx`) | 40.9k★ |
| airbnb/javascript 148k★, clean-code-javascript 94.8k★ | JS-only, not TS/Angular; not used | — |
| google/gts 5.3k★, labs42io/clean-code-typescript 9.8k★ | below 10k bar; not used | — |

Versions locked on master: `@angular/core` 21.2.21 · TypeScript 5.9.3 · typescript-eslint 8.67.0 · `@angular-eslint/eslint-plugin` 21.4.0.

**Version trap.** angular.dev and `best-practices.md` on main now target **v22** ("OnPush is the default in v22+, do NOT set it"; "Prefer Signal Forms"). On our v21 the same file at tag 21.0.3 says the opposite: `best-practices.md:29` *Set `changeDetection: ChangeDetectionStrategy.OnPush`*, `:31` *Prefer Reactive forms*. Every rule below is pinned to v21.

---

## 3 · What the code actually does (master, non-spec `.ts`, inline templates)

All 68 components use inline `template:` — 0 `templateUrl`, 1 `.html` file (`index.html`). The app is **zoneless** (`app.config.ts:11 provideZonelessChangeDetection()`).

```
STRUCTURE
  NgModule ............................ 0        standalone: true written ........ 68 / 68
  routes loadComponent ................ 35       eager component: ................ 1 (ShellComponent, layout)
  cross-feature imports ............... 0 / 375 parent imports (all go to core/ or shared/)
  components > 600 lines .............. 11       (tool-form 3062, chat-session 2063, tool-detail 2017)

DI
  inject() calls ...................... 233 in 97 files
  constructor-parameter DI ............ 0
  components calling HttpClient ....... 2  (auth/forgot-password, auth/reset-password)

SIGNALS / CHANGE DETECTION
  signal( ............................. 512      computed( ....................... 100     effect( .. 2
  input() / @Input .................... 43 / 15  output() / @Output+EventEmitter .. 11 / 5+5
  viewChild() / @ViewChild ............ 0 / 3    host:{} / @HostListener+@HostBinding .. 0 / 6+1
  OnPush .............................. 32 / 68 components

RXJS
  .subscribe( ......................... 258 in 47 files
  takeUntilDestroyed / toSignal ....... 0 / 0    manual ngOnDestroy ............. 6
  error: () => {} (swallowed) ......... 19 in 11 files   toast.error( ......... 117

TEMPLATES
  @if / @for / @switch ................ 649 / 180 / 5
  *ngIf / *ngFor in templates ......... 0 / 0  (1 *ngFor inside a doc comment, async.component.ts:21)
  CommonModule imported ............... 3 files   [ngClass]/[ngStyle] .. 0   [class.x] .. 75
  FormsModule / ngModel ............... 66 files / 285   ReactiveForms ... 0
  (click) on div/span/li/tr/td ........ 37     aria-label ... 25

TYPES
  any ................................. 1  (confirm.service.ts:18, eslint-disable'd)
  non-null `!` ........................ ~243 in 53 files (regex estimate)
  `as X` casts ........................ 77   as unknown as ... 1
  @ts-ignore/expect-error ............. 0    enum ... 0   export default ... 0   namespace ... 0   var ... 0
  private / protected / #private ...... 336 / 87 / 7
  AsyncState<T> users ................. 2 files  vs  `loading = signal` .. 34

ICONS (our rule)
  <app-icon> .......................... 229    <app-select> ... 17   native <select> ... 41 (text-only)
  <mat-icon> / FontAwesome / icon pkg . 0 / 0 / 0
  stroke= on app-icon ................. 0
  emoji / unicode symbol chars in templates . 83 in 7 files   <-- rule broken
```

---

## 1 · Disposition of every existing rule

```
id   rule (where)                                         true on master?          sources          disposition
E1   icons: app-icon only; no emoji, mat-icon, FA          mat/FA yes · emoji NO    ours only        KEEP + tighten (G-E1)
     (rules/angular-ui.md:8, CLAUDE.md:249)               83 symbols, 7 files
E2   icon dropdowns: app-select only (rules :9)           YES (0 emoji options)    ours only        KEEP (G-E2)
E3   colour via [style.color] on parent (rules :10)       YES (0 stroke=)          ours only        MERGE into G-E3
E4   agent-icon exempt (rules :11, ref §4)                YES (7 uses)             ours only        KEEP as decided edge
E5   add icons to LUCIDE only; no icon packages (ref :40-44) YES (0 packages)      ours only        MERGE into G-E1
E6   defaults 1.75 / 16 px (ref :46-47)                   YES icon.component:125-126  —             KEEP as reference fact, not a rule
E7   "Rules: CLAUDE.md §Angular Icon & Select Standard"   NO — section moved to     —               REWRITE pointer
     (ref :3)                                             rules/angular-ui.md (9081a945)
E8   "eslint carries no icon or select rule (#147)"       true, but #147 is about   —               REWRITE citation
     (ref :11)                                            the false header, not icons
E9   standalone only, no NgModules (CLAUDE.md:248)        YES 0 / 68               Angular 21.0.3:11  KEEP + REWRITE (G-B1: also stop writing standalone:true)
E10  unit tests for service calls, signal state,          —                        R18 F10          MERGE → testing (R18), not here
     error paths (CLAUDE.md:252)
E11  UI wired to real API, E2E reachable (CLAUDE.md:253)  —                        —                KEEP, but it is a DoD rule; move to DoD
E12  eslint header claims "standalone only" and           NO — neither rule exists  #147 (open)     REWRITE (G-F2)
     "lazy-loaded routes" enforced (eslint :13-14)
E13  no-console (eslint :53)                              YES 0 console.log        Google; addy      KEEP (config)
E14  no-explicit-any outside specs (eslint :54)           YES (1, suppressed)      Google; Angular :7  KEEP (G-A2)
E15  max-lines 600 warn in features/ (eslint :56)         11 files over; warn never  addy "200 lines" KEEP as warn; say what it is (G-B5)
                                                          fails the build
E16  module boundaries core/shared/features (eslint :62-100)  YES 0 violations,     Angular style "by feature"  REWRITE (G-F3): zones cover
                                                          but cross-feature zones                    4 of 20 features
                                                          name 4 targets of 20
E17  4 Angular rules (class-suffix x2, empty-lifecycle,   YES                      angular-eslint    REPLACE by tsRecommended (G-F1)
     use-lifecycle-interface) (eslint :103-106)
E18  *.html template block, rules: {} (eslint :112-117)   dead: 68/68 inline,       angular-eslint    REWRITE (G-F1: processInlineTemplates)
                                                          no processor, no rules    CONFIGURING_ESLINT.md:50-114
E19  tsconfig strict + noImplicitOverride, noPropertyAccess- YES                   = Angular CLI defaults  KEEP (G-A1)
     FromIndexSignature, noImplicitReturns, noFallthrough,
     strictTemplates/InjectionParameters/InputAccessModifiers
```

## 2 · False or stale claims

1. `eslint.config.js:13-14` — claims standalone-only and lazy routes are enforced. **Neither rule is configured.** Already GitLab **#147** (open, P7).
2. `eslint.config.js:110-111` — "rules ready for when a component splits to .html". The block has `rules: {}` and no inline-template processor, so **zero template linting happens on 68 inline templates**.
3. `eslint.config.js:42` turns on typed linting (`parserOptions.project`) but no type-checked rule is used — the cost is paid, nothing is checked.
4. `references/angular-ui.md:3` — points at a CLAUDE.md section that no longer exists (moved to `.claude/rules/angular-ui.md` in 9081a945).
5. `references/angular-ui.md:11` — cites **#147** for "no icon/select lint rule"; #147 is the false-header ticket. The icon rule has no ticket.
6. `rules/angular-ui.md:8` "never raw emoji as an icon" — **broken 83 times in 7 files**: e.g. `settings.component.ts:661` (🗑 is the button's only content), `tool-form.component.ts:944` (🔍 Discover Tools). Nothing gates it.
7. Every component writes `standalone: true` (68/68). Angular 21.0.3 `best-practices.md:12`: *Must NOT set `standalone: true` … default in Angular v20+.* Harmless but noise an agent copies.
8. Frontend Husky `pre-commit` runs `npm test` only; `lint-staged` is configured in `package.json:35-46` but never invoked. Lint runs only via `make lint` / `make verify` (`Makefile:347,385`).

## 4 · Missing rules (the code already mostly follows them — cheap to codify)

| what | code today | source |
|---|---|---|
| `inject()` not constructor DI | 233 / 0 | style guide §DI; best-practices.md:55 (21.0.3) |
| signal `input()/output()/viewChild()` not decorators | 43 vs 15 | best-practices.md:28 |
| OnPush on every component (zoneless app) | 32 / 68 | 21.0.3 :29; zoneless guide "recommended step" |
| `effect()` only for side effects | 2 uses | angular.dev effect guide |
| subscriptions bound to component lifetime | 0 takeUntilDestroyed | rxjs-interop guide |
| never swallow an error | 19 `error: () => {}` | CLAUDE.md observability spirit; addy :324 |
| clickable = `<button>`; icon-only button has `aria-label` | 37 clickable divs; 🗑 button unlabeled | best-practices.md:22-23 (WCAG AA); addy :180-210; angular-eslint templateAccessibility |
| no non-null `!` / cast to silence the compiler | ~243 `!` | Google TS §non-null, §type assertions |
| closed value sets = string-literal unions, not TS `enum` | 0 enums | resolves CLAUDE.md "enums over string literals" (Java) for TS |
| a linter config that actually covers templates | none | angular-eslint CONFIGURING_ESLINT.md:50-114 |

---

## 5 · GROUPS for the operator — nothing approved

Each rule ≤25 words · source · recommendation. G5 shape per group: Rules · When X use Y · Good/Bad · Decided edges · Review checks.

### G-A · TypeScript strictness

1. Keep `strict` plus the four extra flags and `strictTemplates`; never loosen a compiler flag to make code compile.
   *Src: tsconfig.json:6-10,22-26 (= Angular CLI defaults); TS tsconfig ref.* — **KEEP (codify)**
2. No `any`. Use `unknown` and narrow it. A suppressed `any` needs a one-line reason beside the disable.
   *Src: Google TS §any; Angular best-practices.md:7; eslint :54.* — **KEEP**
3. Don't silence the compiler with `!` or `as`; add a check or fix the type. Existing `!` is left until touched.
   *Src: Google TS §non-null, §type assertions.* — **ADOPT, new code only (~243 existing)**
4. A closed set of values is a string-literal union (`'confirm' | 'prompt'`), not a TS `enum`.
   *Src: ours confirm.service.ts:16, 0 enums; Google allows both.* — **ADOPT (decided edge vs CLAUDE.md Java "enums")**

When X use Y: value of unknown shape → `unknown` + narrowing helper (pattern `asyncErrorFrom`, async-state.ts:29-46).

Good (`shared/async-state.ts:8-12`):
```ts
export type AsyncState<T> =
  | { kind: 'idle' }
  | { kind: 'loading'; message?: string }
  | { kind: 'success'; data: T }
  | { kind: 'error'; message: string; traceId?: string; code?: string; retryable?: boolean };
```
Bad (`core/confirm.service.ts:17-18`, and `core/agent.service.ts:29`):
```ts
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  resolve: (value: any) => void;
...
  return this.http.get<ApiResponse<AgentResponse>>(`/api/agents/${id}`).pipe(map((r) => r.data!));
```
Decided edges: `noUncheckedIndexedAccess` **not** proposed now (open Q3). Named exports only / no `namespace` / no `var` / no `@ts-ignore`: 0 violations today → leave to lint (G-F1), no prose rule.
Review checks: new `!`, new `as`, new eslint-disable without reason.

### G-B · Components & signals (Angular 21)

1. Standalone only; never an NgModule. Don't write `standalone: true` — it is the default.
   *Src: best-practices.md:11-12 (21.0.3); CLAUDE.md:248.* — **REWRITE E9 (68 files carry the redundant flag; remove when touched)**
2. Every component sets `changeDetection: ChangeDetectionStrategy.OnPush`. The app is zoneless.
   *Src: best-practices.md:29 (21.0.3); zoneless guide; app.config.ts:11.* — **ADOPT (32/68 today)**
3. Component state is `signal()`; derived state is `computed()`; `effect()` only for side effects (storage, DOM, logging), never to copy state.
   *Src: best-practices.md "State Management"; angular.dev effect guide.* — **ADOPT (512/100/2)**
4. Use `input()`, `output()`, `model()`, `viewChild()` and `host: {}`; never `@Input/@Output/@ViewChild/@HostListener/@HostBinding`.
   *Src: best-practices.md:15,28.* — **ADOPT for new/touched (15+5+3+7 legacy)**
5. A component renders; HTTP and business logic live in a `core/` service. New components stay under 600 lines.
   *Src: style guide "focus on presentation"; eslint :56; addy :322.* — **KEEP E15 as warn + say why**

Good (`shared/icon.component.ts:121-128`):
```ts
export class IconComponent {
  private readonly sanitizer = inject(DomSanitizer);

  name = input.required<string>();
  size = input<number>(16);
  strokeWidth = input<number>(1.75);

  paths = computed(() => this.sanitizer.bypassSecurityTrustHtml(LUCIDE[this.name()] ?? LUCIDE['file']));
}
```
Bad (`shared/select.component.ts:198,205`) — decorator host listeners: `@HostListener('document:click', ['$event'])`, `@HostListener('document:keydown.escape')`.
Decided edges: Angular says prefer Reactive forms on v21 / Signal Forms on v22; ours is 66 files template-driven, 0 reactive → **no forms rule** (open Q1). Angular style guide says `protected` for template-only members and `readonly` on inputs — not proposed (style, 0 risk). Google says no `#private`; 7 uses — not worth a rule.
Review checks: new component without OnPush; new decorator input/output; `effect()` that calls `.set()`.

### G-C · DI, services, async

1. Inject with `inject()` in a field initialiser; never constructor parameters.
   *Src: style guide §DI; best-practices.md:55.* — **CODIFY (233/0)**
2. HTTP lives in a `providedIn: 'root'` service in `core/` returning `Observable<T>` unwrapped from `ApiResponse<T>`; components never inject `HttpClient`.
   *Src: best-practices.md "Services"; ours agent.service.ts:16-26.* — **CODIFY (2 exceptions: auth/forgot-password, auth/reset-password)**
3. A subscription that outlives one HTTP call (router events, interval, SSE) is bound with `takeUntilDestroyed()`.
   *Src: angular.dev rxjs-interop takeUntilDestroyed.* — **ADOPT (0 today; 6 manual ngOnDestroy)**
4. Never swallow an error: the error branch calls `toast.error(...)` or sets an error state. `error: () => {}` needs a one-line reason.
   *Src: CLAUDE.md observability spirit; addy :324.* — **ADOPT (19 in 11 files)**

Good (`core/agent.service.ts:16-26`):
```ts
@Injectable({ providedIn: 'root' })
export class AgentService {
  private readonly http = inject(HttpClient);

  list(workspaceId?: string): Observable<AgentResponse[]> {
    let params = new HttpParams();
    if (workspaceId) params = params.set('workspaceId', workspaceId);
    return this.http
      .get<ApiResponse<AgentResponse[]>>('/api/agents', { params })
      .pipe(map((r) => r.data ?? []));
  }
```
Bad (`features/agents/agent-list.component.ts:1074-1078`):
```ts
    this.toolsApi.list().subscribe({ next: (ts) => this.tools.set(ts), error: () => {} });
    this.agentService.getTemplates().subscribe({
      next: (t) => this.templates.set(t),
      error: () => {},
    });
```
Decided edge: a one-shot `HttpClient` call completes itself; it needs no `takeUntilDestroyed`. `agent-run-gallery.component.ts:517` (`error: () => {}, // non-fatal — recently used is best-effort`) is the accepted form of rule 4.
Review checks: new `.subscribe(` on a non-HTTP stream without `takeUntilDestroyed`; new empty error branch.

### G-D · Templates & accessibility

1. Use `@if / @for (track) / @switch`, `[class.x]` and `[style.x]`; never `*ngIf/*ngFor`, `ngClass/ngStyle`, or `CommonModule`.
   *Src: best-practices.md:35-37,50.* — **CODIFY (0 violations; 3 CommonModule)**
2. Anything clickable is a `<button type="button">` (or `<a>` for navigation), never a clickable `div/span/tr`.
   *Src: best-practices.md:22-23 WCAG AA; addy :180-196; angular-eslint interactive-supports-focus.* — **ADOPT (37 today)**
3. An icon-only button carries `aria-label`; `title` alone is not enough.
   *Src: addy :198-202; angular-eslint templateAccessibility.* — **ADOPT**

Good (`shared/select.component.ts:26-36`) — native control flow + `[class.x]`:
```html
      <button type="button" class="sel-trigger" (click)="toggle()">
        @if (selectedOpt(); as s) {
          @if (s.icon) {
            <span class="sel-icon" [style.color]="s.iconColor || 'var(--ink-2)'">
              <app-icon [name]="s.icon" [size]="14" />
            </span>
          }
          <span class="sel-label">{{ s.label }}</span>
        } @else {
          <span class="sel-placeholder">{{ placeholder() }}</span>
        }
```
Bad (`shared/select.component.ts:44,49`) — clickable `div`, no keyboard path:
```html
          <div class="sel-item sel-item-clear" (click)="pick('')">
            <div class="sel-item" [class.sel-item-active]="opt.value === value()" (click)="pick(opt.value)">
```
Review checks: new `(click)` on a non-interactive element; new icon-only button without `aria-label`.

### G-E · Icons & select (ours — authentic baseline)

1. Icons are `<app-icon name>` from the `LUCIDE` map; never emoji/unicode symbols, `<mat-icon>`, FontAwesome or an icon package. New icons go into `LUCIDE`.
   *Src: rules/angular-ui.md:8; ref :40-44.* — **KEEP + tighten ("unicode symbols"; 83 violations)**
2. A dropdown whose options show icons is `<app-select>`; a text-only dropdown stays a native `<select>`.
   *Src: rules :9; ref :49-83.* — **KEEP**
3. Colour an icon with `[style.color]` on its parent; `app-icon` has no `stroke` input.
   *Src: rules :10; icon.component.ts:104 (`stroke="currentColor"`).* — **KEEP (merge E3)**

Good (`features/tools/tool-list.component.ts:236-243`; would also need `aria-label`, G-D3):
```html
                      <button
                        class="btn btn-ghost btn-sm btn-icon"
                        title="Delete group"
                        style="color:var(--danger);"
                        (click)="deleteGroup(g)"
                      >
                        <app-icon name="trash" [size]="14" />
                      </button>
```
Bad (`features/settings/settings.component.ts:655-662`):
```html
                      <button
                        class="btn btn-ghost btn-sm btn-icon"
                        style="color:var(--danger)"
                        (click)="revokeKey(k)"
                        [disabled]="k.revoked"
                      >
                        🗑
                      </button>
```
Decided edges: `agent-icon.component.ts` (Heroicons, agent-card picker) is exempt — do not unify. A sweep of the 83 existing symbols is a separate `/crq` change; fix the template you are already editing.
Review checks: any non-ASCII symbol in a template; new icon name not in `LUCIDE` (today it silently renders `file`, icon.component.ts:128 — open Q4).

### G-F · Lint configuration (rules about `eslint.config.js`, not about code)

1. Extend `tseslint.configs.recommended`, angular `tsRecommended`, `templateRecommended` and `templateAccessibility`, with the inline-template processor so the 68 inline templates are linted.
   *Src: angular-eslint CONFIGURING_ESLINT.md:50-114; typescript-eslint configs page.* — **ADOPT (resolves E17, E18)**
2. The header comment lists only rules the config actually enforces.
   *Src: GitLab #147.* — **REWRITE E12**
3. `features/X` never imports `features/Y`: one zone per feature generated from the directory list, not four hand-written targets.
   *Src: eslint :62-100; 0 violations today.* — **REWRITE E16**
4. A newly enabled rule lands at `error` with existing hits fixed, or at `warn` with the count written in its comment.
   *Src: ours E15 precedent; CLAUDE.md "a failing signal that means nothing".* — **ADOPT**

Decided edges: `strict` / `strict-type-checked` not proposed — typescript-eslint says *not semver-stable* and meant for teams "highly proficient in TypeScript". `stylistic` optional; Prettier already owns formatting (`.prettierrc.json`). `prefer-on-push-component-change-detection` is **not** in angular-eslint 21's recommended set — G-B2 needs it added explicitly.
Review checks: `make lint` green; no new `eslint-disable` without a reason.

**Total: 23 rules in 6 groups** (A4 · B5 · C4 · D3 · E3 · F4).

Considered, not proposed: `protected` for template members, `readonly` inputs (style guide — style only) · Reactive/Signal forms (Q1) · `NgOptimizedImage` (0 `<img>` that need it) · lazy routes (35/35 feature routes already; lint can't express it cheaply) · `noUncheckedIndexedAccess` (Q3) · awesome-cursorrules rules (Angular 18, persona prose).

---

## 6 · Open questions

1. **Forms.** Angular 21 says Reactive forms; v22 says Signal Forms. We are 66 files template-driven, 0 reactive. Recommend: no forms rule until the v22 upgrade, then Signal Forms for new forms.
2. **Template a11y lint fallout.** Turning on `templateAccessibility` (G-F1) will flag ~37 clickable non-buttons. Recommend: `click-events-have-key-events` and `interactive-supports-focus` at `warn` with the count (G-F4); rest at `error`.
3. **`noUncheckedIndexedAccess`.** Not in `strict`, not in Angular CLI defaults; would catch `LUCIDE[name]`-style lookups. Recommend: measure the error count first; don't adopt blind.
4. **Typed icon names.** `name = input.required<string>()` lets a typo render `file` silently. Typing it as `keyof typeof LUCIDE` makes `strictTemplates` catch it at build. Recommend: yes, but it's a code change → its own `/crq`.
5. **Emoji sweep.** 83 symbols in 7 files break G-E1. Recommend: one `/crq` chore; the rule applies to new code from approval.
6. **`standalone: true` removal.** 68 files. Recommend: remove only when the file is touched; no sweep.
7. **Where E11 (real API, E2E reachable) lives.** It's a Definition-of-Done check, not a coding standard. Recommend: move to `/dod`.
