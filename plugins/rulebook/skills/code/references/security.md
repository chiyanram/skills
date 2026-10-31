# Security

How code treats untrusted input, stores secrets, authenticates and authorizes a caller in Spring Security, and tests
those controls. Read it when you write or review code that takes outside input, stores or checks a secret, or touches
the security filter chain, a guard, a token or a security test.

Contents: Rules · When X, use Y · Good / Bad (SE1, SS21) · Decided edges · Review checks

The public-path list is the set of paths the filter chain permits without a token. A guard is an authorization check
on a handler, such as `@PreAuthorize`.

## Rules

### Untrusted input and output

- **SE10** — Treat model output and tool arguments as untrusted: schema-check them before SQL, shell, `innerHTML` or a
  path, and enforce permissions in code, because injected text can hijack the prompt, which is no security boundary.
- **SE1** — Fetch a URL not in code only after a URL check: http or https only, private or reserved IPs
  refused after DNS resolution, no redirects, because a user-influenced URL can be aimed at internal services.
- **SE3** — Bind every SQL parameter, and take a dynamic identifier from an allowlist defined in code, because input
  concatenated into SQL is an injection surface.
- **SE4** — Resolve a user-supplied path with `toRealPath()`, then check `startsWith(base)`; a destructive operation
  also checks depth and ownership, because `normalize()` and a `..` check let a symlink escape the base.
- **SE5** — Bind untrusted JSON, a third-party response included, to a fixed record DTO, with no default or
  polymorphic typing and no `Map<String,Object>` past the adapter, because payload-chosen types let the attacker pick
  what gets instantiated.
- **SE6** — Use `[innerHTML]` or `bypassSecurityTrust*` only for content the code controls, never for user or model
  text, because user or model text bound raw into the page enables XSS.

### Secrets

- **SE2** (operator preference, 2026-10-31) — Stop the call when decryption fails, and never fall back to
  unauthenticated, cached or default credentials, because a fallback sends the call unauthenticated or with a cached
  credential.
- **SE7** — Encrypt a stored credential with AES-GCM and mask it in every response; hash passwords with BCrypt, never
  MD5, SHA-1 or DES, because those weak algorithms fail to protect secrets.
- **SS21** — Hash human passwords with `DelegatingPasswordEncoder` (bcrypt ≥10); hash machine secrets of ≥128 bits
  with server-keyed HMAC-SHA-256, compared in constant time, because a per-request slow hash makes a public endpoint a
  CPU sink.
- **SE7a** (operator preference, 2026-10-31) — Keep the credential-encryption key distinct from the token signing key,
  because a key used for two purposes exposes both uses when one leaks.
- **SE8** — Apply rate limiting and user quotas before any LLM call reaches a provider, because uncapped LLM calls
  cause unbounded consumption (OWASP LLM10).

### Filter chain and authorization

- **SS1** — End `authorizeHttpRequests` with `anyRequest().denyAll()`, and give every endpoint a public-path entry or
  an explicit `authenticated()` or role matcher, because a forgotten path stays open to any authenticated caller.
- **SS12** — Give every controller handler `@PreAuthorize`, on the method or the class, or a public-path entry,
  enforced by an architecture test with a written exempt list, because method security leaves an unannotated handler
  open.
- **SS2** (operator preference, 2026-10-31) — Permit `ERROR` and `ASYNC` dispatches in one matcher with the reason in
  a comment, never `REQUEST` or `FORWARD`, because Spring Security authorizes every dispatch type by default.
- **SS3** — Register a custom security `Filter` in the chain and disable its servlet registration with
  `FilterRegistrationBean.setEnabled(false)`, because a `Filter` bean runs twice: once in the chain, once out of order.
- **SS4** — Answer an `Authorization` header with an invalid, expired or wrong-type token with 401 at once, on public
  paths too, because a swallowed token error turns a bad credential into anonymous access.
- **SS5** — Configure CORS only for a named cross-origin client, through `http.cors(…)` with an origin allowlist,
  never `*` or `allowedOriginPatterns("*")` with credentials, because a reflected credentialed origin lets any site
  read a credentialed response.
