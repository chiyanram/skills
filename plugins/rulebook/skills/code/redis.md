# Redis

Read this when the change reads or writes Redis, configures a Redis cache or connection, or names a key. Streams
consumers and pub/sub are in [async-jobs.md](async-jobs.md); retries are in [concurrency.md](concurrency.md).

## Commands

- Never run `KEYS`. Never run `SMEMBERS`, `HGETALL` or `LRANGE 0 -1` on a collection that grows with users or data.
  Iterate with `SCAN`, `SSCAN`, `HSCAN` or `ZSCAN` and a `COUNT`, or page with a bounded `LRANGE`, because one O(N)
  command blocks every client. `HGETALL` on a small hash that is bounded by design is fine.

**Bad**
```java
void evictLoans(final MemberId member) {
    redis.delete(redis.keys("library:loan:" + member.value() + ":*"));
}
```
**Good**: `SCAN` returns a few hundred keys per call, so other clients run between the calls.
```java
void evictLoans(final MemberId member) {
    final var options = ScanOptions.scanOptions()
            .match("library:loan:" + member.value() + ":*")
            .count(500)
            .build();
    try (final Cursor<String> cursor = redis.scan(options)) {
        cursor.forEachRemaining(redis::delete);
    }
}
```

## Cache entries

- Give every cache entry a TTL: `entryTtl` on the `RedisCacheConfiguration`, or `SET … EX`. Add random jitter to
  entries written together. An entry without a TTL stays until eviction drops what you need, and entries that expire
  in the same second block the server while it deletes them. A key that is a record with its own lifetime, such as a
  stream or a rate-limit window, follows that lifetime instead.
- Build the Spring `RedisCacheWriter` with `BatchStrategies.scan(…)`, because the default writer clears a cache with
  `KEYS`.

**Bad**: the default configuration has no TTL.
```java
return RedisCacheManager.builder(writer).build();
```
**Good**: `JitteredTtl` is a `TtlFunction` that returns 10 minutes plus up to 2 random minutes.
```java
final var defaults = RedisCacheConfiguration.defaultCacheConfig()
        .entryTtl(new JitteredTtl(Duration.ofMinutes(10), Duration.ofMinutes(2)));
final var writer = RedisCacheWriter.nonLockingRedisCacheWriter(connections, BatchStrategies.scan(1000));
return RedisCacheManager.builder(writer).cacheDefaults(defaults).build();
```

## What Redis holds

- Keep the system of record outside Redis. Use Redis as a cache or a queue in front of it, because a failover can
  promote a replica that lacks recent writes.
- Let the service start with Redis down and degrade the features that need it, because a hard boot dependency turns
  a Redis outage into a full outage.

## Connections and failover

- With Lettuce, share one multiplexed connection. Give `BLPOP`, `XREADGROUP … BLOCK` and other blocking reads their
  own connection, because a blocking command holds the shared connection for its whole wait. With a pooling client
  (Jedis), use a pool with a fixed maximum and an acquire timeout. Never open a connection per call.
- Reconnect with jittered backoff, and retry an idempotent command on `READONLY` or a connection error, because every
  client that reconnects at once floods the new primary. Prove it with a Toxiproxy test that cuts Redis.

## Key names

- Name keys in lowercase, colon-separated, with a service or tenant prefix: `<service>:<entity>:<id>[:<part>]`, such
  as `library:loan:42:fees`. One scheme lets scans, ACLs and cleanup target a prefix.
