Why 2x? The loop uses `i % 50`, so only 50 keys: after the first 50 calls every lookup is a cache hit. Ask for a realistic key spread and the hit rate.