- **SS17** (operator preference, 2026-10-31) — Filter collections in the query and never put `@PostAuthorize` or
  `@PostFilter` on a method that writes, because `@PostAuthorize` runs after the write commits, so a denial undoes
  nothing.
- **SS26** (operator preference, 2026-10-31) — For a security design, adapt Spring Security's pattern
  (`AuthorizationManager`, a SpEL bean, a chain filter, a meta-annotation) after reading its source, because a
  hand-rolled check misses what the framework already checks.

### Tokens and sessions

- **SS6** — Keep access tokens short-lived, and read tenant membership and account status from the database at
  decision time, because a removed or deactivated user keeps role access for the token's life.
- **SS7** — Give each token purpose its own `typ`; verification pins the algorithm and checks `typ` and `exp`,
  because without an explicit type a token made for one purpose passes as another.
- **SS8** — Carry an access token, refresh token or long-lived secret in a header, an HttpOnly cookie or a single-use
  short-lived ticket, never a URL, because a URL leaks into access logs, browser history and Referer.
- **SS9** — Set a credential cookie `HttpOnly; Secure; SameSite=Strict` with the narrowest `Path`, and reject a
  cross-site `Origin` on its endpoints, because a stateless API is still open to CSRF when a cookie authenticates.
- **SS10** — Rotate the refresh token on every use, and revoke all of a user's refresh tokens on password change or
  reset, deactivation and role change, because a stolen refresh token otherwise survives the victim's password reset.
- **SS11** — Accept an IdP `id_token` through Spring `oauth2Login` after signature, `iss`, `aud`, `exp` and
  `nonce` checks, with `state` bound to the browser, because without them a replayed token or
  login CSRF succeeds.

### Errors and headers

- **SS19** — In production, keep `server.error.include-message` and binding errors off, so an error body carries only
  a code and a fixed message, because `include-message: always` sends internal exception text to clients.
- **SS20** — Keep every Spring default security header, and name the threat in the merge request for any change to
  CSP, HSTS or frame options, because each default header turns on a browser protection.

### Security tests

- **SS22** (operator preference, 2026-10-31) — Authenticate security ITs through the real login and filter chain (IT3,
  [integration-tests.md](../../testing/references/integration-tests.md)), with `@WithMockUser` or `jwt()` only in a
  guard bean's unit spec, because mock users skip the filter building authorities.
