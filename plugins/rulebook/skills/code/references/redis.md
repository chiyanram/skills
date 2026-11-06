# Redis

How code uses Redis safely: which commands it may run, how its keys expire and are named, how it connects and
survives failover, and what Redis may hold. Read it when you write or review code that reads or writes Redis, a
Redis cache, a Redis connection setup, or a key name.

Contents: Rules · When X, use Y · Good / Bad (RD1, RD2) · Decided edges · Review checks

Redis Streams consumers and pub/sub are MS7–MS12 in `messaging.md`. Retries on Redis calls follow CC8 and CC13 in
`concurrency.md`.

## Rules

- **RD1** — Never run `KEYS`, or `SMEMBERS`, `HGETALL` or `LRANGE 0 -1` on a large collection; iterate with `SCAN`,
  `SSCAN` or `HSCAN` and a `COUNT`, because one O(N) command blocks every other client.
- **RD2** — Give every cache entry a TTL, with jitter for entries written together, because entries without one fill
  memory until eviction drops what you need, and mass expiry blocks the server.
- **RD3** — Keep the system of record outside Redis, and let the service start and degrade without it, because a
  failover or restart can lose recent writes.
- **RD4** — Share one multiplexed Lettuce connection or a bounded pool, never a connection per call, and give blocking
  reads their own connection, because a blocking command stalls every request that shares it.
- **RD5** — Reconnect with jittered backoff, retry `READONLY` and connection errors during failover, and test a forced
  failover, because clients that mishandle failover take the service down.
- **RD6** — Name keys in lowercase, colon-separated, with a service or tenant prefix (`orders:42:lines`), because
  mixed schemes make scans, ACLs and cleanup per prefix impossible.

## When X, use Y

| the code | use | why |
|---|---|---|
| iterates keys or a large collection | `SCAN`, `SSCAN`, `HSCAN` or `ZSCAN` with a `COUNT`, or a bounded `LRANGE` page (RD1) | an O(N) command runs alone on the server and blocks every client |
| clears a Spring cache | a `RedisCacheWriter` built with `BatchStrategies.scan(…)` (RD1) | the default writer clears with `KEYS` |
| writes a cache entry | `entryTtl` on the `RedisCacheConfiguration`, or `SET … EX` (RD2) | an entry without a TTL stays until eviction picks it |
| writes many entries at the same moment | a TTL with random jitter (RD2) | entries that expire in the same second block the server while it deletes them |
| needs data that must survive | the database as the system of record, Redis as a cache or a queue in front of it (RD3) | a failover can promote a replica that lacks recent writes |
| starts with Redis down | a start that succeeds, with the features that need Redis degraded (RD3) | a hard boot dependency turns a Redis outage into a full outage |
| connects with Lettuce | one shared, multiplexed connection; a separate connection for `BLPOP` or `XREADGROUP … BLOCK` (RD4) | a blocking command holds the shared connection for its whole wait |
| connects with a pooling client (Jedis) | a pool with a fixed maximum (RD4) | a connection per call costs a handshake each time and floods the server |
| meets a failover | jittered reconnect backoff, a retry on `READONLY`, and an IT that forces a failover (RD5) | every client reconnecting at once floods the new primary |
| names a key | `<service>:<entity>:<id>[:<part>]` in lowercase (RD6) | one scheme lets scans, ACLs and cleanup target a prefix |

## Good / Bad

### RD1 — A cursor, never `KEYS`

**Bad**
```java
void evictSessions(final UserId user) {
    final var keys = redis.keys("sessions:" + user.value() + ":*");
    redis.delete(keys);
}
```
`KEYS` walks the whole keyspace while every other client waits.

**Good**
```java
void evictSessions(final UserId user) {
    final var options = ScanOptions.scanOptions()
            .match("sessions:" + user.value() + ":*")
            .count(500)
            .build();
    try (final var cursor = redis.scan(options)) {
        cursor.forEachRemaining(redis::delete);
    }
}
```
`SCAN` returns the keys a few hundred at a time, so other clients run between the calls.

### RD2 — A TTL on every cache entry

**Bad**
```java
@Bean
RedisCacheManager cacheManager(final RedisConnectionFactory connections) {
    return RedisCacheManager.create(connections);
}
```
The default configuration has no TTL, so every entry stays until memory runs out and eviction starts.

**Good**
```java
@Bean
RedisCacheManager cacheManager(final RedisConnectionFactory connections) {
    final var defaults = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(new JitteredTtl(Duration.ofMinutes(10), Duration.ofMinutes(2)));
    return RedisCacheManager.builder(connections)
            .cacheDefaults(defaults)
            .build();
}
```
`JitteredTtl` is a `TtlFunction` that returns 10 minutes plus up to 2 random minutes, so entries cached together do not
expire together.

## Decided edges

- **Skip when** the collection is small and bounded by design, such as the fields of one small hash: `HGETALL` is fine
  (RD1). — **Do not skip when** the collection grows with users or data. — **Confidence** high
- **Skip when** the key is not a cache entry but a record that must last, such as a stream or a rate-limit window
  with its own expiry: it follows its own rule, MS10 or the window length (RD2). — **Do not skip when** the value is a
  copy of data held elsewhere. — **Confidence** high

## Review checks

Walk every Redis call, cache configuration, connection factory and key name added or changed in the diff.

- [ ] RD1 — `grep -rnE '\.keys\(|"KEYS|members\(|entries\(|\.range\([^,]+, *0, *-1\)|LRANGE.*0 -1'`. A hit on a
  collection that can grow is a finding, and so is a `RedisCacheWriter` with no `BatchStrategies.scan`.
- [ ] RD2 — For each cache configuration and each `set` of a cache entry, find a TTL. A missing TTL is a finding, and
  so is one fixed TTL for entries written in a batch.
- [ ] RD3 — For each value written to Redis, find its copy in the system of record. A value held only in Redis that
  must survive a restart is a finding, and so is a start that fails when Redis is down.
- [ ] RD4 — For each `RedisConnectionFactory` and client, a connection opened per call, a pool with no maximum, or a
  blocking read on the shared connection is a finding.
- [ ] RD5 — Find the reconnect backoff with jitter and an IT that forces a failover (a Testcontainers primary stopped
  mid-test). Either one missing is a finding.
- [ ] RD6 — For each new key pattern, a name that is not lowercase and colon-separated with a service or tenant
  prefix is a finding.
