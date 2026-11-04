# 67 — Host config: what is typed vs derived, and one source for the toolchain (map #9, G32)

Decision G32 (not yet opened). Read 64a–64e first. Researched 2026-10-17. Quotes ≤15 words.
Refs at `origin/main` in `.scratch/one-rulebook/refs/<dir>` unless marked. Ours: agent-fleet `@8738986`,
agent-platform main checkout `@4cf7e69c`. No stated reason → "no stated reason" + INFERENCE.

## Our state (verified)

```
JAVA VERSION — five places, two already disagree on patch
  agent-platform/.sdkmanrc:3                          java=25.0.3-tem        (host devs, doctor reads it)
  agent-platform/build-logic/.../aruvii.java-conventions.gradle.kts:9   toolchain languageVersion 25
  agent-platform/settings.gradle.kts:10               foojay resolver  -> Gradle DOWNLOADS JDK 25 if absent
  agent-platform/Dockerfile:11,104,120                gradle:9.7.1-jdk25 · temurin:25-jre (product image)
  agent-fleet/.devcontainer/Dockerfile:16             temurin:25.0.4.1_1-jdk  <-- worker image, 25.0.4 ≠ 25.0.3
  agent-fleet/templates/machine.env.example:15        JAVA_HOME=/usr/lib/jvm/java-25-openjdk-amd64 (typed)
```

| fact in machine.env | typed today | actually derivable from | who needs it |
|---|---|---|---|
| `JAVA_HOME` | yes, `machine.env.example:15`, REQUIRED `machine_env.py:24` | image `ENV` (`.devcontainer/Dockerfile:34`); host only for fleet-runner's shell executor (`setup-gate-runner.sh:157`) | runner gate on host |
| `DOCKER_HOST` | yes, uid by hand (`:18-19`) | `id -u` — `worker-container:56` **already derives it**; `fleet-zones:332` already knows each zone's uid | every zone |
| `LANG`/`LC_ALL` | yes (`:24-25`) | constant `C.UTF-8`; image sets it (`.devcontainer/Dockerfile:32-33`) | all |
| `FLEET_PORT_BASE` | yes (`:28`); overlap checked after (`setup-gate-runner.sh:113-133`) | Verifier already assigns `PORT_START+100N` (`setup-verifier.sh:113`) | runner, worker |
| `FLEET_PROJECT_REPO` | yes (`docs/install.md:57`) | zone home + fixed name, made by fleet-zones | worker |
| `FLEET_OPERATOR_LOGIN`, `FLEET_CLAIM_LOGIN`, notifier | yes | **nothing** — a trust choice | coord |

Doctor: `scripts/doctor.sh:122-125` reads the major from `.sdkmanrc`; `:159-165` accepts major-only, newer passes
("failing someone for being one patch ahead would be actively wrong"); fix hint `sdk env install` (`:458`).
No `.tool-versions`, `mise.toml`, `.java-version`, or `gradle/gradle-daemon-jvm.properties` in agent-platform.

## References

**rameezk-forge** (`57f3619`) — Nix everywhere; host facts in one typed file, toolchain owned by the repo.
- Config has **three tiers**: no sane default (SSH keys, hostname) · defaulted-but-overridable (locale, timezone,
  admin user) · internal wiring "not worth exposing" (`docs/adr/0002-…:11`). Real file gitignored, example committed (`:19,24`).
  Why: forge is reusable, so "nothing person- or deployment-specific may be a baked-in constant" (`:9`).
- Defaults live in code, not the example: `infra/lib/load-config.nix:4-14` (`locale = "en_US.UTF-8"` etc.), merged `defaults // raw`.
- Runtime config is a **typed** NixOS module, so "a malformed worker is a Nix evaluation error" not a silent
  runtime failure (`docs/adr/0005-…:24`).
- **Toolchain = the repo's flake devShell**, not forge's toolset (`docs/adr/0027-…:15,22`). Why: a per-forge toolset
  "duplicates the repository's devShell and drifts from it" (`:14`). Entered by the runner via `nix print-dev-env`
  *before* the agent, so "a broken devShell fails the dispatch before pi starts" (`:19`).