- **SS23** (operator preference, 2026-10-31) — Give each guarded controller a matrix IT: caller kind (anonymous, each
  role, another tenant's member, a machine client) × endpoint → status, a refusal changing nothing, because one
  wrong-role test misses other caller kinds.
- **SS24** — Keep ITs that send a forged, expired, `alg:none`, wrong-key and wrong-`typ` token and expect 401, because
  JWT libraries have shipped critical flaws that accepted forged tokens.
- **SS25** (operator preference, 2026-10-31) — Give each public-path entry an IT proving the check that replaces the
  token refuses a bad caller, because on a public path that check is the only guard.

## When X, use Y

| the code | use | why |
|---|---|---|
| fetches a URL from config, a user or a remote document | the URL check on a client with redirects off, for every URL the remote side names (SE1) | a user-influenced URL can be aimed at internal services · addyosmani security-and-hardening "reject any private or reserved address"; OWASP SSRF Cheat Sheet "Disable the support for the following of the redirection" |
| puts a value or a column name into SQL | a bound parameter for a value; an allowlist in code for an identifier (SE3) | input concatenated into SQL is an injection surface · OWASP SQL Injection Prevention Cheat Sheet §Prepared Statements, §Allow-list Input Validation; plinth 124-java-secure-coding "Never concatenate user input directly into SQL"; addyosmani security-checklist |
| opens a path a caller supplied | `toRealPath()`, then `startsWith(base)`; depth and ownership too before a delete (SE4) | `normalize()` does not follow symlinks · SEI CERT FIO16-J "fully resolved before any file validation"; addyosmani security-checklist "symlinks resolved BEFORE the check"; JDK `Path.normalize` "does not access the file system" |
| passes model output or tool arguments on | a schema check first; the permission check in code, not the prompt (SE10) | the prompt is no security boundary · OWASP GenAI LLM05 Improper Output Handling; addyosmani security-and-hardening "Model output is untrusted input" |
| stores a human password | `DelegatingPasswordEncoder` with bcrypt (SS21) | adaptive hashing is for passwords · Spring Security password storage "adaptive one-way functions"; OWASP Password Storage Cheat Sheet "bcrypt, use a work factor of 10 or more" |
| stores a machine-generated secret of ≥128 bits | server-keyed HMAC-SHA-256 and `MessageDigest.isEqual` (SS21) | a slow hash checked per request is a CPU sink · Spring Security password storage: a short-term credential must validate quickly |
| stores a credential it must send later | AES-GCM; masked in every response (SE7) | MD5, SHA-1 and DES fail to protect secrets · OWASP Cryptographic Storage Cheat Sheet "GCM"; plinth 124-java-secure-coding |
| must carry a bearer credential to the server | a header, an HttpOnly cookie, or a single-use short-lived ticket (SS8) | a URL leaks into logs and Referer · RFC 6750 §2.3, §5.3; OWASP REST Security Cheat Sheet |
| authenticates with a cookie | `HttpOnly; Secure; SameSite=Strict`, narrowest `Path`, and an `Origin` check (SS9) | stateless is no CSRF protection when a cookie authenticates · Spring Security csrf §CSRF and Stateless Browser Applications; OWASP Session Management and CSRF Prevention Cheat Sheets |
| serves a named cross-origin client | `http.cors(…)` with an origin allowlist (SS5) | a reflected credentialed origin lets any site read a response · Spring Security cors; ASVS 3.4.2; plinth 304-frameworks-spring-boot-security |
| logs users in through an external IdP | Spring `oauth2Login` (SS11) | `nonce` stops replay, bound `state` stops login CSRF · OIDC Core §3.1.3.7; ASVS V10 |
| checks who owns a resource, or adds an auth step | an `AuthorizationManager`, a SpEL bean, a chain filter or a meta-annotation (SS26) | operator preference: a hand-rolled check misses what the framework already checks |
| decides on membership or account status | a database read at decision time, not a token claim (SS6) | authz changes apply at once · ASVS 8.3.2, 7.4.2; spring-boot-skills spring-security-jwt "validate current account status" |
| tests a guard | a guard bean's unit spec may use `@WithMockUser` or `jwt()`; an IT logs in for real (SS22) | operator preference · Spring Security testing: `@WithMockUser` "cannot apply to full HTTP requests" |

## Good / Bad

Every rule's approved pair: [examples/security.md](examples/security.md).

### SE1 — A URL not in code is fetched only through the checked fetch

**Bad** (neutral)
```java
private RefundReply requestRefund(final GatewayDiscovery discovery, final RefundRequest request) {
    final RefundReply reply = restClient.post()
            .uri(discovery.refundEndpoint())
            .contentType(MediaType.APPLICATION_JSON)
            .header("X-Api-Secret", gatewaySecret)
            .body(request)
            .retrieve()
            .body(RefundReply.class);
    return reply;
}
```
The discovery document was fetched through the URL check, but the endpoint it returned is called unchecked, carrying
the secret.

**Good** (neutral)
```java
private RefundReply requestRefund(final GatewayDiscovery discovery, final RefundRequest request) {
    final CheckedUrl refundEndpoint = switch (urlGuard.check(discovery.refundEndpoint())) {
        case UrlDecision.Blocked blocked -> throw new OrderException(
                ErrorCode.GATEWAY_URL_BLOCKED,
                blocked.host());
        case UrlDecision.Permitted permitted -> permitted.target();
    };
    return noRedirectRestClient.post()
            .uri(refundEndpoint.value())
            .contentType(MediaType.APPLICATION_JSON)
            .header("X-Api-Secret", gatewaySecret)
            .body(request)
            .retrieve()
            .body(RefundReply.class);
}
```
Every URL the remote side names passes the same check, on a client with redirects off. (Real evidence: ledger row
SE1.)

### SS21 — Passwords via `DelegatingPasswordEncoder`; machine secrets via HMAC-SHA-256; never the encoder per request

**Bad** (neutral)
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
}
// ApiKeyService — runs on every request that carries an API key
ApiKeyEntity found = null;
if (rawKey != null && rawKey.startsWith("ok_")) {
    String prefix = rawKey.substring(0, Math.min(8, rawKey.length()));
    found = apiKeyRepository.findByKeyPrefix(prefix).stream()
        .filter(ApiKeyEntity::isValid)
        .filter(key -> passwordEncoder.matches(rawKey, key.getKeyHash()))
        .findFirst()
        .orElse(null);
}
```
One slow password hash also checks API keys, so every API-key request pays a deliberately slow hash per candidate row.

**Good** (neutral)
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();
}
// ApiKeyService
public Optional<ApiKeyEntity> authenticateKey(final ApiKeyCandidate candidate) {
    final byte[] presented = apiKeyMac.digest(candidate.rawKey());
    return apiKeyRepository.findByKeyPrefix(candidate.prefix()).stream()
            .filter(ApiKeyEntity::isValid)
            .filter(key -> MessageDigest.isEqual(presented, key.getKeyHmac()))
            .findFirst();
}
```
Passwords keep an adaptive hash; a random 128-bit key needs only a keyed HMAC, compared in constant time. (Real
evidence: ledger row SS21.)

