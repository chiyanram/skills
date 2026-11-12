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
- **SE1** — Fetch a URL not in code only after one check: http or https, every resolved IP outside private
  and reserved ranges, connect to that IP, redirects off, because a user-influenced URL can reach internal services.
- **SE3** — Bind every SQL parameter, and take a dynamic identifier from an allowlist defined in code, because input
  concatenated into SQL is an injection surface.
- **SE4** — Resolve a caller-supplied path and its base with `toRealPath()`, then check `Path.startsWith(base)`;
  before a delete, move or overwrite also check the caller owns the target, because `normalize()` lets a symlink
  escape the base.
- **SE5** — Bind untrusted JSON to a fixed DTO holding only the fields the caller may set, with no default typing and
  no class-name type ids (`Id.CLASS`), because payload-chosen classes let the attacker pick what is instantiated.
- **SE6** — Use `[innerHTML]` or `bypassSecurityTrust*` only for content the code controls, never for user or model
  text, because user or model text bound raw into the page enables XSS.

### Secrets

- **SEN2** — Read every key and credential from the environment or a secret store, never a literal in code or config,
  because committed secrets survive in history.
- **SE2** — Stop the call when decryption fails, and never fall back to unauthenticated, cached or default
  credentials, because a fallback sends the call unauthenticated or with a cached credential.
- **SS21** — Hash human passwords with `DelegatingPasswordEncoder` (bcrypt ≥10); hash machine secrets of ≥128 bits
  with server-keyed HMAC-SHA-256, compared in constant time, because a per-request slow hash makes a public endpoint a
  CPU sink.
- **SE7** — Encrypt a stored credential the code must send later with AES-GCM (Spring's `AesGcmBytesEncryptor`),
  never ECB or MD5, SHA-1 or DES, and mask it in every response, because unauthenticated or weak ciphers expose it.
- **SE7a** — Give each key one purpose: the credential-encryption key, each token-signing key and each HMAC key are
  separate secrets, because a key shared across purposes lets output made for one pass as another.
- **SE8** — Pass every LLM provider call through a per-caller rate limit and quota first, because uncapped calls let
  one caller run up unbounded cost and exhaust the provider quota.

### Filter chain and authorization

- **SS1** — End `authorizeHttpRequests` with `anyRequest().denyAll()`, and give every endpoint a public-path entry or
  an explicit `authenticated()` or role matcher, because a forgotten path stays open to any authenticated caller.
- **SS16** — Give a service method called from a non-HTTP entry point (worker, scheduler, listener) its own
  authorization check, because the filter chain and controller guards never see that call.
- **SS2** — Permit `FORWARD` and `ERROR` dispatches with `dispatcherTypeMatchers(FORWARD, ERROR).permitAll()`, never
  `REQUEST`, because Spring Security authorizes every dispatch, so a forward or error dispatch can fail with an
  unexpected `AccessDeniedException`.
- **SS3** — Register a custom security `Filter` in the chain and disable its servlet registration with
  `FilterRegistrationBean.setEnabled(false)`, because a `Filter` bean runs twice: once in the chain, once out of order.
- **SS4** — Answer an `Authorization` header with an invalid, expired or wrong-type token with 401 at once, on public
  paths too, because a swallowed token error turns a bad credential into anonymous access.
- **SS5** — Configure CORS only for a named cross-origin client, through `http.cors(…)` with an origin allowlist,
  never `*` or `allowedOriginPatterns("*")` with credentials, because a reflected credentialed origin lets any site
  read a credentialed response.
- **SS17** — Filter collections in the query and never put `@PostAuthorize` or `@PostFilter` on a method that writes,
  because `@PostAuthorize` runs after the write commits, so a denial undoes nothing.
- **SS26** — For a security design, adapt Spring Security's pattern (`AuthorizationManager`, a SpEL bean, a chain
  filter, a meta-annotation) after reading its source, because a hand-rolled check misses what the framework already
  checks.

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
- **SEN1** — Rate-limit failed authentication attempts per account, because an unthrottled login or key check lets an
  attacker guess passwords online.

### Errors and headers

- **SS19** — In production, keep `server.error.include-message` and binding errors off, so an error body carries only
  a code and a fixed message, because `include-message: always` sends internal exception text to clients.
- **SS20** — Keep every Spring Security default response header; a change may tighten CSP, HSTS or framing but never
  removes or loosens one, because each default header is a browser protection that disappears silently.

### Security tests