- ADR-0073: credential-carrying tools (forge's `gh`) go **before** the devShell on PATH; repo's dev shell shipped its own
  `gh` and a PR "failed as unanswered" (`docs/adr/0073-…:11,20`). Rule: platform owns credential tools, repo owns stack tools.
- ADR-0057: empty per-run `CLAUDE_CONFIG_DIR`, discarded after, so "no host state or earlier run reaches it" (`:20,24`).
- ADR-0058: a login shell wiped the runner-built `PATH`/`LANG`; fix marks env as already set, and a VM test probes
  it (`:9,18,22`). Lesson: environment the platform builds must survive the shell the harness spawns — test it.

**kunchenguid-firstmate** (`5f2b81b`) — config/ = gitignored local choices; detect only what is evidence, ask for trust.
- `config/firstmate-role`: "Write the primary home's file by hand; firstmate never grants itself a role" (`docs/configuration.md:591`);
  malformed → fails closed "rather than guessing" (`:593`); "never inferred from GitHub identity, … remotes, … CI" (`:596`).
- `config/project-capacity`: optional; malformed file refuses every spawn "rather than guessing the intended limit" (`:1166`).
  Why: surplus workers burnt tokens waiting on a machine resource (64b, issue #4237).
- `config/crew-exclude-tools`: unsupported runtime refuses; a list "is never silently ignored" (`:940`).
- Harness: auto-detected from runtime markers (`$TMUX`, `HERDR_ENV`) innermost-first (`:435-438`); experimental ones
  "never auto-detected" (`:442`). Provider: "Firstmate never guesses a provider" (`:997`).
- `bin/fm-forge-detect.sh:9-14` — detection is **PROPOSAL ONLY**; the captain confirms and the record is kept,
  "because detection can be wrong, so nothing re-derives the binding from the clone later".
- `bin/fm-remote-doctor.sh:2` — readiness check with optional `--fix` per remote account.

**openclaw-openclaw** (`b94e5177`, local fetch) — no mise/.tool-versions/devcontainer. One code-owned version contract.
- `node-version.mjs:1,5-8` — floors live in a zero-dependency module "shared by source and packaged entry points"; the
  same numbers feed `package.json:2380` `engines` and the error text (`:21-29`). One source, many readers.
- Images pinned by tag **and digest** as build ARGs (`Dockerfile:16-21`); `packageManager` pinned with sha512 (`package.json:2382`).
- `openclaw doctor`: read-only lint mode for CI/preflight, `--fix` applies repairs (`docs/gateway/doctor/running.md:6,36-41`).

**cursor-plugins pstack** (`f713f14`) — `/setup-pstack` detects, asks one question, validates, overwrites.
- Detect models from the session; "Never write a real slug you have not confirmed is available" (`pstack/skills/setup-pstack/SKILL.md:14`).
- Asks only the **budget** (4 fixed labels, `:22-27`); everything else derived from it (`:29`), then shown for confirm (`:31`).
- Validate before write (`:35`); overwrite the whole file "so re-runs stay idempotent" (`:39`).

**mattpocock-skills** (`49dd158`) — setup infers from the repo, asks only where exploration did not settle it.
- "Explore, present what you found, confirm with the user, then write" (`skills/engineering/setup-matt-pocock-skills/SKILL.md:15`).
- Proposes GitHub/GitLab from `git remote` (`:42`); skips a section "when exploration already settled it" (`:36`);
  single-context domain docs written "without asking" (`:59`).
- No verify mode: re-run setup and ask it to check drift (`.out-of-scope/setup-skill-verify-mode.md:9`).

**imdganesancareers-MasterLaundry** (`8f61e5ea`) — the counter-example.
- `deploy/prod/.env.example:16-17` types the DB password twice (`DB_PASSWORD` and inside `DATABASE_URL`) — a derived value typed by hand.
- Floating images: `node:20-alpine` (`docker/Dockerfile:2,39`), `postgres:16-alpine`, `IMAGE_TAG:-latest` (`deploy/prod/docker-compose.yml:7,56`).

**humanlayer-humanlayer** (`99abe673`) — ports derived from the ticket number, probed, overridable.
- `hack/port-utils.sh:26-48`: try the ticket number, then `20000 + ticket%10000 + k·1000`; probe with lsof/nc.
- Typed override wins: `PORT=` skips derivation (`Makefile:290-296`). Flaw: no tool → "assume port is available" (`port-utils.sh:20-21`); probe-then-bind races.
- Setup is one script, CI detected from `$CI` (`hack/setup_repo.sh:11-15`). Nothing else on host config.

## Industry (primary docs, fetched 2026-10-17)

| source | says | for us |
|---|---|---|
| 12factor.net/config | config = "everything that is likely to vary between deploys"; stored in env vars | uid, port block vary per zone; Java version does **not** — it is code, not config |
| docs.gradle.org/…/toolchains.html | toolchain matched against detected JDKs (JAVA_HOME, SDKMAN!, asdf…); else downloaded via foojay into Gradle User Home | we already have this: host JAVA_HOME only picks the *launcher* JVM |
| docs.gradle.org/…/gradle_daemon.html | `updateDaemonJvm` writes `gradle/gradle-daemon-jvm.properties`, committed; criteria "takes precedence over JAVA_HOME"; downloads a JDK if none found | pins the daemon too → JAVA_HOME becomes irrelevant past "any JVM to start the wrapper" |
| sdkman.io/usage | `sdk env install` installs `.sdkmanrc` SDKs; `sdk env` switches PATH per shell; `sdkman_auto_env` on `cd` | per-shell, interactive — nothing a systemd/runner job inherits |
| mise.jdx.dev/dev-tools/versions.html | reads `.sdkmanrc`/`.java-version` for java, opt-in (`idiomatic_version_file_enable_tools` "empty by default") | mise could consume our existing `.sdkmanrc`; no new file needed |
| asdf-vm.com/manage/configuration.html | `.tool-versions`: `tool version` per line, applies to dir + subdirs; legacy files off by default | second file format = second source; avoid |
| containers.dev features + lockfile spec | Features are versioned OCI installers; `devcontainer-lock.json` records `version`, `resolved` (digest), `integrity` for "reproducibility" and "trust on first use" | lock pattern for our image inputs |
| containers.dev json_reference | `initializeCommand` runs on the host; `${localEnv:VAR}` reads host env; prefer `containerEnv` | host-derived facts can be computed at container start |
| nix.dev/concepts/flakes | `flake.lock` pins inputs once a nix command runs | forge's whole answer; heavy for us |
| freedesktop basedir spec | `XDG_RUNTIME_DIR` owned by user, 0700, lifetime "bound to the user being logged in"; unset → fall back + warn | not reliable for a lingering service user |
| man7 pam_systemd(8) | path is `/run/user/$UID`; "not set if the current user is not the original user of the session" | `sudo -u fleet-worker` → unset; derive from `id -u`, as `worker-container:56` does |
| docs.podman.io podman-system-service | rootless default `unix://$XDG_RUNTIME_DIR/podman/podman.sock` | DOCKER_HOST is a pure function of uid |

Unreached: systemd.io (403 on freedesktop.org/software/systemd); sdkman has no non-interactive docs page beyond usage.

## Options for us

**(a) Which values stay hand-typed**

| option | pros | cons | source |
|---|---|---|---|
| A1 Only trust/identity: `FLEET_OPERATOR_LOGIN`, `FLEET_CLAIM_LOGIN`, notifier target, repo URL | matches "never inferred from identity/remotes"; file shrinks to ~4 lines | detection can't help first-time setup | firstmate `configuration.md:591,596`; forge ADR-0002 tier 1 |
| A2 A1 + tunables with code defaults (watchdog hours, caps) — absent = default | example shows defaults, file only holds overrides | two places to read a value | forge `load-config.nix:4-14`; firstmate "absent means default" (`:144`) |
| A3 Keep today's list | no change | every derived fact can be typed wrong (uid, JDK path) | — |

Lean: **A2** — type only trust choices; tunables default in code, typed only to override.

**(b) How derived values are computed**

| option | pros | cons | source |
|---|---|---|---|
| B1 Launcher at start (`id -u` → socket, constant locale) | always current; already done in `worker-container:56` | each launcher repeats it unless one lib owns it | podman docs; pam_systemd |
| B2 fleet-zones at apply writes them into machine.env | one writer, visible in file | stale if uid/zone changes; file then mixes typed + generated | forge ADR-0002 (generated tfvars rejected: regenerate step) |
| B3 Image build (`ENV`) | facts of the image never vary | only for in-container facts; host socket path is host-side | `.devcontainer/Dockerfile:28-29` |

Lean: **B1 for host facts (uid, socket) via one `machine_env.py` function; B3 for in-container facts; nothing generated into the typed file.**

**(c) One source for the Java version**

| option | pros | cons | source |
|---|---|---|---|
| C1 Gradle owns it: toolchain + foojay (exists) + commit `gradle-daemon-jvm.properties`; host/image need only *a* JVM for the wrapper | already 80% there; no JAVA_HOME pin anywhere; works on host runner and in image alike | first build downloads a JDK (cache volume `fleet-gradle-cache` absorbs it); `.sdkmanrc` still the IDE/dev hint | Gradle toolchains + daemon docs; `settings.gradle.kts:10` |
| C2 Image built from `.sdkmanrc` (build arg read from project) | one file; host devs and image agree | agent-fleet image is project-agnostic — reading a project file couples the fleet to agent-platform | forge ADR-0027 (repo owns stack) |
| C3 Image build fails on mismatch (check, two files) | cheap, keeps layouts | still two sources, just guarded; patch drift (25.0.3 vs 25.0.4) needs a major-only rule like `doctor.sh:159` | openclaw `node-version.mjs` single contract |
| C4 Host never needs Java: run fleet-runner's gate inside the worker image too | removes host JDK entirely | shell executor → docker/podman executor is a bigger change (`setup-gate-runner.sh:157`) | forge: workloads run in repo's devShell |

Lean: **C1** — the project's Gradle build is the one source; `.sdkmanrc` is derived/checked from it by `make doctor`, and machine.env drops `JAVA_HOME`.

**(d) Port blocks**

| option | pros | cons | source |
|---|---|---|---|
| D1 Assigned by fleet-zones from zone index (`base + 100·i`) + overlap check at apply | no typing; same as Verifier slots | renumbering zones moves ports | `setup-verifier.sh:113`; humanlayer derive-from-id |
| D2 Typed + overlap check (today) | explicit | operator picks; check catches only fleet-known blocks | `setup-gate-runner.sh:113-133` |
| D3 Probe free ports at launch | zero config | races; "assume available" fallback | humanlayer `port-utils.sh:20-21` |

Lean: **D1** — assign deterministically, keep the overlap check, allow a typed override that the check still validates.