## Decided edges

- **Skip when** the dispatch is `ERROR` or `ASYNC`: permit it in one matcher, with the reason in a comment (SS2). —
  **Do not skip when** the dispatch is `REQUEST` or `FORWARD`. — **Confidence** high (Spring Security
  authorize-http-requests "authorizes all dispatcher types by default")
- **Skip when** method security does not yet guard every handler: `anyRequest().authenticated()` stays last (SS1). —
  **Do not skip when** the SS12 architecture test is in place: change to `denyAll()` with it. — **Confidence** high
- **Skip when** the token's issuer is its only verifier: `iss` and `aud` may be left out (SS7). — **Do not skip
  when** a second party verifies the token: add `iss` and `aud`. — **Confidence** high (RFC 8725 §3.9; OWASP JSON
  Web Token Cheat Sheet §MAC "Do not reuse the same secret with another audience")
- **Skip when** an existing external caller sends a webhook secret in the URL path: accept a header form, keep the
  path form one release, then remove it (SS8). — **Do not skip when** the endpoint is new. — **Confidence** high

## Review checks

Walk every changed file that takes outside input, stores or checks a secret, configures the filter chain, or holds a
guard, a token or a security test. Each rule below gets a check.

- [ ] SE10 — Trace every model output and tool argument to its sink. Reaching SQL, a shell, `innerHTML` or a path
  without a schema check, or a permission enforced only by prompt text, is a finding.
- [ ] SE1 — For each outbound HTTP call (`grep -nE "\.uri\(|new URL\(|URI.create"`), the URL is a literal in code or
  passed the URL check, on a client with redirects off. A URL check that allows a scheme
  other than http or https, or does not refuse private and reserved IPs after DNS resolution, is a finding. Any other
  URL is a finding.
- [ ] SE3 — String concatenation or `formatted(` that builds SQL from a variable is a finding, unless the variable
  is an identifier taken from an allowlist in code.
- [ ] SE4 — For each caller-supplied path, find `toRealPath()` before `startsWith`. A `normalize()`-only or `..`
  check is a finding; a delete without depth and ownership checks is a finding.
- [ ] SE5 — Untrusted JSON bound to anything but a fixed record DTO is a finding: `Map<String, Object>` past the
  adapter, `activateDefaultTyping` or `@JsonTypeInfo`.
- [ ] SE6 — Each `[innerHTML]` or `bypassSecurityTrust` (`grep -rnE "innerHTML|bypassSecurityTrust"`) binds content
  the code controls. User or model text is a finding.
- [ ] SE2 — Open each decrypt call. A failure that continues with no credential, a cached one or a default one is
  a finding.
