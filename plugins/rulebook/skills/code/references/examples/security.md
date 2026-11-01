# Security — Good / Bad examples

Every approved Good/Bad pair for the security rules, one per rule that has one. The rules, the decision table and the
review checks are in [`../security.md`](../security.md). Each pair is in one neutral domain (orders and billing).

Contents: SE1 · SE4 · SE5 · SS21

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
The discovery document was fetched through the URL check, but the endpoint it returned is called unchecked, carrying the secret.

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
Every URL the remote side names passes the same check, on a client with redirects off. (Real evidence: ledger row SE1.)

### SE4 — Resolve a user-supplied path with `toRealPath()`, then check `startsWith(base)`

**Bad** (neutral)
```java
public Path locate(final Path basePath, final String relativePath) {
    if (relativePath.contains("..")) {
        throw new OrderException(ErrorCode.PDF_PATH_BLOCKED, relativePath);
    }
    final Path base = basePath.toAbsolutePath().normalize();
    final Path resolved = base.resolve(relativePath).normalize();
    if (!resolved.startsWith(base)) {
        throw new OrderException(ErrorCode.PDF_PATH_BLOCKED, relativePath);
    }
    return resolved;
}
```
Both checks are lexical; a symlink inside the base that points at `/etc` passes them.

**Good** (neutral)
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
The deciding check runs on the real path with symlinks followed, and the caller opens exactly the path that was checked. (Real evidence: ledger row SE4.)

### SE5 — Untrusted JSON binds to a fixed record; no `Map<String,Object>` past the adapter

**Bad** (neutral)
```java
final Map<String, Object> body = noRedirectRestClient.get()
        .uri(checked.value())
        .retrieve()
        .body(Map.class);
if (body == null) {
    throw new IllegalStateException("Empty gateway discovery from " + checked.value());
}
return new GatewayDiscovery(
        (String) body.get("charge_endpoint"),
        (String) body.get("refund_endpoint"));
// …
public record GatewayDiscovery(String chargeEndpoint, String refundEndpoint) {}
```
A typed record exists, yet the reply is cast field by field; a missing key becomes a `null` URL that fails three calls later.

**Good** (neutral)
```java
final GatewayDiscovery discovery = noRedirectRestClient.get()
        .uri(checked.value())
        .retrieve()
        .body(GatewayDiscovery.class);
return Optional.ofNullable(discovery)
        .orElseThrow(() -> new OrderException(ErrorCode.GATEWAY_DISCOVERY_FAILED));
// …
public record GatewayDiscovery(
        @JsonProperty("charge_endpoint") String chargeEndpoint,
        @JsonProperty("refund_endpoint") String refundEndpoint) {
    public GatewayDiscovery {
        requireUrls(chargeEndpoint, refundEndpoint);
    }
}
```
The reply binds straight to the record, and its constructor refuses a bad document at the boundary with one error. (Real evidence: ledger row SE5.)

### SS21 — Passwords via `DelegatingPasswordEncoder`; machine secrets via HMAC-SHA-256; never the encoder per request

**Bad** (neutral)
```java
@Bean
public PasswordEncoder passwordEncoder() {
    return new BCryptPasswordEncoder(12);
}
// ApiKeyService — runs on every request that carries an API key
public Optional<ApiKeyEntity> authenticateKey(final ApiKeyCandidate candidate) {
    return apiKeyRepository.findByKeyPrefix(candidate.prefix()).stream()
            .filter(ApiKeyEntity::isValid)
            .filter(key -> passwordEncoder.matches(candidate.rawKey(), key.getKeyHash()))
            .findFirst();
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
Passwords keep an adaptive hash; a random 128-bit key needs only a keyed HMAC, compared in constant time. (Real evidence: ledger row SS21.)
