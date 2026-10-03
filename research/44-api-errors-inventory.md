# 44 — API contract + error handling + error-code catalogue: inventory

For grilling **chiyanram/skills#58** — API contract, error handling, one `ErrorCode` per real scenario.
Read-only research. agent-platform `origin/master` @ **`291a308e`** (`291a308eeb98aa5cd7f66f3dabd813ea8e2d5239`).
Every `path:line` below is at that SHA unless marked otherwise. Fetched / reference text is quoted as data.

---

## 0. Headline

```
  CLAUDE.md:260 says        errors are ProblemDetail (RFC 9457)
  the code says             errors are ApiResponse{success:false, code, message, traceId}
  ProblemDetail in prod     0 uses  (two comments claim it: ModelRoleController.java:73, AbstractIT.java:67)
  already recorded          docs/adr/0008-apiresponse-envelope-problemdetail.md:32  "DRIFT — doc contradicts code"
                            docs/spec/REQ-500-login-throttle-progressive-delay.md:603-611 (deferred to "its own issue")
```

Error responses reach the wire through **five** different paths, only one of which uses `ErrorCode`:

```
 throw AruviiException(ErrorCode)  ──► GlobalExceptionHandler.handleAruvii ──► ApiResponse{code=kebab slug}   ✔ catalogue
 controller-local @ExceptionHandler ──► ApiResponse.error(ex.getMessage())  ──► code=null                     ✘ 40 handlers / 15 files
 ResponseEntity.status(..).body(ApiResponse.error(e.getMessage()))          ──► code=null                     ✘ 32+15 sites
 throw ResponseStatusException(...)  ──► GEH.handleResponseStatus           ──► code="404" (status as string) ✘ 35 sites / 8 files
 filter chain (401 entry point, URL-level 403, RateLimitFilter)             ──► empty body / Boot /error JSON  ✘ outside MVC advice
```

---

## 1. Our code as it is

### 1.1 `ErrorCode` — `aruvii-shared/src/main/java/ai/aruvii/shared/error/ErrorCode.java`

Shape (`:120-140`): `code` (kebab slug), `defaultMessage`, `httpStatus` (int, Spring-free), `retryable`, `severity` (INFO/WARN/ERROR → log level).
Javadoc claim (`:18-20`): *"A grep over this file reveals every error path"* — **false**, see §1.5.

**65 constants.** `main` = references in `src/main` outside the enum (name match; a few names collide with
`ToolErrorCode`, so treat as approximate). `0` = no production path produces it.