- [ ] SE7 — Each stored credential is encrypted with AES-GCM and masked in every response, and each password is
  hashed with BCrypt. MD5, SHA-1 or DES for a secret (`grep -nE "MD5|SHA-1|SHA1|DES"`) is a finding.
- [ ] SS21 — Passwords go through `DelegatingPasswordEncoder` with bcrypt cost ≥10. Machine secrets go through
  server-keyed HMAC-SHA-256 and a constant-time compare. A password encoder on a machine secret, or `equals` on a
  secret, is a finding.
- [ ] SE7a — One key used for both credential encryption and token signing is a finding.
- [ ] SE8 — Each new LLM provider call path passes the rate limiter before the call. A path that skips it is a
  finding.
- [ ] SS1 — The last matcher in `authorizeHttpRequests` is `anyRequest().denyAll()`, or a Decided edge allows
  `authenticated()`. A new endpoint matched only by the last line is a finding.
- [ ] SS12 — Only where no gate enforces it (the SS12 architecture test): a controller handler with no
  `@PreAuthorize`, on the method or the class, and no public-path entry is a finding. A new exempt-list entry without
  a reason is a finding.
- [ ] SS2 — A `dispatcherTypeMatchers` that permits `REQUEST` or `FORWARD`, or permits without a reason comment, is a
  finding.
- [ ] SS3 — A class extending `OncePerRequestFilter` or `Filter` that is not added to the chain, or is a `@Component`
  with no `FilterRegistrationBean.setEnabled(false)`, is a finding.
- [ ] SS4 — In each token filter, an invalid, expired or wrong-type token that continues the chain, on any path,
  public ones too, is a finding.
- [ ] SS5 — Each CORS config (`grep -nE "allowedOrigin|CorsConfiguration"`) serves a named cross-origin client
  through `http.cors(…)` with an origin allowlist. `*` or `allowedOriginPatterns("*")` with credentials is a finding.
- [ ] SS17 — `@PostAuthorize` or `@PostFilter` on a writing method, or an in-memory filter of query results by
  permission, is a finding.
- [ ] SS26 — A new hand-written authentication or authorization mechanism where a Spring Security pattern exists is a
  finding.
- [ ] SS6 — An access token with no short lifetime set in configuration, or a guard that reads membership or account
  status from a token claim, is a finding.
- [ ] SS7 — A token purpose with no own `typ`, a missing `typ` check, an unpinned algorithm, or no `exp` check is a
  finding.
- [ ] SS8 — A token or secret read from a query parameter or path variable (`grep -nE "getParameter\(\"token|\?token="`)
  is a finding, outside the webhook Decided edge.
- [ ] SS9 — Each credential cookie (`grep -n "ResponseCookie"`) sets `HttpOnly`, `Secure`, `SameSite=Strict` and a
  narrow `Path`, and its endpoint checks `Origin`. A missing one is a finding.
- [ ] SS10 — Each refresh issues a new token and revokes the old one. A password change or reset, deactivation or role
  change that leaves refresh tokens alive is a finding.
- [ ] SS11 — An IdP login outside `oauth2Login`, or one that skips the signature, `iss`, `aud`, `exp`, `nonce` or
  browser-bound `state` check, is a finding.
- [ ] SS19 — `include-message` or `include-binding-errors` set to anything but `never` in production configuration is
  a finding.
- [ ] SS20 — A removed default header, or a CSP, HSTS or frame-options change with no threat named in the merge
  request, is a finding.
- [ ] SS22 — Each security IT gets its token from the real login. `@WithMockUser` or `jwt()` in an IT
  (`grep -rnE "@WithMockUser|jwt\(\)"`) is a finding.
- [ ] SS23 — Each guarded controller's IT covers anonymous, each role, another tenant's member and a machine client
  on each endpoint, and shows a refusal changes nothing. A missing caller kind is a finding.
- [ ] SS24 — The token ITs send forged, expired, `alg:none`, wrong-key and wrong-`typ` tokens and expect 401. A missing
  case is a finding.
- [ ] SS25 — Each new public-path entry has an IT where a bad caller is refused by the replacement check. None is a
  finding.
