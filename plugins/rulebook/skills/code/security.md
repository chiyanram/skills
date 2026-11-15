# Security notes

Read this when the change takes outside input, stores or checks a secret, or touches a token, a guard, the security
filter chain or a security test. The general rules are in [SKILL.md](SKILL.md).

The public-path list is the set of paths the filter chain permits without a token. A guard is an authorization check
on a handler, such as `@PreAuthorize`.

## Outside input

- Treat model output and tool arguments as untrusted. Check them against a schema before they reach SQL, a shell,
  `innerHTML` or a path, and enforce permissions in code, because injected text can take over the prompt, and a prompt
  is no security boundary.
- Fetch a URL that is not a literal in code only after one check: the scheme is http or https, every resolved address
  is outside private and reserved ranges, and the call connects to those checked addresses on a client with redirects
  off. Run the check again for each URL the remote side names. A user-influenced URL can otherwise reach internal
  services, and a fresh lookup or a followed redirect skips the check.
- Take a dynamic SQL identifier, such as a sort column, from an allowlist defined in code, because a bound parameter
  cannot hold an identifier and a concatenated one is an injection.
- Resolve a caller-supplied path and its base with `toRealPath()`, then check `Path.startsWith(base)`, never
  `String.startsWith`. Before a delete, move or overwrite, also check from server state that the caller owns the
  target. `normalize()` does not read the file system, so a symlink inside the base escapes it.
- Bind untrusted JSON to a fixed DTO that holds only the fields the caller may set. Use no default typing and no
  class-name type id (`Id.CLASS`, `Id.MINIMAL_CLASS`), because then the payload picks the class to build.
  `@JsonTypeInfo(use = Id.NAME)` over a closed set is safe.
- Use `[innerHTML]` or `bypassSecurityTrust*` only for content the code controls, never user or model text, because
  raw text bound into the page is XSS.

**Bad**: the member chose the callback URL. It can name `169.254.169.254` or `localhost`, and the client follows
redirects.
```java
void deliver(URI callback, LoanEvent event) {
    restClient.post().uri(callback).body(event).retrieve().toBodilessEntity();
}
```
**Good**: one check, then a call to the checked addresses, not a fresh lookup.
```java
UrlCheck check(URI url) {
    if (!Set.of("http", "https").contains(url.getScheme())) {
        return new UrlCheck.Refused("scheme not allowed");
    }
    List<InetAddress> addresses = dns.resolveAll(url.getHost());
    return addresses.stream().anyMatch(PublicAddress::isPrivateOrReserved)
            ? new UrlCheck.Refused("private or reserved address")
            : new UrlCheck.Allowed(url, addresses);
}

Delivery deliver(URI callback, LoanEvent event) {
    return switch (check(callback)) {
        case UrlCheck.Refused refused -> new Delivery.Refused(refused.reason());
        case UrlCheck.Allowed allowed -> send(noRedirectClient, allowed.url(), allowed.addresses(), event);
    };
}
```

**Bad**: `normalize()` passes a symlink to `/etc`, and nothing proves the member owns the file.
```java
void deleteExport(Path exportRoot, String requested) {
    Path target = exportRoot.resolve(requested).normalize();
    if (!target.startsWith(exportRoot)) throw new ExportException(ErrorCode.PATH_OUTSIDE_ROOT);
    exports.delete(target);
}
```
**Good**: the check runs on the real path, below the root and never the root itself, and the owner comes from server
state.
```java
Deletion deleteExport(Path realRoot, String requested, MemberId caller) {
    Path target;
    try {
        target = realRoot.resolve(requested).toRealPath();
    } catch (IOException _) {
        return new Deletion.NotFound(requested);
    }
    if (!target.startsWith(realRoot) || target.equals(realRoot)) {
        return new Deletion.Refused(target, "outside the export root");
    }
    if (!exportIndex.isOwnedBy(target, caller)) {
        return new Deletion.Refused(target, "owner not proven");
    }
    return exports.delete(target);
}
```

## Secrets

- Stop the call when decryption of a credential fails. Never fall back to no credential, a cached one or a default,
  because the call then goes out unauthenticated or as someone else.
- Hash a human password with `DelegatingPasswordEncoder` (bcrypt cost 10 or more), so its `{id}` prefix lets you
  upgrade the hash later. Hash a machine-generated secret of 128 bits or more with a server-keyed HMAC-SHA-256 and
  compare with `MessageDigest.isEqual`, never `equals`. A slow password hash checked on every request makes a public
  endpoint a CPU sink.
- Encrypt a stored credential the code must send later with AES-GCM (`AesGcmBytesEncryptor`), and mask it in every
  response. Never use ECB, MD5, SHA-1 or DES on a secret. A bare `Cipher.getInstance("AES")` is ECB in the JDK.
- Give each key one purpose: the credential-encryption key, each token-signing key and each HMAC key are separate
  secrets, because a shared key lets output made for one purpose pass as another.