- **SS22** — Authenticate security ITs through the real login and filter chain (`testing`
  skill's stack notes), with `@WithMockUser` or `jwt()` only in a
  guard bean's unit spec, because mock users skip the filter building authorities.
- **SS23** — Give each guarded controller a matrix IT: caller kind (anonymous, each role, another tenant's member, a
  machine client) × endpoint → status, a refusal changing nothing, because one wrong-role test misses other caller
  kinds.
- **SS24** — Keep ITs that send a forged, expired, `alg:none`, wrong-key and wrong-`typ` token and expect 401, because
  JWT libraries have shipped critical flaws that accepted forged tokens.
- **SS25** — Give each public-path entry an IT proving the check that replaces the token refuses a bad caller, because
  on a public path that check is the only guard.

## When X, use Y

| the code | use | why |
|---|---|---|
| passes model output or tool arguments on | a schema check first; the permission check in code, not the prompt (SE10) | injected text can hijack the prompt, which is no security boundary |
| fetches a URL from config, a user or a remote document | one URL check that connects to the checked IP, on a client with redirects off, for every URL the remote side names (SE1) | a user-influenced URL can reach internal services |
| puts a value or a column name into SQL | a bound parameter for a value; an allowlist in code for an identifier (SE3) | input concatenated into SQL is an injection surface |
| opens a path a caller supplied | `toRealPath()` on the path and its base, then `Path.startsWith(base)`; an ownership check before a delete, move or overwrite (SE4) | `normalize()` lets a symlink escape the base |
| binds untrusted JSON | a fixed DTO with only the fields the caller may set; no default typing, no `Id.CLASS` (SE5) | payload-chosen classes let the attacker pick what is instantiated |
| binds HTML into an Angular template | `[innerHTML]` or `bypassSecurityTrust*` only for content the code controls (SE6) | user or model text bound raw into the page enables XSS |
| needs a key or a credential | the environment or a secret store (SEN2) | committed secrets survive in history |
| fails to decrypt a credential | a stopped call, never a cached, default or missing credential (SE2) | a fallback sends the call unauthenticated or with a cached credential |
| stores a human password | `DelegatingPasswordEncoder` with bcrypt (SS21) | adaptive hashing is for passwords, and it can be upgraded by its `{id}` prefix |
| stores a machine-generated secret of ≥128 bits | server-keyed HMAC-SHA-256 and `MessageDigest.isEqual` (SS21) | a slow hash checked per request makes a public endpoint a CPU sink |
| stores a credential it must send later | AES-GCM through `AesGcmBytesEncryptor`; masked in every response (SE7) | unauthenticated or weak ciphers expose it |
| creates an encryption, signing or HMAC key | a separate key for each purpose (SE7a) | a key shared across purposes lets output made for one pass as another |
| calls an LLM provider | a per-caller rate limit and quota before the call (SE8) | uncapped calls let one caller run up unbounded cost |
| writes a password, token, session id or key to a log | nothing: LG4 in [logging.md](../../obs/references/logging.md) | logs reach more readers than the secret should |
| configures `authorizeHttpRequests` | an explicit matcher per endpoint and `anyRequest().denyAll()` last (SS1) | a forgotten path stays open to any authenticated caller |
| permits a dispatch type | `dispatcherTypeMatchers(FORWARD, ERROR).permitAll()` (SS2) | a forward or error dispatch otherwise fails with an unexpected `AccessDeniedException` |
| adds a custom security `Filter` | the chain, with `FilterRegistrationBean.setEnabled(false)` (SS3) | a `Filter` bean otherwise runs twice, once out of order |
| receives an invalid, expired or wrong-type token | 401 at once, on public paths too (SS4) | a swallowed token error turns a bad credential into anonymous access |
| serves a named cross-origin client | `http.cors(…)` with an origin allowlist (SS5) | a reflected credentialed origin lets any site read a response |
| runs a service method from a worker, a scheduler or a listener | an authorization check in that method (SS16) | the filter chain and controller guards never see that call |
| guards a method that writes | a check before the write; collections filtered in the query (SS17) | `@PostAuthorize` runs after the write commits, so a denial undoes nothing |
| checks who owns a resource, or adds an auth step | an `AuthorizationManager`, a SpEL bean, a chain filter or a meta-annotation (SS26) | a hand-rolled check misses what the framework already checks |
| decides on membership or account status | a database read at decision time, not a token claim (SS6) | a removed or deactivated user keeps role access for the token's life |
| issues or verifies a token | its own `typ`, a pinned algorithm and an `exp` check (SS7) | without an explicit type a token made for one purpose passes as another |
| must carry a bearer credential to the server | a header, an HttpOnly cookie, or a single-use short-lived ticket (SS8) | a URL leaks into access logs, browser history and Referer |
| authenticates with a cookie | `HttpOnly; Secure; SameSite=Strict`, narrowest `Path`, and an `Origin` check (SS9) | stateless is no CSRF protection when a cookie authenticates |
| refreshes a token | a new refresh token each use; all revoked on password change or reset, deactivation, role change (SS10) | a stolen refresh token otherwise survives the victim's password reset |
| logs users in through an external IdP | Spring `oauth2Login` (SS11) | without its checks a replayed token or login CSRF succeeds |
| checks a password or a key | a failed-attempt limit per account (SEN1) | an unthrottled login or key check lets an attacker guess passwords online |
| returns an error body in production | a code and a fixed message; `include-message` and binding errors off (SS19) | `include-message: always` sends internal exception text to clients |
| changes a response header | the Spring Security defaults, tightened only (SS20) | each default header is a browser protection that disappears silently |
| tests a guard | a guard bean's unit spec may use `@WithMockUser` or `jwt()`; an IT logs in for real (SS22) | mock users skip the filter building authorities |
| tests a guarded controller | a matrix IT of caller kind × endpoint → status (SS23) | one wrong-role test misses other caller kinds |
| tests token validation | forged, expired, `alg:none`, wrong-key and wrong-`typ` tokens, each expecting 401 (SS24) | JWT libraries have shipped critical flaws that accepted forged tokens |
| adds a public-path entry | an IT where the replacement check refuses a bad caller (SS25) | on a public path that check is the only guard |

## Good / Bad

Every rule's approved pair: [examples/security.md](examples/security.md).

### SE1 — A URL not in code is fetched only after the URL check

**Bad**
```java
void deliver(final URI callback, final InvoiceEvent event) {
    restClient.post()
            .uri(callback)
            .body(event)
            .retrieve()
            .toBodilessEntity();
}
```
The subscriber chose the callback URL. It can name `169.254.169.254` or `localhost`, and the client follows redirects.

**Good**
```java
UrlCheck check(final URI url) {
    if (!Set.of("http", "https").contains(url.getScheme())) {
        return new UrlCheck.Refused("scheme not allowed");
    }
    final List<InetAddress> addresses = dns.resolveAll(url.getHost());
    return addresses.stream().anyMatch(PublicAddress::isPrivateOrReserved)
            ? new UrlCheck.Refused("private or reserved address")
            : new UrlCheck.Allowed(url, addresses);
}

Delivery deliver(final URI callback, final InvoiceEvent event) {
    return switch (check(callback)) {
        case UrlCheck.Refused refused -> new Delivery.Refused(refused.reason());
        case UrlCheck.Allowed allowed -> send(noRedirectClient, allowed.url(), allowed.addresses(), event);
    };
}
```
The check allows http or https only and refuses the URL when any resolved address is private or reserved. The call
then connects to those checked addresses, not a fresh lookup, on a client with redirects off.

### SS21 — Passwords via `DelegatingPasswordEncoder`; machine secrets via HMAC-SHA-256; never the encoder per request

**Bad**
```java
@Bean
PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
}

// runs on every request that carries an API key
Optional<ApiClient> authenticate(final PresentedKey key) {
    return clientRepository.findByKeyId(key.keyId())
            .filter(client -> passwordEncoder.matches(key.secret(), client.secretHash()));
}
```
The password encoder also checks API keys, so every API-key request pays a deliberately slow hash.

**Good**
```java
@Bean
PasswordEncoder passwordEncoder() {
    return PasswordEncoderFactories.createDelegatingPasswordEncoder();
}

// runs on every request that carries an API key
Optional<ApiClient> authenticate(final PresentedKey key) {
    final byte[] presented = keyMac.hmacSha256(key.secret());
    return clientRepository.findByKeyId(key.keyId())
            .filter(client -> MessageDigest.isEqual(presented, client.secretHmac()));
}
```
Passwords keep an adaptive hash that can be upgraded by its `{id}` prefix. A random key of 128 bits or more needs only
a server-keyed HMAC, compared in constant time.

## Decided edges

- **Skip when** a service method is called only from guarded controller handlers: it needs no check of its own
  (SS16). — **Do not skip when** a worker, a scheduler or a listener also calls it. — **Confidence** high
- **Skip when** the token's issuer is its only verifier: `iss` and `aud` may be left out (SS7). — **Do not skip
  when** a second party verifies the token: add `iss` and `aud`. — **Confidence** high

## Review checks

Walk every changed file that takes outside input, stores or checks a secret, configures the filter chain, or holds a
guard, a token or a security test. Each rule below gets a check.

- [ ] SE10 — Trace every model output and tool argument to its sink. Reaching SQL, a shell, `innerHTML` or a path
  without a schema check, or a permission enforced only by prompt text, is a finding.
- [ ] SE1 — For each outbound HTTP call (`grep -nE "\.uri\(|new URL\(|URI\.create"`), the URL is a literal in code or
  passed the URL check, on a client with redirects off. A URL check that allows a scheme other than http or https,
  checks only one resolved IP, misses a private or reserved range, or lets the client resolve the host again instead
  of connecting to the checked IP, is a finding. Any other URL is a finding.
- [ ] SE3 — String concatenation or `formatted(` that builds SQL from a variable is a finding, unless the variable
  is an identifier taken from an allowlist in code.
- [ ] SE4 — For each caller-supplied path, the deciding `startsWith(base)` runs on the `toRealPath()` result against
  a real base. A `normalize()`-only or `..` check, or a `String.startsWith` on paths, is a finding; a delete, move or
  overwrite with no check that the caller owns the target is a finding.
- [ ] SE5 — Untrusted JSON bound to anything but a fixed DTO is a finding: a `Map<String, Object>` past the adapter,
  a DTO field the caller may not set, default typing or a class-name type id
  (`grep -nE "DefaultTyping|Id\.(MINIMAL_)?CLASS"`). `@JsonTypeInfo(use = Id.NAME)` over a closed set is not a
  finding.
- [ ] SE6 — Each `[innerHTML]` or `bypassSecurityTrust` (`grep -rnE "innerHTML|bypassSecurityTrust"`) binds content
  the code controls. User or model text is a finding.
- [ ] SEN2 — `grep -niE '(password|secret|api[-_]?key|token)[a-z_]*"?\s*[:=]\s*"?[A-Za-z0-9+/_-]{8,}'` in code and
  committed config. A key or credential written as a literal, not read from the environment or a secret store
  (`${…}`), is a finding.
- [ ] SE2 — Open each decrypt call. A failure that continues with no credential, a cached one or a default one is
  a finding.
- [ ] SS21 — Passwords go through `DelegatingPasswordEncoder` with bcrypt cost ≥10. Machine secrets go through
  server-keyed HMAC-SHA-256 and a constant-time compare. A password encoder on a machine secret, or `equals` on a
  secret, is a finding.
- [ ] SE7 — Each stored credential the code sends later is encrypted with AES-GCM and masked in every response. ECB,
  MD5, SHA-1 or DES on a secret (`grep -nE 'ECB|MD5|SHA-?1\b|"DES|getInstance\("AES"\)'`; bare `"AES"` means ECB in
  the JDK) is a finding.
- [ ] SE7a — One key, or one secret property, used for two of credential encryption, token signing and HMAC, or for
  two kinds of token, is a finding.
- [ ] SE8 — Each LLM provider call path passes a per-caller rate limit and quota before the call. A path that skips
  it, or a limit shared by every caller, is a finding.
- [ ] SS1 — The last matcher in `authorizeHttpRequests` is `anyRequest().denyAll()`. A new endpoint matched only by
  the last line is a finding.
- [ ] SS16 — For each service method a worker, scheduler or listener calls
  (`grep -nE "@Scheduled|@[A-Za-z]*Listener\b|implements .*Listener"`), find its own authorization check. None is a
  finding.
- [ ] SS2 — `grep -n "dispatcherTypeMatchers"`. A matcher that permits `REQUEST` is a finding, and so is a chain that
  forwards to views or renders Spring Boot error pages with no `FORWARD` and `ERROR` permit.
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
- [ ] SS8 — A token or secret read from a query parameter or path variable
  (`grep -nE "getParameter\(\"token|\?token="`) is a finding.
- [ ] SS9 — Each credential cookie (`grep -n "ResponseCookie"`) sets `HttpOnly`, `Secure`, `SameSite=Strict` and a
  narrow `Path`, and its endpoint checks `Origin`. A missing one is a finding.
- [ ] SS10 — Each refresh issues a new token and revokes the old one. A password change or reset, deactivation or role
  change that leaves refresh tokens alive is a finding.
- [ ] SS11 — An IdP login outside `oauth2Login`, or one that skips the signature, `iss`, `aud`, `exp`, `nonce` or
  browser-bound `state` check, is a finding.
- [ ] SEN1 — Each login or key-check path counts failed attempts per account and throttles after a limit. A path with
  no limit, or one counted only per IP address, is a finding.
- [ ] SS19 — `include-message` or `include-binding-errors` set to anything but `never` in production configuration is
  a finding.
- [ ] SS20 — `grep -nE "headers\(|frameOptions|httpStrictTransportSecurity|contentSecurityPolicy"` and read each. A
  disabled or removed default header, or a CSP, HSTS or framing setting looser than the default, is a finding.
- [ ] SS22 — Each security IT gets its token from the real login. `@WithMockUser` or `jwt()` in an IT
  (`grep -rnE "@WithMockUser|jwt\(\)"`) is a finding.
- [ ] SS23 — Each guarded controller's IT covers anonymous, each role, another tenant's member and a machine client
  on each endpoint, and shows a refusal changes nothing. A missing caller kind is a finding.
- [ ] SS24 — The token ITs send forged, expired, `alg:none`, wrong-key and wrong-`typ` tokens and expect 401. A
  missing case is a finding.
- [ ] SS25 — Each new public-path entry has an IT where a bad caller is refused by the replacement check. None is a
  finding.
