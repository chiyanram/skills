# 56c — G9b Good/Bad pairs · batch GB5 · API and security (#33, map #9)

Rules: AP3a AP4a TT2 SE1 SE4 SE5 SS13 SS21 (operator-approved, `54-g9b-good-bad-selection.md` §3).
Governed by `55-good-bad-v3-BRIEF.md` (GB2): **Bad = our real code**; **Good = that same Bad rewritten** to obey its
rule, every rule in `19-approved-rules.md` and house style. Our code is never a Good as-is. Where our code has no Bad,
both sides are `adapted from <source:line>` (a source opened in this session).

- Bads: agent-platform `origin/master` @ **`772736bf`** (2026-10-03), read with `git show` / `git grep`. Module
  prefixes dropped where the file name is unique.
- Every Good is **NEEDS COMPILE CHECK** until work item 1 compiles it.
- House style (`31-good-bad-v2-BRIEF.md`): Spock specs, `def "should …"()` (U2a), labelled `given:/when:/then:/where:`,
  ST1 (`final` on every Java local; `def` in Groovy), ST2, NM1, ER2, ER10, LG3, U4.
- Seams follow SEAM1 (ADR-0017 S-1..S-7) and avoid the Fowler baseline
  (`rameezk/skills skills/code-review/martin-fowler-code-smells.md`, fetched 2026-10-03).

---

### AP3a — A role rule is proven by a caller × endpoint matrix IT

**Bad** (ours)
```java
@Test
@DisplayName("PATCH /api/tools/{id} updates name and description")
void updateTool_changesNameAndDesc() throws Exception {
    var req = new CreateToolRequest(/* … */);
    final var createdBody = http.post().uri("/api/tools")
            .header(HttpHeaders.AUTHORIZATION, adminToken) /* … */;
    final String id = JsonPath.read(/* … */, "$.data.id");
    http.patch().uri("/api/tools/" + id)
            .header(HttpHeaders.AUTHORIZATION, adminToken)
            .contentType(MediaType.APPLICATION_JSON)
            .body("""{ "name": "Updated Name", … }""")
            .exchange()
            .expectStatus().isOk();
}
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/ToolControllerIT.java:328-354` @ `772736bf` (`adminToken`
set once at `:49-53`) — `ToolController.java:69-70` gates PATCH by role, yet the only caller ever sent is the seeded
admin. In 709 lines the one refusal is anonymous on a GET (`:309-315`); no 403 anywhere, so the cross-workspace PATCH
(R34 §6 #1, see SS13) is unproven and unnoticed. also breaks: U2a, ST1 (`var req`), Spock-first.

**Good** (rewritten from `ToolControllerIT.java:328-354`) · NEEDS COMPILE CHECK
```groovy
def "should answer #caller with #expected when it renames a tool of workspace A"() {
    given: "a tool in workspace A, and the caller logged in through the real filter chain"
    def tool = toolIn(WORKSPACE_A)
    when: "the caller renames it"
    def status = patchAs(bearerFor(caller), "/api/tools/${tool.id()}", [name: "Updated Name"])
    then: "the status is the matrix's, and a refusal left the tool as it was"
    status == expected
    expected == 200 || toolRepository.findById(tool.id()).get() == tool
    where:
    caller           || expected
    ANONYMOUS        || 401
    EDITOR_OF_A      || 200
    EDITOR_OF_B      || 403
    API_KEY_OF_B     || 403
}
```
— What changed: the one admin call became a `where:` table of every caller kind (SS23), each with a real login
(`bearerFor`, SS22), and a refusal is checked to change nothing. Prevents the misreading "one wrong-role 403 (or
one 401) is the proof": the rows a role check cannot tell apart — `EDITOR_OF_B` and `API_KEY_OF_B` hold the same role
name as `EDITOR_OF_A` — are the ones that catch BOLA. On master `EDITOR_OF_B` gets 200, so this table fails until SS13
is fixed; the real spec also lists DELETE, test-connection and the viewer/owner/admin rows (4 of ~8 rows shown).