- Put every call to a model provider behind a per-caller rate limit and quota, because one caller can otherwise run
  up unbounded cost and use up the shared provider quota.
- Rate-limit failed login and key checks per account, not only per IP address, because an attacker spreads guesses
  across addresses.

**Bad**: the password encoder also checks API keys, so every API-key request pays a slow hash.
```java
@Bean PasswordEncoder passwordEncoder() { return new BCryptPasswordEncoder(12); }

Optional<ApiClient> authenticate(PresentedKey key) {   // runs on every request
    return clients.findByKeyId(key.keyId())
            .filter(c -> passwordEncoder.matches(key.secret(), c.secretHash()));
}
```
**Good**
```java
@Bean PasswordEncoder passwordEncoder() { return PasswordEncoderFactories.createDelegatingPasswordEncoder(); }

Optional<ApiClient> authenticate(PresentedKey key) {   // runs on every request
    byte[] presented = keyMac.hmacSha256(key.secret());
    return clients.findByKeyId(key.keyId())
            .filter(c -> MessageDigest.isEqual(presented, c.secretHmac()));
}
```

## The filter chain

- End `authorizeHttpRequests` with `anyRequest().denyAll()`, and give every endpoint a public-path entry or its own
  `authenticated()` or role matcher, because a forgotten path otherwise stays open to any authenticated caller.
- Permit `dispatcherTypeMatchers(FORWARD, ERROR)`, never `REQUEST`. Spring Security authorizes every dispatch, so a
  forward or an error page otherwise fails with an `AccessDeniedException`.
- Add a custom security `Filter` to the chain and turn off its servlet registration with
  `FilterRegistrationBean.setEnabled(false)`, because a `Filter` bean otherwise runs twice, once out of order.
- Answer an `Authorization` header that holds an invalid, expired or wrong-type token with 401 at once, on public
  paths too, because a swallowed token error turns a bad credential into anonymous access.
- Configure CORS only for a named cross-origin client, through `http.cors(…)` with an origin allowlist. Never use `*`
  or `allowedOriginPatterns("*")` with credentials, because any site can then read a credentialed response.
- Keep every default security response header. Tighten CSP, HSTS or framing, never remove or loosen one, because a
  lost header removes a browser protection with no error.

## Guards

- Give a service method that a worker, scheduler or listener calls its own authorization check, because the filter
  chain and controller guards never see that call. A method called only from guarded handlers needs none.
- Check before a write. Filter a collection in the query, never in memory after it. Never put `@PostAuthorize` or
  `@PostFilter` on a method that writes, because it runs after the write commits, so a denial undoes nothing.
- Build an ownership check or a new auth step from Spring Security's own parts (`AuthorizationManager`, a SpEL bean,
  a chain filter, a meta-annotation) after you read their source, because a hand-rolled check misses what the
  framework already checks.
- Read tenant membership and account status from the database at decision time, never from a token claim, and keep
  access tokens short-lived, because a removed or deactivated user otherwise keeps access for the token's life.

## Tokens and sessions

- Give each token purpose its own `typ`. Verification pins the algorithm and checks `typ` and `exp`, because a token
  made for one purpose otherwise passes as another. Add `iss` and `aud` when a party other than the issuer verifies
  the token.
- Carry an access token, refresh token or long-lived secret in a header, an HttpOnly cookie or a single-use,
  short-lived ticket, never in a URL, because a URL leaks into access logs, browser history and `Referer`.
- Set a credential cookie `HttpOnly; Secure; SameSite=Strict` with the narrowest `Path`, and refuse a cross-site
  `Origin` on its endpoints, because a stateless API is still open to CSRF when a cookie authenticates.
- Issue a new refresh token on every use and revoke the old one. Revoke all of a user's refresh tokens on a password
  change or reset, a deactivation and a role change, because a stolen refresh token otherwise outlives the reset.
- Accept an outside identity provider's login only through `oauth2Login`, with the signature, `iss`, `aud`, `exp` and
  `nonce` checked and `state` bound to the browser, because without them a replayed token or a login CSRF succeeds.

## Security tests

- Authenticate a security integration test through the real login and filter chain (see the `testing` skill's stack
  notes). Use `@WithMockUser` or `jwt()` only in a guard bean's unit spec, because a mock user skips the filter that
  builds the authorities.
- Give each guarded controller a matrix test: each caller kind (anonymous, each role, another tenant's member, a
  machine client) against each endpoint, with the expected status, and show that a refusal changes nothing. One
  wrong-role test misses the other caller kinds.
- Keep tests that send a forged, an expired, an `alg:none`, a wrong-key and a wrong-`typ` token, each expecting 401,
  because token libraries have shipped flaws that accepted forged tokens.
- Give each public-path entry a test that shows the check that replaces the token refuses a bad caller, because on a
  public path that check is the only guard.
