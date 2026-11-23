---
approved: operator
---

Not shown. One run each on a laptop cannot tell a 2x change from noise: ask for repeated runs of each version (for example five alternating runs, or several JMH forks), with a spread such as the range or an error bar. Ask why the number is 2x: the benchmark looks up only 50 distinct keys, so after the first 50 every call is a cache hit, and the result says more about the key set than about real traffic. Ask for a run with a realistic key spread and the hit rate.
