# Security — Good / Bad examples

Every approved Good/Bad pair for the security rules, one per rule that has one. The rules, the decision table and the
review checks are in [`../security.md`](../security.md). Each pair is in one neutral domain (invoices and payments).

Contents: SE1 · SE4 · SE5 · SS21

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

### SE4 — Resolve a caller-supplied path with `toRealPath()`, check `Path.startsWith(base)`, prove ownership first

**Bad**
```java
void deleteExport(final Path exportRoot, final String requested) {
    final Path target = exportRoot.resolve(requested).normalize();
    if (!target.startsWith(exportRoot)) {
        throw new ExportException(ErrorCode.PATH_OUTSIDE_ROOT);
    }
    exports.delete(target);
}
```
`normalize()` does not read the file system. A symlink inside the root that points at `/etc` passes the check, and
nothing proves the caller owns the file.

**Good**
```java
Deletion deleteExport(final Path realRoot, final String requested, final AccountId caller) {
    final Path target;
    try {
        target = realRoot.resolve(requested).toRealPath();
    } catch (final IOException _) {
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
The check runs on the real path with symlinks followed. The target sits below the root, never the root itself, and
its owner comes from server state read before the delete.

### SE5 — Untrusted JSON binds to a fixed DTO, with no default typing

**Bad**
```java
private final JsonMapper mapper = JsonMapper.builder()
        .activateDefaultTyping(LaissezFaireSubTypeValidator.instance)
        .build();

PaymentReply parseReply(final String json) {
    final Map<String, Object> body = mapper.readValue(json, Map.class);
    return new PaymentReply(
            (String) body.get("payment_id"),
            (String) body.get("status"));
}
```
Default typing lets the payload name the class to build. The untyped map then spreads casts and unchecked keys into
the caller.

**Good**
```java
private final JsonMapper mapper = JsonMapper.builder().build();

PaymentReply parseReply(final String json) {
    return mapper.readValue(json, PaymentReply.class);
}

public record PaymentReply(
        @JsonProperty("payment_id") String paymentId,
        @JsonProperty("status") PaymentStatus status) {
}
```
The gateway reply binds to one concrete record with no default typing. The status is an enum, so an unknown value
fails at the boundary.

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
