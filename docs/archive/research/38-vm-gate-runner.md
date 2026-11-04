# R29 · The VM as gate runner — where the hour goes (#62)

Measured on the VM by the fleet developer, 2026-10-02 15:45 UTC, during Verifier job `80f3d2`; timings from the last
completed job `133306-d28641` (#622 @54457bf1, PASS, 60m45s wall).

## Machine
8 vCPU · 23 GB RAM (10 GB available under load) · swap 7 GB unused · rootless **podman** (no /var/lib/docker), cgroup v2,
overlay storage · `oom_kill` 0 in the developer cgroup.
Top RSS: Verifier Gradle + Testcontainers ~2.6 + 2.2 + 1.1 GB · a container JVM 0.77 GB · developer Gradle daemon
0.71 GB · each `claude` ~0.4 GB. Gradle `-Xmx4g`, `parallel=true`, caching on; 2 daemons (developer + verifier).

## Where the 61 minutes go
| phase | time | share | note |
|---|---|---|---|
| smoke FULL (795 tests, 2 workers) | 24m33 | 40 % | LLM specs on **Ollama qwen3:1.7b, CPU-only**; scripted specs on fake-llm (#576) |
| build + unit + ITs + checks (one Gradle run) | 21m40 | 36 % | one IT task (790 tests) alone 18m50 — serial (`maxParallelForks = 1`); Testcontainers reuse OFF |
| deploy (3 images 3m26 + start + healthy) | ~10m | 16 % | ~6.5 min from start to healthy |
| UI build + Playwright unit | 2m33 | 4 % | |

## Top causes
1. **Smoke full is the biggest single phase**, and part of it runs a real LLM on CPU. With 8 cores and 10 GB free, 2
   Playwright workers is conservative.
2. **One serial IT task (790 tests) is the critical path of the Gradle run** — 18m50 of 21m40. Serial by design
   (ADR-0009, shared containers); reuse is off.
3. **Deploy spends ~6.5 min waiting for healthy** after the images are built.

Not the cause: memory. 10 GB free and zero OOM kills under a running job. The agents' "OOM on make verify" is a developer
running a second `-Xmx4g` Gradle + containers beside the Verifier — the case the developer minimum (#35 Q26) removes.
Explains the env failures: rootless podman needs `DOCKER_HOST` pointed at the podman socket and Testcontainers' Ryuk
config — machine-file material (ND-15).

## Still missing
Laptop timings for the same phases (`make verify FRESH=1`, `make smoke FULL=1`) — needed to tell "VM is slower" from
"the gate is this big". Per-module IT times (log has no timestamps).

## Levers (for the operator to decide)
- Gate smoke on the scripted model only; real-Ollama specs move to a separate tier (nightly or on demand).
- Playwright workers 2 → 4 on the runner.
- Biggest IT module: split the task, or a fork-per-database scheme (a change to ADR-0009 — needs its own decision).
- Deploy: find what the 6.5 min healthy wait is (healthcheck intervals, Ollama warm-up).
- Timestamps per phase in the Verifier log.