### AP4a — A `PUBLIC_PATHS` entry has an IT proving its replacement check refuses; no secret in a URL

**Bad** (ours)
```java
@Test
@DisplayName("POST /api/setup/complete → sets setupComplete to true")
void shouldSetSetupCompleteOnComplete() {
    // given / when / then
    http.post().uri("/api/setup/complete")
        .exchange()
        .expectStatus().isOk()
        .expectBody()
        .jsonPath("$.data.setupComplete").isEqualTo(true);
}
```
`aruvii-api/src/integrationTest/java/ai/aruvii/api/controller/SetupControllerIT.java:271-280` @ `772736bf` — `/api/setup/**`
is in `PUBLIC_PATHS` (`SecurityConfig.java:36`), so the "setup not yet complete" guard is the only thing that replaces
the JWT. Every sibling handler has it (`SetupController.java:50,60,70,83,95,111,124`); `complete()` at `:140-144` does
not, and its only IT is the happy path, so nobody saw that any anonymous caller can end setup on a live install. also
breaks: Spock-first, labelled blocks (a `// given / when / then` comment instead).

**Good** (rewritten from `SetupControllerIT.java:271-280`) · NEEDS COMPILE CHECK
```groovy
def "should refuse an anonymous caller who completes setup on a completed install"() {
    given: "an install whose setup is already complete"
    completeSetup()

    when: "a caller with no token posts to the public complete endpoint"
    def reply = http.post().uri("/api/setup/complete").exchange()

    then: "the check that replaces the JWT refuses it"
    reply.expectStatus().isBadRequest()
        .expectBody()
        .jsonPath('$.success').isEqualTo(false)
        .jsonPath('$.code').isNotEmpty()
}
```
— What changed: the IT now sends the bad caller the public path admits and proves the replacement check (setup done →
400, SS25's own example) refuses it; the happy path stays as a second feature. It fails on master until `complete()`
gets the sibling guard. Prevents the misreading "the MR sentence saying what replaces the JWT is enough" — the sentence
existed for the siblings; only a refusal IT catches the one handler that skipped it. The URL half (SS8, OQ-SS-3):
`/api/webhooks/{id}/{secret}` (`WebhookControllerIT.java:86`) passes this IT shape yet still fails AP4a until the
secret moves to a header.

### TT2 — Read a tool's required arguments off its handler; the schema is never stricter

No Bad in our code: `git log -S` finds no stricter email schema at any commit; #407 (`0b14f715`) wrote the handler-true
one first time. Both sides are **adapted** from pstack `refs/cursor-plugins/pstack/skills/principle-type-system-discipline/SKILL.md:21`
("derive from the authoritative shape instead of hand-rolling a parallel type") applied to the counterexample agent-platform
`CLAUDE.md:423-427` @ `772736bf` describes in prose. The handler facts are `EmailToolHandler.java:116-127` (`to` via
`toStringList`, refused if empty; `subject` refused if blank; `body` defaulted to `""`).

**Bad** (adapted from CLAUDE.md:423-427)
```java
@Override
public ToolInputContract inputContract(final Tool tool) {
    return new ToolInputContract.Declared("""
        {"type":"object",
         "properties":{
           "to":{"type":"string"},
           "subject":{"type":"string"},
           "body":{"type":"string"}},
         "required":["to","subject","body"]}
        """);
}
```
— written from what an email "obviously" needs: `to` as one string and `body` required. The handler serves a list of
recipients and an absent body, so this schema refuses calls that work — on a self-hosted upgrade a working tool stops.

**Good** (adapted from pstack SKILL.md:21 + CLAUDE.md:423-427) · NEEDS COMPILE CHECK
```java
@Override
public ToolInputContract inputContract(final Tool tool) {
    return new ToolInputContract.Declared("""
        {"type":"object",
         "properties":{
           "to":{"anyOf":[{"type":"string"},{"type":"array","items":{"type":"string"}}]},
           "subject":{"type":"string","description":"Must not be empty."},
           "body":{"type":"string","description":"Sent empty if omitted."}},
         "required":["to","subject"]}
        """);
}
```
— What changed: `to` takes what `toStringList` takes; `required` lists exactly the arguments the handler refuses
without; `body` is described as defaulted, not required. Prevents the misreading "stricter is safer": a schema the
handler would have served is a regression, not a hardening. (cc/bcc/html omitted for length.)

### SE1 — A URL not in code is fetched only through the checked fetch

**Bad** (ours)
```java
@SuppressWarnings("unchecked")
private String exchangeCode(OidcDiscoveryDoc doc, String code, String redirectUri) {
    MultiValueMap<String, String> form = new LinkedMultiValueMap<>();
    // … grant_type, code, redirect_uri, client_id, client_secret …
    Map<String, Object> body = restClient.post()
        .uri(doc.tokenEndpoint())
        .contentType(MediaType.APPLICATION_FORM_URLENCODED)
        .body(form)
        .retrieve()
        .body(Map.class);
    if (body == null || !body.containsKey("id_token")) {
        throw new IllegalStateException("Token endpoint did not return id_token");
    }
    return (String) body.get("id_token");
}
```
`aruvii-api/src/main/java/ai/aruvii/api/controller/OidcController.java:163-183` @ `772736bf` — the discovery document
itself is fetched through `SsrfGuard` (`OidcSettingsService.java:91-102`), but the `token_endpoint` it *returned* is
posted to unchecked, carrying the client secret, on `RestClient.create()` (`:54`) with no redirect policy of ours.
`jwks_uri` (`:131`) is the same. also breaks: SE5 (`Map.class` + casts), ER2 (`IllegalStateException`), ST1, SS11
(hand-rolled code exchange).

**Good** (rewritten from `OidcController.java:163-183`) · NEEDS COMPILE CHECK
```java
private String exchangeCode(final OidcDiscoveryDoc doc, final String code, final String redirectUri) {
    final CheckedUrl tokenEndpoint = switch (ssrfGuard.check(doc.tokenEndpoint())) {
        case SsrfDecision.Blocked blocked -> throw new AruviiException(
                ErrorCode.OIDC_ENDPOINT_BLOCKED,
                blocked.host());
        case SsrfDecision.Permitted permitted -> permitted.target();
    };
    final OidcTokenResponse tokens = noRedirectRestClient.post()
            .uri(tokenEndpoint.value())
            .contentType(MediaType.APPLICATION_FORM_URLENCODED)
            .body(tokenRequestForm(code, redirectUri))
            .retrieve()
            .body(OidcTokenResponse.class);
    return tokens.idToken();
}
```
— What changed: the endpoint goes through the same `SsrfGuard` decision as the document it came from; the client is
built with redirects off; the reply binds to a record (`OidcTokenResponse(@JsonProperty("id_token") String idToken)`,
compact ctor rejects a blank token, SE5); a refusal is an `AruviiException` with a new catalogue code (ER2, proposed
`OIDC_ENDPOINT_BLOCKED`). Prevents the misreading "a URL from a document we fetched safely is ours": every hop the
remote side names is untrusted. Edge kept: no address pinning (`SsrfGuard.java:20-23`, REQ-107 D4). Under SS11 this
method is replaced by `oauth2Login`; the checked, no-redirect client then backs Spring's token-response client.

### SE4 — Resolve a user-supplied path with `toRealPath()`, then check `startsWith(base)`

**Bad** (ours)
```java
public void validatePath(String basePath, String relativePath, List<String> allowedExtensions) {
    if (relativePath.contains("..")) {
        throw new SecurityException("Path traversal detected in: " + relativePath);
    }
    Path base     = Paths.get(basePath).toAbsolutePath().normalize();
    Path resolved = base.resolve(relativePath).normalize();
    if (!resolved.startsWith(base)) {
        throw new SecurityException("Path escapes basePath: " + relativePath);
    }
    String fileName = resolved.getFileName().toString();
    boolean allowed = allowedExtensions.stream()
        .anyMatch(ext -> fileName.toLowerCase().endsWith(ext.toLowerCase()));
    if (!allowed) throw new SecurityException("File extension not allowed: " + fileName);
}
```
`aruvii-tools/src/main/java/ai/aruvii/tools/infrastructure/handlers/FileToolHandler.java:50-63` @ `772736bf` (unchanged
since `161f71fd`) — `normalize()` and the `".."` test are lexical: a symlink inside `basePath` pointing at `/etc` passes
both, and `:152-153` resolves the path a second time and reads it. The model chooses `path` (SE10). also breaks: ER1
(a refusal the model will foreseeably trigger is thrown, then caught at `:145-147`), ST1, U4 (`:150`).

**Good** (rewritten from `FileToolHandler.java:50-63`) · NEEDS COMPILE CHECK
```java
PathCheck resolveInside(final Path realBase, final String requested) {
    final Path candidate = realBase.resolve(requested).normalize();
    if (!candidate.startsWith(realBase)) {
        return new PathCheck.Outside();
    }
    try {
        final Path real = candidate.toRealPath();
        return real.startsWith(realBase) ? new PathCheck.Inside(real) : new PathCheck.Outside();
    } catch (final IOException missingOrUnreadable) {
        return new PathCheck.NotFound();
    }
}
```
— What changed: the decisive check runs on `toRealPath()` (symlinks followed), against a base the caller resolved once
with `toRealPath()` too; the method returns the real `Path` it checked inside a sealed `PathCheck`
(`Inside(Path real) | Outside | NotFound`), so the reader opens exactly what was checked and the handler switches it
to `success` / `PATH_BLOCKED` / `FILE_NOT_FOUND` (ER1, SEAM1 "record in, sealed out"). The lexical check stays only
as a first refusal so a path outside the base never reaches the file system (no exists-or-not answer about `/etc`).
The extension check moves to its own method (one job). Prevents the misreading "`normalize()` plus a `..` test is
complete". The file tool only reads; a delete or move would add SE4's depth and ownership checks.

### SE5 — Untrusted JSON binds to a fixed record; no `Map<String,Object>` past the adapter

**Bad** (ours)
```java
Map<String, Object> body = restClient.get()
    .uri(checked.value())
    .retrieve()
    .body(Map.class);
if (body == null) throw new IllegalStateException("Empty OIDC discovery response from " + url);
return new OidcDiscoveryDoc(
    (String) body.get("authorization_endpoint"),
    (String) body.get("token_endpoint"),
    (String) body.get("jwks_uri")
);
// …
public record OidcDiscoveryDoc(String authorizationEndpoint,
                               String tokenEndpoint,
                               String jwksUri) {}
```
`aruvii-api/src/main/java/ai/aruvii/api/service/OidcSettingsService.java:105-114,121-123` @ `772736bf` (method carries
`@SuppressWarnings("unchecked")`, `:90`) — the typed record already exists, yet the IdP's reply is read as a raw
`Map` and cast field by field: a number where a string belongs is a `ClassCastException`, a missing key is a `null`
endpoint that fails three calls later in `OidcController`. also breaks: ER2 (`IllegalStateException`), ST1, ST2.

**Good** (rewritten from `OidcSettingsService.java:105-114,121-123`) · NEEDS COMPILE CHECK
```java
final OidcDiscoveryDoc discovery = restClient.get()
        .uri(checked.value())
        .retrieve()
        .body(OidcDiscoveryDoc.class);
return Optional.ofNullable(discovery)
        .orElseThrow(() -> new AruviiException(ErrorCode.OIDC_DISCOVERY_FAILED));
// …
public record OidcDiscoveryDoc(
        @JsonProperty("authorization_endpoint") String authorizationEndpoint,
        @JsonProperty("token_endpoint") String tokenEndpoint,
        @JsonProperty("jwks_uri") String jwksUri) {
    public OidcDiscoveryDoc {
        requireUrls(authorizationEndpoint, tokenEndpoint, jwksUri);
    }
}
```
— What changed: the reply binds straight to the record we already had (OQ-R27-3: "if there is a type, use it"); the
compact constructor refuses a blank or missing endpoint at the boundary, so a bad document fails at parse with one
error, not three calls later; no casts, no `@SuppressWarnings`; a fault is an `AruviiException` (ER2, proposed code
`OIDC_DISCOVERY_FAILED`). Prevents the misreading "it is inside the adapter, so a `Map` is allowed": OQ-R27-3 admits
a `Map` only for a shape we cannot type cheaply — three named strings are the cheapest type there is.

### SS13 — A workspace-resource guard asks `@wsAuth`; `hasRole` names platform roles only

**Bad** (ours)
```java
@PatchMapping("/{id}")
@PreAuthorize("hasAnyRole('SUPER_ADMIN','PLATFORM_ADMIN','WORKSPACE_OWNER','WORKSPACE_EDITOR')")
public ApiResponse<ToolResponse> update(@PathVariable UUID id,
                                        @RequestBody UpdateToolRequest req) {
    return ApiResponse.ok(toolService.update(id, req));
}

@DeleteMapping("/{id}")
@ResponseStatus(HttpStatus.NO_CONTENT)
@PreAuthorize("hasAnyRole('SUPER_ADMIN','PLATFORM_ADMIN','WORKSPACE_OWNER')")
public void delete(@PathVariable UUID id) {
    toolService.delete(id);
}
```
`aruvii-api/src/main/java/ai/aruvii/api/controller/ToolController.java:69-81` @ `772736bf` — `WORKSPACE_EDITOR` is held
*in some workspace*; `hasAnyRole` cannot ask *which*, so an editor of workspace B may rename or (as owner of B) delete a
tool of workspace A — probable BOLA (R34 §6 #1). `@wsAuth.canEditTool` / `canDeleteTool` already exist
(`WorkspaceAuthorization.java:97-103`) and nothing in `main` calls them. also breaks: SS14 (workspace role names in a
guard), AP3a (no IT can see it, see above), `:72` `@RequestBody` without `@Valid`.

**Good** (rewritten from `ToolController.java:69-81`) · NEEDS COMPILE CHECK
```java
@PatchMapping("/{id}")
@PreAuthorize("@wsAuth.canEditTool(#id)")
public ApiResponse<ToolResponse> update(
        @PathVariable final UUID id,
        @RequestBody @Valid final UpdateToolRequest request) {
    return ApiResponse.ok(toolService.update(id, request));
}

@DeleteMapping("/{id}")
@ResponseStatus(HttpStatus.NO_CONTENT)
@PreAuthorize("@wsAuth.canDeleteTool(#id)")
public void delete(@PathVariable final UUID id) {
    toolService.delete(id);
}
```
— What changed: each guard asks about *this* tool's workspace through `@wsAuth`, which resolves the tool's
`workspace_id` and checks the caller's role there; platform admins still pass, via the bypass inside
`JwtAuthentication.hasWorkspaceRole` (`:111-112`), so no platform role needs naming. Prevents the misreading
"`hasAnyRole('WORKSPACE_EDITOR')` is a correct workspace check" — a role name says *what* the caller is, never *where*.
An API key reaches the same answer through `api_keys.workspace_id` (OQ-SS-4). Proven by the AP3a matrix.

### SS21 — Passwords via `DelegatingPasswordEncoder`; machine secrets via HMAC-SHA-256; never the encoder per request

**Bad** (ours)
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
}
// ApiKeyService — runs on every request that carries an API key
ApiKeyEntity found = null;
if (rawKey != null && rawKey.startsWith("ak_")) {
    String prefix = rawKey.substring(0, Math.min(8, rawKey.length()));
    found = apiKeyRepo.findByKeyPrefix(prefix).stream()
        .filter(ApiKeyEntity::isValid)
        .filter(k -> passwordEncoder.matches(rawKey, k.getKeyHash()))
        .findFirst()
        .filter(this::ownerStillHoldsRole)
        .orElse(null);
}
```
`aruvii-auth/src/main/java/ai/aruvii/auth/infrastructure/AuthAutoConfiguration.java:16-19` and
`aruvii-auth/src/main/java/ai/aruvii/auth/application/ApiKeyService.java:239-248` @ `772736bf` — one BCrypt(12) bean
serves both human passwords and API keys, so every API-key request pays a deliberately slow hash per candidate row (and
an `ak_` prefix collision multiplies it). The key itself is 24 hex chars of a UUID (`:112`, ~92 random bits, under the
128 SS21 asks). also breaks: TY1 (`null` means "not authenticated", `:239,256`), ST1, U4 (`:236`).

**Good** (rewritten from `AuthAutoConfiguration.java:16-19` + `ApiKeyService.java:239-248`) · NEEDS COMPILE CHECK
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();
}
// ApiKeyService
public Optional<ApiKeyEntity> authenticateKey(final ApiKeyCandidate candidate) {
    final byte[] presented = apiKeyMac.digest(candidate.rawKey());
    return apiKeyRepo.findByKeyPrefix(candidate.prefix()).stream()
            .filter(ApiKeyEntity::isValid)
            .filter(key -> MessageDigest.isEqual(presented, key.getKeyHmac()))
            .findFirst()
            .filter(this::ownerStillHoldsRole);
}
```
— What changed: passwords go through `DelegatingPasswordEncoder` (SSR `features/authentication/password-storage.html`
§DelegatingPasswordEncoder: `PasswordEncoderFactories.createDelegatingPasswordEncoder()`,
bcrypt by default, re-hashable later); API keys are HMAC-SHA-256 under a server key (`apiKeyMac`, a key distinct from
the JWT and credential keys, SE7a) and compared with `MessageDigest.isEqual` (constant time). The filter parses the
header into `ApiKeyCandidate` (prefix checked there), so no `null` reaches here; "no key" is `Optional.empty()`.
Creation (`:112,118`) changes with it: 32 bytes from `SecureRandom`, stored as `apiKeyMac.digest(raw)`. Prevents the
misreading "BCrypt everything is safest" — SSR §Password Storage History: an adaptive hash is meant to cost ~1 s
and should not be verified per request; a ≥128-bit random key needs no work factor. Existing BCrypt key hashes need a
migration (re-issue or verify-once-then-rehash) — out of this example.

---

## Counts

| | n | rules |
|---|---|---|
| pairs written | 8 | AP3a AP4a TT2 SE1 SE4 SE5 SS13 SS21 |
| Bad = our real code @ `772736bf` | 7 | AP3a AP4a SE1 SE4 SE5 SS13 SS21 |
| Good rewritten from that Bad | 7 | same 7 |
| both sides adapted (no Bad in our code) | 1 | TT2 (pstack type-system SKILL.md:21 + agent-platform CLAUDE.md:423-427) |
| Goods that are our code as-is | 0 | — |
| Goods NEEDS COMPILE CHECK | 8 | all |
| Goods that fail on master until the fix lands | 2 | AP3a (needs SS13), AP4a (needs `complete()` guard) |
| new `ErrorCode` values proposed in a Good | 2 | `OIDC_ENDPOINT_BLOCKED` (SE1), `OIDC_DISCOVERY_FAILED` (SE5) |

Real defects surfaced while writing (not fixed here): `ToolController` PATCH/DELETE cross-workspace (SS13);
`POST /api/setup/complete` unguarded on a public path (AP4a); OIDC `token_endpoint` and `jwks_uri` fetched without
`SsrfGuard` (SE1); `FileToolHandler` symlink escape (SE4); API keys ~92 bits and BCrypt-verified per request (SS21).