| constant | status | main | thrown from (examples) |
|---|---|---|---|
| WORKSPACE_NOT_FOUND | 404 | 1 | WorkspaceService |
| WORKSPACE_FORBIDDEN | 403 | 1 | (javadoc example only in AruviiException) |
| **WORKSPACE_SLUG_TAKEN** | 409 | **0** | — (WorkspaceController returns raw 409 instead) |
| AUTH_REQUIRED | 401 | 2 | GEH only |
| **AUTH_INVALID_TOKEN** | 401 | **0** | — |
| AUTH_FORBIDDEN | 403 | 12 | ApiKeyScopeInterceptor, ApiKeyService, PromptBuilderController, GEH |
| TOOL_NOT_FOUND | 404 | 2 | LookupResult (ToolController uses its own ToolNotFoundException → code=null) |
| **TOOL_FORBIDDEN** | 403 | **0** | — |
| TOOL_INVALID_CONFIG | 400 | 3 | ToolService, RagIngestionService |
| **TOOL_EXECUTION_FAILED** | 502 | **0** | — (tool failures use `ToolErrorCode`, a separate 68-value enum) |
| **TOOL_TIMEOUT** | 504 | **0** | — |
| **TOOL_APPROVAL_REQUIRED** | **202** | **0** | — (a 2xx in an error catalogue) |
| AGENT_NOT_FOUND | 404 | 7 | ExplanationService, InteractionsController, RefusalReason, SessionNotFoundException |
| **AGENT_FORBIDDEN** | 403 | **0** | — |
| **AGENT_INVALID_STATE** | 409 | **0** | — |
| AGENT_NOT_VERIFIED | 409 | 1 | RefusalReason |
| **CERTIFICATION_VERDICT_REQUIRED** | 409 | **0** | — |
| **AGENT_VERSION_INCOMPLETE / _ALREADY_PROD / _NEVER_PROMOTED / _ALREADY_CERTIFIED / _NOT_FOUND** | 409/409/409/409/404 | **0 each** | — (5 codes; slug not in UI either) |
| AGENT_VERSION_UNAVAILABLE | 409 | 1 | RefusalReason |
| EVAL_QUEUE_UNAVAILABLE | 503 | 1 | AgentEvalController |
| PROVIDER_NOT_FOUND | 404 | 20 | ProviderController, ChatOrchestrator, PromptBuilderTestHandler |
| PROVIDER_UNAVAILABLE | 502 | 5 | ChatOrchestrator, PromptBuilderTestHandler, RefusalReason |
| **PROVIDER_INVALID_KEY** | **401** | **0** | — (if ever thrown, the UI 401 interceptor would log the user out: `auth.interceptor.ts:30`) |
| MODEL_NOT_FOUND | 404 | 1 | SessionModelController |
| PROVIDER_NAME_TAKEN / _IN_USE | 409 | 1 / 1 | ProviderController |
| PROVIDER_TRUST_NOT_NEEDED, _CERT_MOVED, _FALLBACK_{SELF,MISSING,ARCHIVED,CHAINED}, _TYPE_UNREADABLE, _NOT_PINNED | 409 / 422 | 1 each | ProviderPrecondition (outcome → code mapping; the good pattern) |
| RATE_LIMIT_EXCEEDED | 429 | 3 | RateLimitFilter |
| BUDGET_EXCEEDED | 429 | 5 | ChatOrchestrator, ChatResponseEvent, RefusalReason |
| SESSION_ARCHIVED / SESSION_LIMIT_EXCEEDED | 409 / 429 | 1 / 1 | SessionMessageController |
| BAD_REQUEST | 400 | 41 | GEH (×5 mappings) + many controllers |
| VALIDATION_FAILED | 400 | 12 | GEH, ApiKeyService, AuditLogAccess |
| **DOCUMENT_NOT_FOUND** | 404 | **0** | — |
| PII_REDACTION_FAILED | 422 | 1 | ChatResponseEvent |
| RAG_INGEST_BLOCKED | 422 | 2 | RagIngestionService |
| RAG_TOP_K_INVALID / RAG_COLLECTION_INVALID | 400 | 1 / 1 | RagConfigField |
| DB_CONNECTION_NOT_FOUND / _NAME_TAKEN / _TEST_FAILED | 404/409/502 | 4/1/2 | DbConnectionService |
| **DB_CONNECTION_IN_USE / DB_CREDENTIAL_DECRYPT_FAILED / DB_DESCRIPTOR_MISMATCH** | 409/500/502 | **0 each** | — |
| INJECTION_DETECTED | 422 | 1 | RefusalReason |
| NOTIFICATION_* (4) | 404/400/400/400 | 1–2 | NotificationConfigController / Service |
| AGENT_PAUSED / MAX_STEPS / GUARDRAIL_BLOCKED | 409/422/**400** | 2/6/1 | RefusalReason, ChatOrchestrator (SSE only — `ErrorCode.java:107-111`) |
| **PROVIDER_TRUST_UNUSABLE** | 502 | **0** | — |
| INTERNAL_ERROR | 500 | 14 | GEH catch-all, ChatOrchestrator, FailureKind |

**20 of 65 codes (31%) are produced by no production path.** Tests: `ErrorCodeTest` checks kebab case,
sentence case, status range, uniqueness, severity set (`aruvii-shared/src/test/.../ErrorCodeTest.java:16-56`) —
nothing checks that a code is thrown, nor that its status is right for its scenario.

Separate catalogue: `ToolErrorCode` (`aruvii-shared/src/main/java/ai/aruvii/shared/tool/ToolErrorCode.java:12-80`)
— 67 values + `UNKNOWN`, UPPER_SNAKE, no status, carried in tool results / traces (ADR-0019), not HTTP.

### 1.2 `AruviiException` — `aruvii-shared/src/main/java/ai/aruvii/shared/error/AruviiException.java:19-52`

`RuntimeException` carrying `ErrorCode` + optional `detail` (goes to log only, `getMessage()` = `code: detail`)
+ optional `userMessage` override via `userFacing(...)` (`:43`). 68 `new AruviiException` / `userFacing` sites in `src/main`.
Only **1** class `extends AruviiException`; **28** custom exceptions extend `RuntimeException`/`IllegalState`/`IllegalArgument`
directly and are mapped by hand, controller by controller.

### 1.3 Global handler — `aruvii-api/src/main/java/ai/aruvii/api/controller/GlobalExceptionHandler.java`

The only `@RestControllerAdvice` on master. Returns `ApiResponse`, never `ProblemDetail`; does **not** extend `ResponseEntityExceptionHandler`.

| exception | status | `code` on wire | message on wire | line |
|---|---|---|---|---|
| LicenseLimitException | 402 | `LICENSE_LIMIT_EXCEEDED` (UPPER, not in catalogue) | `ex.getMessage()` | :58-64 |
| AruviiException | `ec.httpStatus()` | kebab slug | `userMessage()` | :66-73 |
| AccessDenied / AuthorizationDenied | 403 | `auth-forbidden` | default | :75-84 |
| AuthenticationException | 401 | `auth-required` | default | :86-95 (rarely reached — filter chain answers first) |
| MethodArgumentNotValidException | 400 | `validation-failed` | **first** field error only, `field: msg` | :97-107 |
| MissingServletRequestParameter | 400 | `bad-request` | fixed text + param name | :109-116 |
| MethodArgumentTypeMismatch | 400 | `bad-request` | fixed text + param name | :118-125 |
| HttpMessageNotReadable | 400 | `bad-request` | fixed | :127-134 |
| **IllegalArgumentException** | 400 | `bad-request` | **`ex.getMessage()`** — any JDK/library IAE text (e.g. `UUID.fromString`, `Enum.valueOf` → FQCN) | :136-143 |
| ResponseStatusException | its status | **`"404"`, `"409"`…** (status as string) | `getReason()` | :145-156 |
| ConstraintViolationException | 400 | `validation-failed` | first violation | :158-168 |
| jakarta EntityNotFoundException | 404 | **`NOT_FOUND`** (UPPER, not in catalogue) | `ex.getMessage()` | :170-177 |
| Exception | 500 | `internal-error` | default (safe) | :179-190 |

Also: `ResponseBodyAdvice` stamps `traceId` + `X-Trace-Id` on every `ApiResponse` (`:202-217`); falls back to a random
16-hex id when no span (`:227`). Severity → log level for AruviiException (`:192-198`).

`code` on the wire therefore has **four** formats: kebab slug, UPPER_SNAKE, numeric string, or null.

### 1.4 `ApiResponse<T>` — `aruvii-shared/src/main/java/ai/aruvii/shared/domain/ApiResponse.java:21-29`

`(success, data, message, code, actionable, traceId, timestamp)`. Used for **both** success and error (ADR-0008).
`error(String message)` (`:48`) — a factory with **no code** — is the most-called error factory.
`ErrorCode.retryable` is **never serialised**; the UI re-derives retryable from status (`aruvii-ui/src/app/shared/async-state.ts:40`).
`Actionable` is set in 2 production files only.

### 1.5 Violations (counts at `291a308e`, `src/main/**/*.java`)

| pattern | count | where |
|---|---|---|
| controller-local `@ExceptionHandler` | **40 handlers / 15 files** (#640 says 13 controllers) | AgentController:162-190, ToolController:117-170, ToolApprovalController:99-114, … |
| `ApiResponse.error(...)` outside GEH | **65 sites / 24 files**; **64 of them pass no code** | UserController ×7, WorkspaceController ×6, ToolController ×6, AuthController ×4, SetupController ×3 … |
| exception text echoed to client (`getMessage()` into response) | **58 sites** | list in §1.5a |
| driver text to client | **1** — `AgentController.java:186-190` `"Invalid reference: " + getMostSpecificCause().getMessage()` (#640) | ToolController:146-151 does it right: logs cause, returns fixed text |
| `ResponseEntity.status(...)` | **32 / 11 files**; + **15** `ResponseEntity.badRequest()/notFound()` | AuthController:59,73,93; UserController:57-134; WorkspaceController:57-131 |
| `new ResponseStatusException` | **35 / 8 files**, incl. **service layer** `aruvii-tools/.../ToolGroupService.java:44-87` (HTTP type in `application/`) | OpenApiImportController ×7, ToolGroupService ×7, WebhookRetryService ×6 |
| `spring.web.error.include-message: always` + `include-binding-errors: always` | `aruvii-api/src/main/resources/application.yml:68-70` | Boot `/error` page echoes exception messages for anything outside MVC advice |
| 401 from filter chain = **empty body** | `aruvii-api/src/main/java/ai/aruvii/api/config/SecurityConfig.java:62` `HttpStatusEntryPoint(UNAUTHORIZED)` | no code, no traceId |
| stale count in rulebook | `.agents/skills/code/references/errors.md` (branch `chore/643-one-rulebook-skeleton`) §2 says "Thirty-five entries" — master has 65 | |

**1.5a** — echo sites: AgentController:165,171,177,183 · AgentEvalController:120,126,132 · AgentTriggerController:121,127 ·
AuthController:59,93 · DbPoolController:38 · GEH:63 · McpServerController:79,85 · OpenApiImportController:62,88,107,109 ·
PasswordResetController:36 · PipelineController:104,110 · PromptBuilderController:210,216,222 · RagDocumentController:357 ·
SessionMessageController:298 · ToolApprovalController:102,108,114 · ToolController:120,126,157,163,169 ·
ToolExecuteController:47,53 · ToolTestCaseController:102,108,114 · TrustedCertificateController:82,88,94 ·
UserController:57,70,81,83,130,132,134 · WorkspaceController:57,69,81,118,131 · WorkspaceTrustedCertificateController:127,133,139.
Most are domain exceptions with authored text (low risk); the ones catching `IllegalArgumentException` / `IllegalStateException`
/ `NoSuchElementException` echo whatever any library threw.

**Same scenario, different status:**

| scenario | answers | where |
|---|---|---|
| `IllegalArgumentException` | 400 everywhere, **404** in ToolApprovalController | ToolApprovalController.java:99-100 |
| `IllegalStateException` | **409** (AgentTrigger:124, ToolApproval:105) vs **502** (McpServer:82) | |
| `DataIntegrityViolationException` | **400** in AgentController:186 vs **409** in ToolController:146 | ToolController javadoc :141-144 notes it deliberately |
| content blocked by guardrail | `GUARDRAIL_BLOCKED` **400** vs `INJECTION_DETECTED` / `RAG_INGEST_BLOCKED` **422** | ErrorCode.java:98,85,114 |
| feature disabled | `FeatureDisabledException` → **400** | ToolController.java:160 |
| login throttle vs chat rate limit | both 429 + `Retry-After`; throttle has **no code** (AuthController:73-76), rate limit has `rate-limit-exceeded` (RateLimitFilter:111-117) | |
| not found | `tool-not-found` slug, or `null` code (ToolNotFoundException), or `"404"` (ToolGroupService RSE), or `NOT_FOUND` (EntityNotFound) | |

### 1.6 Pagination, versioning, validation, idempotency

- **Pagination:** 0 controllers take `Pageable`; **44** endpoints return `ApiResponse<List<…>>` unbounded. Four bespoke page records with **three** field schemes:
  `FeedbackPage(items,total,page,size)` (AgentFeedbackController.java:41) · `InteractionsPage(items,total,page,size)` (shared/llm/InteractionPort.java:50) ·
  `ErasureLogPage(content,total,page,…)` (DataErasureController.java:134) · `AuditLogPage(content,totalElements,pageNumber,pageSize)` (shared/audit/AuditLogPort.java:39). No cursor anywhere.
- **Versioning:** none — base `/api`, no `/v1`, no version header (only `/v1` hits are outbound provider URLs).
- **Validation:** 40 `@Valid`/`@Validated` params in api controllers; errors surface as **first field only**, flattened into `message` (GEH:101-106) — no per-field list.
- **Idempotency:** no `Idempotency-Key` on any endpoint; only internal tool-call idempotency (ToolService.java:587,675).
- **Optimistic lock:** 0 `@Version` fields, 0 `OptimisticLock*` handling, 0 ETag/If-Match. Concurrent edits are last-write-wins, silently.

### 1.7 UI — how `aruvii-ui` reads errors

- `asyncErrorFrom` (`aruvii-ui/src/app/shared/async-state.ts:30-48`) reads `error.message`, `traceId`, `code`; retryable = `status>=500 || 429`.
- ~90 reads of `error.message` vs **2** of `error.code`; the only code-driven branch is `TOP_K_REFUSED = 'rag-top-k-invalid'` (`features/tools/tool-detail.component.ts:33,1657`).
- Status-driven branches: 401→refresh/logout and 403 (`core/auth.interceptor.ts:30,48`), 409 (`openapi-import.component.ts:1053`, `workspace-list.component.ts:499`), 429 (`settings.component.ts:1380`), 403 (erasure-log, settings).
- So today the UI's real contract is **status + message**, not `code`. Renaming a slug breaks one screen; changing message text breaks none programmatically but is what users see.

---

## 2. Scenarios by domain — what master returns today

| domain | scenario | status | body `code` | source |
|---|---|---|---|---|
| auth | no/invalid JWT on protected route | 401 | **empty body** | SecurityConfig.java:62 |
| auth | bad login credentials | 401 | null, `AuthException` text | AuthController.java:58-59 |
| auth | login throttled | 429 + `Retry-After` | null | AuthController.java:72-76 (REQ-500) |
| auth | refresh missing / invalid | 401 | null ("No refresh token") | AuthController.java:84-93 |
| RBAC | `@PreAuthorize` denial | 403 | `auth-forbidden` | GEH:75-84 |
| RBAC | URL-level denial (`/actuator/loggers`) | 403 | Boot `/error` JSON, not ApiResponse | SecurityConfig.java:79-80 (default AccessDeniedHandler) |
| RBAC | API-key scope | 403 | `auth-forbidden` | ApiKeyScopeInterceptor |
| validation | `@Valid` body | 400 | `validation-failed`, first field only | GEH:97-107 |
| validation | bad query/path param | 400 | `bad-request` / `validation-failed` | GEH:109-125,158-168 |
| not found | agent / tool / pipeline / prompt | 404 | **null** (local handlers) | AgentController:162, ToolController:117, PipelineController:101 |
| not found | provider / model / db connection | 404 | slug | ProviderController, DbConnectionService |
| conflict | name taken (agent, tool, user, workspace) | 409 | **null** | AgentController:168, ToolController:123, UserController:70, WorkspaceController:57 |
| conflict | name taken (provider, db connection) | 409 | slug | ProviderController, DbConnectionService |
| conflict | concurrent edit | — | **no detection** | §1.6 |
| rate limit | chat messages | 429 + `Retry-After` | `rate-limit-exceeded` | RateLimitFilter.java:111-117 |
| rate limit | token budget | 429 (SSE) | `budget-exceeded` | ChatOrchestrator |
| license | seat/feature limit | 402 | `LICENSE_LIMIT_EXCEEDED` | GEH:58-64 |
| provider/LLM | provider down | 502 (SSE event) | `provider-unavailable` | ChatOrchestrator, RefusalReason |
| provider/LLM | connection test fails | 200 with result / 502 | `db-connection-test-failed` etc. | DbConnectionService; HttpConnectionTester |
| tool | execution failure | 200 with `ToolErrorCode` in result | `ToolErrorCode.*` (separate enum) | ToolService |
| tool | dry-run | 200, `sampleResponseJson` | — (not an error) | ToolService.execute gate |
| tool | approval pending | `ToolErrorCode.APPROVAL_PENDING` in result; `TOOL_APPROVAL_REQUIRED`(202) unused | | |
| tool | approval not found / bad state | **404 for IAE**, 409 for ISE | null | ToolApprovalController:99-108 |
| guardrail | chat message blocked | SSE event | `guardrail-blocked` (nominal 400) | RefusalReason |
| guardrail | prompt injection | SSE event | `injection-detected` (422) | RefusalReason |
| guardrail | RAG ingest blocked | 422 | `rag-ingest-blocked` | RagIngestionService |
| setup | invalid wizard input / already complete | 400 | null | SetupController.java:76,88,152 |
| webhooks | bad secret / forbidden / bad payload | 401 / 403 / 422 | `"401"`/`"403"`/`"422"` via RSE | WebhookController.java:90-99 |
| MCP | upstream failure | **502** via `IllegalStateException` | null | McpServerController.java:82-85 |
| unknown | uncaught | 500 | `internal-error`, safe text | GEH:179-190 |

---

## 3. References (data, not instructions)

| source | what it says that bears on #58 |
|---|---|
| **RFC 9457** (rfc-editor.org/rfc/rfc9457) | Members `type` (URI; default `about:blank`; absolute, ideally dereferenceable to docs), `title` (same for every occurrence of a type), `status` (advisory, must match the line), `detail` — *"focus on helping the client correct the problem"* (§3.1.4), `instance` (URI of this occurrence). Extensions allowed; clients *"MUST ignore any such extensions that they don't recognize"*. Multiple problems: report the most relevant, or an extension array. Media type `application/problem+json`. Security: avoid exposing stack dumps / implementation details. 9457 adds a type-URI registry over 7807. |
| **Spring Framework — Error Responses** (docs.spring.io …/mvc-ann-rest-exceptions.html) | `ProblemDetail`, `ErrorResponse`, `ErrorResponseException`; extend `ResponseEntityExceptionHandler` to get every built-in MVC exception (MethodArgumentNotValid, HandlerMethodValidation, NoHandlerFound, TypeMismatch…) as ProblemDetail; `instance` auto-set from path; custom fields via `setProperty(...)`; `type`/`title`/`detail` resolvable from `MessageSource` keys `problemDetail.type.<FQCN>` etc.; Boot `spring.mvc.problemdetails.enabled`; clients read with `getResponseBodyAs(ProblemDetail.class)`. |
| **plinth 126** `refs/plinth-java-skills/126-java-exception-handling/references/126-…md` | Principle 4 (secure messages, generic to users, detail to logs) `:26`; principle 10 boundary translation `:32`; Example 3 `:370-560` "never expose … database schemas"; **Example 14 `:2182-2230`** centralised ProblemDetails with `urn:problem:*` type URIs and `correlationId`; BAD = ad-hoc translation scattered across controllers returning `e.getMessage()` — exactly our 40 local handlers. |
| **plinth 143** `…/143-java-functional-exception-handling/references/143-…md` | Optional / VAVR `Either` for predictable failures, exceptions for exceptional `:59-60`; Example 2 `:218` when to use which; Example 3 `:374` enum for simple errors, sealed+records for rich ones. (Our errors.md §7 already rejects VAVR; sealed outcomes are our equivalent.) |
| **Jeffallan api-designer** `refs/Jeffallan-claude-skills/skills/api-designer/` | SKILL.md MUST: RFC 7807 errors, paginate **all** collections, version with deprecation policy, "Return inconsistent response structures" is a MUST NOT. error-handling.md: category→status table (400/401/403/404/409/422/429+Retry-After/500/503+Retry-After) `:71-285`, "Never expose: stack traces, database errors" `:259`, error-code catalogue with status per code `:287`, field-level validation arrays `:343`, request-id `:399`, retryable vs non-retryable lists `:479-495`. versioning.md `:136` recommends URI versioning. pagination.md: offset / page / cursor / keyset trade-offs. |
| **addyosmani api-and-interface-design** `refs/addyosmani-agent-skills/skills/api-and-interface-design/SKILL.md` | Hyrum's Law `:22-31` (error text becomes contract); One-Version Rule `:33-35`; "Consistent Error Semantics … Don't mix patterns" `:61-86`; Idempotency-Key must be honoured not just accepted `:158-199`; paginate list endpoints `:232`; anti-pattern "Inconsistent error formats across endpoints" `:341`. |
| **ultrapowers api-design** (installed, plugins/synced/…/skills/api-design/SKILL.md) | one error schema everywhere; always a machine-readable code; cursor default for growing lists; URL-path versioning default, "No versioning — best if you control all clients"; 429 + `Retry-After`, `X-RateLimit-*` headers. |
| **ultrapowers error-handling** (…/skills/error-handling/SKILL.md) | layer table: boundary returns structured errors, service uses typed errors/results, infra wraps with context; "if the caller should handle it, use a result type"; translate at boundaries; log at handling not throwing; "Error messages exposing internals → map to safe messages at the API layer". |
| **jvm-skills** | No ProblemDetail-specific content found (only candidate lists); not used. |

---

## 4. Gap table — ours vs references

| concern | ours @ `291a308e` | references | gap |
|---|---|---|---|
| error body format | `ApiResponse{success:false,…}` | RFC 9457 `application/problem+json` (RFC, Spring, plinth 126 Ex14, Jeffallan) | not standard; CLAUDE.md:260 claims otherwise (ADR-0008 drift) |
| one error shape | 5 paths, `code` in 4 formats or null | "one error schema everywhere" (ultrapowers, addy, Jeffallan MUST NOT) | **large** |
| central translation | 1 advice + 40 local handlers + 47 inline `ResponseEntity` + 35 RSE | centralised mapper (plinth 126 Ex14, ultrapowers) | **large** |
| `type` URI | none | URI per problem type, docs if dereferenceable (RFC 3.1.1) | missing |
| `instance` | none (traceId instead) | URI of occurrence (RFC 3.1.5); Spring auto-fills path | missing; traceId is our de-facto instance |
| no leak | 58 echo sites, 1 driver leak (#640), GEH IAE echo, `include-message: always` | never expose DB/stack (RFC §5, Jeffallan :259, plinth 126 Ex3) | **real** |
| catalogue | 65 codes, 20 never thrown, statuses not tested per scenario | catalogue with status per code (Jeffallan :287) | dead entries; no "test that proves it" |
| retryable | in enum, not on wire | retryable list / Retry-After (Jeffallan :479, ultrapowers) | not exposed |
| validation errors | first field only, in `message` | per-field array (Jeffallan :343, ultrapowers "accumulate errors"), Spring HandlerMethodValidation | missing |
| filter-chain errors | empty 401, Boot `/error` 403 | same shape as every other error | inconsistent |
| pagination | 44 unbounded lists, 4 ad-hoc page records, 3 field schemes | paginate all collections; cursor for growing data (Jeffallan, addy, ultrapowers) | **large** |
| versioning | none, `/api` | URI `/v1` (Jeffallan, ultrapowers) — or none if you control all clients (ultrapowers) | decision needed; self-hosted customers call the API |
| idempotency | none | Idempotency-Key honoured (addy) | missing; low priority |
| optimistic lock | none | 409/412 on version mismatch (Jeffallan conflict, addy 409 "version mismatch") | missing |
| exception vs outcome | errors.md §1 already: sealed outcome vs AruviiException; ProviderPrecondition models it | ultrapowers, plinth 143 | aligned — keep |
| service-layer HTTP types | `ResponseStatusException` in ToolGroupService / WebhookRetryService | translate at boundary only | layering breach |

---

## 5. Decisions for the operator

**D1 — Error wire format.**
| option | what changes | backed by |
|---|---|---|
| A. Adopt RFC 9457 `ProblemDetail` for errors, keep `ApiResponse` for success; carry `code`, `traceId`, `retryable` as extension members | GEH extends `ResponseEntityExceptionHandler`; UI `asyncErrorFrom` reads `detail`/`code`; every IT asserting `$.message` changes | RFC 9457, Spring docs, plinth 126 Ex14, Jeffallan |
| B. Keep `ApiResponse` envelope for errors; fix CLAUDE.md:260 to say so (finalise ADR-0008) | doc change only; enforce shape | ADR-0008, addy (consistency over standard), ultrapowers custom `{error:{code}}` |
| C. Both: `ApiResponse` envelope whose error branch embeds RFC 9457 members | additive, no UI break | — (hybrid; no reference does this) |
Recommendation: **A** — 9457 is what CLAUDE.md already promises and Spring gives the built-in exceptions free; UI touch is one function (`async-state.ts:30-48`) plus ~90 `.message` reads.

**D2 — One translation point.**
| option | backed by |
|---|---|
| A. Only `GlobalExceptionHandler` maps exceptions; delete 40 local handlers; ban `ResponseEntity.status` / `ApiResponse.error` / `ResponseStatusException` in controllers and services (ArchUnit) | plinth 126 Ex14, ultrapowers "translate at boundaries" |
| B. Allow local handlers but they must use `ErrorCode` | — |
Recommendation: **A**, with an ArchUnit gate (no gate exists today; semgrep deleted).

**D3 — Catalogue scope and proof.**
| option | backed by |
|---|---|
| A. One `ErrorCode` per real scenario; delete the 20 dead codes; every code has a test proving status + code (parameterised IT) | issue #58 Q3, Jeffallan :287 |
| B. Keep dead codes as "reserved" | — |
Sub-decisions: kebab slug vs UPPER_SNAKE (`ToolErrorCode` is UPPER; slug is what UI reads); `type` = `urn:aruvii:problem:<slug>` vs `https://docs…/errors/<slug>` (RFC prefers dereferenceable); fold `ToolErrorCode` in or keep separate (separate: different channel, ADR-0019).
Recommendation: **A**, `type` as a non-dereferenceable URN (self-hosted, no public docs host) — RFC permits it.

**D4 — Status rules for the ambiguous cases.**
| case | today | options |
|---|---|---|
| guardrail / injection block | 400 vs 422 | 422 for all (content understood, refused) · 400 for all |
| integrity / name taken | 400 vs 409 | 409 always (Jeffallan conflict) |
| upstream provider/MCP/DB failure | 502 / ISE→502 | 502 bad gateway · 503 + Retry-After when transient |
| token budget | 429 | 429 (Jeffallan, retry later) · 403 (policy, not rate) |
| approval required | `TOOL_APPROVAL_REQUIRED` 202 in error catalogue | move out of the catalogue (202 is a success outcome) |
| provider rejected key | 401 | **not 401** — collides with the UI logout interceptor; 502 or 422 |
Recommendation: 422 for content blocks, 409 for conflicts, 502 upstream, 429 budget, 202 out of catalogue, provider-key → 502.

**D5 — Contract scope for v1 (pagination / versioning / optimistic lock / validation detail).**
| option | backed by |
|---|---|
| A. Minimum: one page record (`items,total,page,size`) for the 4 existing paged endpoints; per-field `errors[]` extension for validation; no `/v1` (single-version, customer runs the UI that ships with the API) | ultrapowers "no versioning if you control all clients", addy One-Version Rule |
| B. Full: paginate all 44 list endpoints, `/api/v1`, `@Version` + 409 on conflict, Idempotency-Key on creates | Jeffallan MUSTs, addy idempotency |
| C. A now, B items as separate tickets | — |
Recommendation: **C** — #58 owns the rule and catalogue; mass endpoint changes are their own tickets.

---

*Not verified:* the URL-level 403 body shape (inferred from Spring Security defaults, not observed at runtime); per-code `main`
counts are name matches and may include `ToolErrorCode` collisions (`DB_CONNECTION_NOT_FOUND`, `MAX_STEPS`-like names).
