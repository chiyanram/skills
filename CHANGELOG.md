# Changelog

What the `rulebook` plugin ships, by version. semantic-release writes this file from the commit messages on
`main`; do not edit it by hand. Design work under `research/` and `review/` ships nothing and is not listed.

## [1.1.2](https://github.com/chiyanram/skills/compare/rulebook--v1.1.1...rulebook--v1.1.2) (2026-11-10)

### 🐛 Fixes

* **crq** — the design-reviewer card hands off the JSON it returns ([chiyanram/agent-factory#237](https://github.com/chiyanram/agent-factory/issues/237)) · PR [#279](https://github.com/chiyanram/skills/pull/279)
* **repo** — leave git trailers out of breaking-change release notes · [#283](https://github.com/chiyanram/skills/issues/283) (PR [#284](https://github.com/chiyanram/skills/pull/284))

Update: `claude plugin update rulebook@chiyanram`

## [1.1.1](https://github.com/chiyanram/skills/compare/rulebook--v1.1.0...rulebook--v1.1.1) (2026-11-09)

### Bug Fixes

* **crq:** ask every open question at once, with choices ([chiyanram/agent-factory#320](https://github.com/chiyanram/agent-factory/issues/320)) ([#275](https://github.com/chiyanram/skills/issues/275)) ([bd1622b](https://github.com/chiyanram/skills/commit/bd1622b4b00e4941d68a7b2db7f130b1add2a3e8))
* **crq:** the finder card hands off the design's finding contract ([#237](https://github.com/chiyanram/skills/issues/237)) ([#274](https://github.com/chiyanram/skills/issues/274)) ([44d4a13](https://github.com/chiyanram/skills/commit/44d4a13678621bb21d143e503abd7a501d274147))

## [1.1.0](https://github.com/chiyanram/skills/compare/rulebook--v1.0.0...rulebook--v1.1.0) (2026-11-09)

### Features

* **agent:** add the agent domain with its seven references ([#134](https://github.com/chiyanram/skills/issues/134)) ([#266](https://github.com/chiyanram/skills/issues/266)) ([0d2744c](https://github.com/chiyanram/skills/commit/0d2744c73e5c319de46acbddfb7acda5c0b1e5f2)), closes [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#132](https://github.com/chiyanram/skills/issues/132) [#271](https://github.com/chiyanram/skills/issues/271) [#132](https://github.com/chiyanram/skills/issues/132)

## [1.0.0](https://github.com/chiyanram/skills/compare/rulebook--v0.45.0...rulebook--v1.0.0) (2026-11-09)

### ⚠ BREAKING CHANGES

* **planning:** rule IDs GA3 and CV1 are removed, and acceptance
criteria are no longer Gherkin scenarios.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012EphAgXmJeLDVFfEgSjwGe
* **planning:** rule ID GT2 is removed.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012EphAgXmJeLDVFfEgSjwGe

### Features

* **planning:** numbered AC-n lines replace Gherkin, with the AC-to-tests and glossary wording passes ([#244](https://github.com/chiyanram/skills/issues/244)) ([#260](https://github.com/chiyanram/skills/issues/260)) ([f9702ef](https://github.com/chiyanram/skills/commit/f9702ef83a51eb4b93943e8f9f82ba8bf417de43)), closes [#237](https://github.com/chiyanram/skills/issues/237)

## [0.45.0](https://github.com/chiyanram/skills/compare/rulebook--v0.44.0...rulebook--v0.45.0) (2026-11-09)

### Features

* **crq:** a full retro runs only when a human starts one ([#244](https://github.com/chiyanram/skills/issues/244)) ([#262](https://github.com/chiyanram/skills/issues/262)) ([d9ab715](https://github.com/chiyanram/skills/commit/d9ab71598665d098d1feb514bd015e3a5c9cf672))

## [0.44.0](https://github.com/chiyanram/skills/compare/rulebook--v0.43.0...rulebook--v0.44.0) (2026-11-09)

### Features

* **crq:** add the review baseline as process/review.json, checked by check_process.py ([#265](https://github.com/chiyanram/skills/issues/265)) ([0438085](https://github.com/chiyanram/skills/commit/0438085c93cf74f26a5926809b5b58d5c082a354))

## [0.43.0](https://github.com/chiyanram/skills/compare/rulebook--v0.42.0...rulebook--v0.43.0) (2026-11-09)

### Features

* **crq:** add the cleanup, retro and onboarder cards and their scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#252](https://github.com/chiyanram/skills/issues/252)) ([bff98af](https://github.com/chiyanram/skills/commit/bff98afd2c797546b1d39e322fe5b4165d709c4c))

## [0.42.0](https://github.com/chiyanram/skills/compare/rulebook--v0.41.0...rulebook--v0.42.0) (2026-11-09)

### Features

* **crq:** add the implementer card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#249](https://github.com/chiyanram/skills/issues/249)) ([24a3616](https://github.com/chiyanram/skills/commit/24a3616dbd0cd80cc0c9d878baaa579a10664602))

## [0.41.0](https://github.com/chiyanram/skills/compare/rulebook--v0.40.0...rulebook--v0.41.0) (2026-11-09)

### Features

* **crq:** add the test-first card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#248](https://github.com/chiyanram/skills/issues/248)) ([aee0579](https://github.com/chiyanram/skills/commit/aee0579e3ab98ba0f502252a325b8b0c4a4106e6))

## [0.40.0](https://github.com/chiyanram/skills/compare/rulebook--v0.39.0...rulebook--v0.40.0) (2026-11-09)

### Features

* **crq:** add the design-reviewer card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#247](https://github.com/chiyanram/skills/issues/247)) ([f7abca0](https://github.com/chiyanram/skills/commit/f7abca0c37e911047becba5810b24e4836372b42))

## [0.39.0](https://github.com/chiyanram/skills/compare/rulebook--v0.38.0...rulebook--v0.39.0) (2026-11-09)

### Features

* **crq:** add the coordinator card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#246](https://github.com/chiyanram/skills/issues/246)) ([73397bb](https://github.com/chiyanram/skills/commit/73397bbb75e4f9b77a4056826606e577e1f4ea38))

## [0.38.0](https://github.com/chiyanram/skills/compare/rulebook--v0.37.0...rulebook--v0.38.0) (2026-11-09)

### Features

* **crq:** add the verify-pass card and its three scenarios ([#237](https://github.com/chiyanram/skills/issues/237)) ([#245](https://github.com/chiyanram/skills/issues/245)) ([e8f93cd](https://github.com/chiyanram/skills/commit/e8f93cd0729bb87540ff6d96f03e6c9355b7a32c))

## [0.37.0](https://github.com/chiyanram/skills/compare/rulebook--v0.36.0...rulebook--v0.37.0) (2026-11-09)

### Features

* **crq:** add the lanes file, the glossary and the finder card ([#237](https://github.com/chiyanram/skills/issues/237)) ([#243](https://github.com/chiyanram/skills/issues/243)) ([2cee43b](https://github.com/chiyanram/skills/commit/2cee43b69362dd00d961d584351222af31253eb3))

## [0.36.0](https://github.com/chiyanram/skills/compare/rulebook--v0.35.1...rulebook--v0.36.0) (2026-11-09)

### Features

* **crq:** add the test-integrity review rubric ([#235](https://github.com/chiyanram/skills/issues/235)) ([#241](https://github.com/chiyanram/skills/issues/241)) ([3888c9e](https://github.com/chiyanram/skills/commit/3888c9ea041527acfdccce19b75ae44cfc195353))

### Bug Fixes

* **crq:** role evals live in evals/<role>/, the review cases become the finder's ([#236](https://github.com/chiyanram/skills/issues/236)) ([#242](https://github.com/chiyanram/skills/issues/242)) ([e37f14f](https://github.com/chiyanram/skills/commit/e37f14fcf2b19bf81134622ddde1674775fee4fe))

## [0.35.1](https://github.com/chiyanram/skills/compare/rulebook--v0.35.0...rulebook--v0.35.1) (2026-11-09)

### Bug Fixes

* **crq:** approval binds spec and design, a three-round review cap, one size rule ([#234](https://github.com/chiyanram/skills/issues/234)) ([#240](https://github.com/chiyanram/skills/issues/240)) ([2055d87](https://github.com/chiyanram/skills/commit/2055d873ef427726cca99196076e8b2544bf367d))

## [0.35.0](https://github.com/chiyanram/skills/compare/rulebook--v0.34.1...rulebook--v0.35.0) (2026-11-09)

### Features

* **planning:** every review check names when it applies, its evidence, its edges, severity and verify ([#210](https://github.com/chiyanram/skills/issues/210)) ([#232](https://github.com/chiyanram/skills/issues/232)) ([2db978f](https://github.com/chiyanram/skills/commit/2db978fb8f850a00ca2b8ecafecebab89f1b15c6))

## [0.34.1](https://github.com/chiyanram/skills/compare/rulebook--v0.34.0...rulebook--v0.34.1) (2026-11-08)

### Bug Fixes

* **code:** name JPA entities and repositories in the router, with a free routing check ([#223](https://github.com/chiyanram/skills/issues/223)) ([#228](https://github.com/chiyanram/skills/issues/228)) ([734fb63](https://github.com/chiyanram/skills/commit/734fb633da2f3417062615d3b1ef9c05bfe5bb7f))

## [0.34.0](https://github.com/chiyanram/skills/compare/rulebook--v0.33.0...rulebook--v0.34.0) (2026-11-08)

### Features

* **crq:** Group B rules from the outside skill repos ([#223](https://github.com/chiyanram/skills/issues/223)) ([#227](https://github.com/chiyanram/skills/issues/227)) ([369f28f](https://github.com/chiyanram/skills/commit/369f28f847eedc019e23bdb119b8480c814f9263))

## [0.33.0](https://github.com/chiyanram/skills/compare/rulebook--v0.32.1...rulebook--v0.33.0) (2026-11-07)

### Features

* **planning:** seven rules from the outside skill repos ([#223](https://github.com/chiyanram/skills/issues/223)) ([#226](https://github.com/chiyanram/skills/issues/226)) ([49c312e](https://github.com/chiyanram/skills/commit/49c312e07ad8d89c4a816ad8ab31ff908ad7b035))

### Bug Fixes

* **repo:** merge the ledger with union and check it for repeated rows ([#224](https://github.com/chiyanram/skills/issues/224)) ([f8a91d6](https://github.com/chiyanram/skills/commit/f8a91d6117556256818ec4343a34752ef97c9042))

## [0.32.1](https://github.com/chiyanram/skills/compare/rulebook--v0.32.0...rulebook--v0.32.1) (2026-11-06)

### Bug Fixes

* **crq:** approval gate counts a human-only control recorded with the spec hash ([#210](https://github.com/chiyanram/skills/issues/210)) ([#222](https://github.com/chiyanram/skills/issues/222)) ([2c54c46](https://github.com/chiyanram/skills/commit/2c54c4677c51e0a363a3c1329911414180c4472f)), closes [agent-factory#30](https://github.com/chiyanram/agent-factory/issues/30)

## [0.32.0](https://github.com/chiyanram/skills/compare/rulebook--v0.31.1...rulebook--v0.32.0) (2026-11-06)

### Features

* **crq:** review never approves, approval is human-signed, new deps go to the human ([#210](https://github.com/chiyanram/skills/issues/210)) ([#221](https://github.com/chiyanram/skills/issues/221)) ([abfec90](https://github.com/chiyanram/skills/commit/abfec90f3d72dfd4be2b1ca38c5efe956ac57018)), closes [agent-factory#30](https://github.com/chiyanram/agent-factory/issues/30)

## [0.31.1](https://github.com/chiyanram/skills/compare/rulebook--v0.31.0...rulebook--v0.31.1) (2026-11-06)

### Bug Fixes

* **crq:** name the approval gate, not a /approved token ([#210](https://github.com/chiyanram/skills/issues/210)) ([#220](https://github.com/chiyanram/skills/issues/220)) ([02b0d50](https://github.com/chiyanram/skills/commit/02b0d50c9416ca41723d38669531afee29721008)), closes [chiyanram/agent-factory#30](https://github.com/chiyanram/agent-factory/issues/30)

## [0.31.0](https://github.com/chiyanram/skills/compare/rulebook--v0.30.0...rulebook--v0.31.0) (2026-11-06)

### Features

* **code:** Redis reference and Redis Streams messaging rules ([#219](https://github.com/chiyanram/skills/issues/219)) ([3b78b10](https://github.com/chiyanram/skills/commit/3b78b103e25cf3240d50ff36760f50ae3c402f77)), closes [#71](https://github.com/chiyanram/skills/issues/71) [#56](https://github.com/chiyanram/skills/issues/56) [#71](https://github.com/chiyanram/skills/issues/71)

## [0.30.0](https://github.com/chiyanram/skills/compare/rulebook--v0.29.0...rulebook--v0.30.0) (2026-11-06)

### Features

* **code:** rules from a production-incident check of the merged references ([#218](https://github.com/chiyanram/skills/issues/218)) ([1247551](https://github.com/chiyanram/skills/commit/12475510841e153e341b8d32abb72d4a1873f7eb))

## [0.29.0](https://github.com/chiyanram/skills/compare/rulebook--v0.28.0...rulebook--v0.29.0) (2026-11-06)

### Features

* **code:** scheduling and batch jobs reference ([#217](https://github.com/chiyanram/skills/issues/217)) ([9fcf7c4](https://github.com/chiyanram/skills/commit/9fcf7c4c01747f3514129c5ce3c3ffcfdc131700)), closes [#52](https://github.com/chiyanram/skills/issues/52) [#52](https://github.com/chiyanram/skills/issues/52)

## [0.28.0](https://github.com/chiyanram/skills/compare/rulebook--v0.27.0...rulebook--v0.28.0) (2026-11-06)

### Features

* **code:** API design reference — pagination, compatibility, versioning ([#216](https://github.com/chiyanram/skills/issues/216)) ([9af215e](https://github.com/chiyanram/skills/commit/9af215ecc0f7cce5f188f22eaa4ee32059ed3f7c)), closes [#74](https://github.com/chiyanram/skills/issues/74) [#74](https://github.com/chiyanram/skills/issues/74) [#74](https://github.com/chiyanram/skills/issues/74)

## [0.27.0](https://github.com/chiyanram/skills/compare/rulebook--v0.26.0...rulebook--v0.27.0) (2026-11-06)

### Features

* **crq:** the /crq pipeline skill with its six references, and four planning rules ([chiyanram/skills#210](https://github.com/chiyanram/skills/issues/210)) ([#214](https://github.com/chiyanram/skills/issues/214)) ([58ac935](https://github.com/chiyanram/skills/commit/58ac93511acbfd8b2d523cc5b6925f9e9ffe8e17))

## [0.26.0](https://github.com/chiyanram/skills/compare/rulebook--v0.25.0...rulebook--v0.26.0) (2026-11-06)

### Features

* **code:** concurrent-edit rules — ETag and If-Match, 409 for lost races, required idempotency keys ([#215](https://github.com/chiyanram/skills/issues/215)) ([a7ed9da](https://github.com/chiyanram/skills/commit/a7ed9da9ad82390b424d2a04d7a99045477319c1)), closes [#75](https://github.com/chiyanram/skills/issues/75) [#75](https://github.com/chiyanram/skills/issues/75) [#75](https://github.com/chiyanram/skills/issues/75) [#75](https://github.com/chiyanram/skills/issues/75)

## [0.25.0](https://github.com/chiyanram/skills/compare/rulebook--v0.24.0...rulebook--v0.25.0) (2026-11-06)

### Features

* **code:** resilience rules — one retry layer, deadline propagation, idempotency keys, Retry-After ([#213](https://github.com/chiyanram/skills/issues/213)) ([512998b](https://github.com/chiyanram/skills/commit/512998b0cbc592949c59c01acf6e8a255f33841e)), closes [#54](https://github.com/chiyanram/skills/issues/54) [#54](https://github.com/chiyanram/skills/issues/54) [#54](https://github.com/chiyanram/skills/issues/54)

## [0.24.0](https://github.com/chiyanram/skills/compare/rulebook--v0.23.0...rulebook--v0.24.0) (2026-11-06)

### Features

* **code:** persistence reference — JPA fetching, paging, batching, ids, locking, pool ([#212](https://github.com/chiyanram/skills/issues/212)) ([547841f](https://github.com/chiyanram/skills/commit/547841f9a8809a0d4f2bd639fc0007f4248f68ae)), closes [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57) [#57](https://github.com/chiyanram/skills/issues/57)

## [0.23.0](https://github.com/chiyanram/skills/compare/rulebook--v0.22.0...rulebook--v0.23.0) (2026-11-04)

### Features

* **planning:** design-review rules SR9–SR15 in spec-review; SR4 asks for options and a recommendation (SR8) ([#207](https://github.com/chiyanram/skills/issues/207)) ([d77e110](https://github.com/chiyanram/skills/commit/d77e1103a794bd54956c2de601d76afb1cc853ae))

## [0.22.0](https://github.com/chiyanram/skills/compare/rulebook--v0.21.4...rulebook--v0.22.0) (2026-11-04)

### Features

* **code:** modern-java reference for current JDKs ([chiyanram/agent-factory#60](https://github.com/chiyanram/agent-factory/issues/60)) ([#208](https://github.com/chiyanram/skills/issues/208)) ([c1a2f70](https://github.com/chiyanram/skills/commit/c1a2f70f947251e6621438509abe8f5f3564c90f))

## [0.21.4](https://github.com/chiyanram/skills/compare/rulebook--v0.21.3...rulebook--v0.21.4) (2026-11-04)

### Bug Fixes

* **testing:** S6, a bug fix's failing test runs locally first ([#152](https://github.com/chiyanram/skills/issues/152)) ([#205](https://github.com/chiyanram/skills/issues/205)) ([90a7fb6](https://github.com/chiyanram/skills/commit/90a7fb63391e2504e3ef911fe67ece427645c64f))

## [0.21.3](https://github.com/chiyanram/skills/compare/rulebook--v0.21.2...rulebook--v0.21.3) (2026-11-04)

### Features

* **repo:** rule files hold only rules; check_provenance enforces it ([chiyanram/agent-factory#59](https://github.com/chiyanram/agent-factory/issues/59)) ([#204](https://github.com/chiyanram/skills/issues/204)) ([e81dd2d](https://github.com/chiyanram/skills/commit/e81dd2dc2880aba4059ba374c9e43ed3cfd0c980))

### Bug Fixes

* **code:** drop CM6; ER1, MS6 and DS12 examples keep decisions free of I/O ([chiyanram/agent-factory#59](https://github.com/chiyanram/agent-factory/issues/59)) ([#206](https://github.com/chiyanram/skills/issues/206)) ([b7c3511](https://github.com/chiyanram/skills/commit/b7c3511c808dd57f3438797424b36ca9091ff215))

## [0.21.2](https://github.com/chiyanram/skills/compare/rulebook--v0.21.1...rulebook--v0.21.2) (2026-11-04)

### Bug Fixes

* **obs:** migrations and obs files hold only rules ([chiyanram/agent-factory#59](https://github.com/chiyanram/agent-factory/issues/59)) ([#203](https://github.com/chiyanram/skills/issues/203)) ([6b23875](https://github.com/chiyanram/skills/commit/6b2387534012d8f77a5b00afb3a274dcc07c1670))

## [0.21.1](https://github.com/chiyanram/skills/compare/rulebook--v0.21.0...rulebook--v0.21.1) (2026-11-04)

### Bug Fixes

* **code:** industry re-check applied; code files hold only rules ([chiyanram/agent-factory#59](https://github.com/chiyanram/agent-factory/issues/59)) ([#200](https://github.com/chiyanram/skills/issues/200)) ([985d4dd](https://github.com/chiyanram/skills/commit/985d4ddaf3452c081014d66c97a2016246645f31))
* **planning:** planning and meta files hold only rules; SRC2 keeps provenance in the ledger ([chiyanram/agent-factory#59](https://github.com/chiyanram/agent-factory/issues/59)) ([#202](https://github.com/chiyanram/skills/issues/202)) ([8cb3682](https://github.com/chiyanram/skills/commit/8cb36826a11179eec5c40b8b286f3e12fde29f1b))
* **testing:** testing files hold only rules ([chiyanram/agent-factory#59](https://github.com/chiyanram/agent-factory/issues/59)) ([#201](https://github.com/chiyanram/skills/issues/201)) ([e9d9a0f](https://github.com/chiyanram/skills/commit/e9d9a0f9804e9d9b194ac516d1e44ee8d0f031f3))

## [0.21.0](https://github.com/chiyanram/skills/compare/rulebook--v0.20.0...rulebook--v0.21.0) (2026-11-04)

### Features

* **rulebook:** build each router's reference table with make index ([#199](https://github.com/chiyanram/skills/issues/199)) ([638d357](https://github.com/chiyanram/skills/commit/638d357ec5bba9700c2ef572b10d69bfcb5d6acf)), closes [chiyanram/agent-factory#46](https://github.com/chiyanram/agent-factory/issues/46)

## [0.20.0](https://github.com/chiyanram/skills/compare/rulebook--v0.19.0...rulebook--v0.20.0) (2026-11-02)

### Features

* **meta:** writing-references reference from industry sources ([#197](https://github.com/chiyanram/skills/issues/197)) ([314a934](https://github.com/chiyanram/skills/commit/314a9349bdab212164f6f8d7bdc106ec01f871ac)), closes [agent-factory#33](https://github.com/chiyanram/agent-factory/issues/33)
* **planning:** diagrams reference from industry sources ([#195](https://github.com/chiyanram/skills/issues/195)) ([b4b67ff](https://github.com/chiyanram/skills/commit/b4b67ff7fa6a329673b00dabbd42900fa2847414)), closes [agent-factory#33](https://github.com/chiyanram/agent-factory/issues/33)
* **planning:** writing-docs reference from industry sources ([#196](https://github.com/chiyanram/skills/issues/196)) ([519f082](https://github.com/chiyanram/skills/commit/519f08256f89db537408b15f94015c6152afd97b)), closes [agent-factory#33](https://github.com/chiyanram/agent-factory/issues/33)

## [0.19.0](https://github.com/chiyanram/skills/compare/rulebook--v0.18.0...rulebook--v0.19.0) (2026-11-02)

### Features

* **planning:** program-design reference from industry sources ([#194](https://github.com/chiyanram/skills/issues/194)) ([7dee76f](https://github.com/chiyanram/skills/commit/7dee76f11a9f83fa5f25611dec6b9f96d39bce99)), closes [agent-factory#33](https://github.com/chiyanram/agent-factory/issues/33)

## [0.18.0](https://github.com/chiyanram/skills/compare/rulebook--v0.17.0...rulebook--v0.18.0) (2026-11-02)

### Features

* **planning:** spec-review reference from industry sources ([#193](https://github.com/chiyanram/skills/issues/193)) ([07e2efa](https://github.com/chiyanram/skills/commit/07e2efadcbde309db29dade23499c68274179f37)), closes [agent-factory#33](https://github.com/chiyanram/agent-factory/issues/33)

## [0.17.0](https://github.com/chiyanram/skills/compare/rulebook--v0.16.3...rulebook--v0.17.0) (2026-11-02)

### Features

* **planning:** acceptance-criteria reference from industry sources ([#192](https://github.com/chiyanram/skills/issues/192)) ([0d19d09](https://github.com/chiyanram/skills/commit/0d19d0920dd99110a9d92c4b98e9d3b9128b7192)), closes [agent-factory#33](https://github.com/chiyanram/agent-factory/issues/33)

## [0.16.3](https://github.com/chiyanram/skills/compare/rulebook--v0.16.2...rulebook--v0.16.3) (2026-11-01)

### Bug Fixes

* **code:** comments-concurrency-ui-services Good/Bad pairs come from sources, not project code ([#189](https://github.com/chiyanram/skills/issues/189)) ([6aba449](https://github.com/chiyanram/skills/commit/6aba449f933fd076589b8e51727eb62da2c4a4d2)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** errors-messaging Good/Bad pairs come from sources, not project code ([#187](https://github.com/chiyanram/skills/issues/187)) ([d25e8f5](https://github.com/chiyanram/skills/commit/d25e8f59cf8d57ac38e8bb3cf8cd1fd7b03cae18)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** java-types Good/Bad pairs come from sources, not project code ([#188](https://github.com/chiyanram/skills/issues/188)) ([0d694b2](https://github.com/chiyanram/skills/commit/0d694b202114f0a9be7085910a090fbaa77695cc)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** security Good/Bad pairs come from sources, not project code ([#185](https://github.com/chiyanram/skills/issues/185)) ([11ec167](https://github.com/chiyanram/skills/commit/11ec1678cba4cc27d22cb15a4f289ddd3224aaf3)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** smells-design Good/Bad pairs come from sources, not project code ([#186](https://github.com/chiyanram/skills/issues/186)) ([1d77a3e](https://github.com/chiyanram/skills/commit/1d77a3e431c9a4e117867b857980a3ae78ebb848)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** spring Good/Bad pairs come from sources, not project code ([#184](https://github.com/chiyanram/skills/issues/184)) ([d6fe8ab](https://github.com/chiyanram/skills/commit/d6fe8ab88dfa8634790f74d7b20e7b5a25128ae4)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)

## [0.16.2](https://github.com/chiyanram/skills/compare/rulebook--v0.16.1...rulebook--v0.16.2) (2026-11-01)

### Bug Fixes

* **code:** a rule line holds the rule only; preference moves to one line ([#183](https://github.com/chiyanram/skills/issues/183)) ([a2af313](https://github.com/chiyanram/skills/commit/a2af3136611c646bd722e3335cfd533e4fe3fcdd))

## [0.16.1](https://github.com/chiyanram/skills/compare/rulebook--v0.16.0...rulebook--v0.16.1) (2026-11-01)

### Bug Fixes

* **code:** angular-ui rules cite two sources or the preference label ([#170](https://github.com/chiyanram/skills/issues/170)) ([1deeabc](https://github.com/chiyanram/skills/commit/1deeabc03d1153f4ef858c071428d347f47b124e)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** comments rules cite two sources or the preference label ([#171](https://github.com/chiyanram/skills/issues/171)) ([6cba5f6](https://github.com/chiyanram/skills/commit/6cba5f60c0a5983136008bfa43fd047439308e3a)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** concurrency rules cite two sources or the preference label ([#172](https://github.com/chiyanram/skills/issues/172)) ([b3d8f0f](https://github.com/chiyanram/skills/commit/b3d8f0f9c8bdebbbb935227e81ef8791eb82750f)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** design rules cite two sources or the preference label ([#173](https://github.com/chiyanram/skills/issues/173)) ([2f5bc75](https://github.com/chiyanram/skills/commit/2f5bc750f33401c221e7f0634977c92f43342e50)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** deslop rules cite two sources or the preference label ([#174](https://github.com/chiyanram/skills/issues/174)) ([48a9229](https://github.com/chiyanram/skills/commit/48a92296a1a322f3a05882c50afb98041e960a89)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** errors rules cite two sources or the preference label ([#175](https://github.com/chiyanram/skills/issues/175)) ([5c34e38](https://github.com/chiyanram/skills/commit/5c34e38ec4ba00a9eaf5ebc3004bf73321c75e84)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** java rules cite two sources or the preference label ([#176](https://github.com/chiyanram/skills/issues/176)) ([742aa95](https://github.com/chiyanram/skills/commit/742aa956423926f727cf9356224d5028776d7400)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** messaging rules cite two sources or the preference label ([#177](https://github.com/chiyanram/skills/issues/177)) ([4d7c66e](https://github.com/chiyanram/skills/commit/4d7c66e24a989ed7af6a41f5f8d707d396491999)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** security rules cite two sources or the preference label ([#178](https://github.com/chiyanram/skills/issues/178)) ([4263af4](https://github.com/chiyanram/skills/commit/4263af4dda20c5f76478d23a91d482f51cef2d64)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** services rules cite two sources or the preference label ([#179](https://github.com/chiyanram/skills/issues/179)) ([d258c52](https://github.com/chiyanram/skills/commit/d258c52b421bf0746d2c95636ccfe13a40757671)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** smells rules cite two sources or the preference label ([#180](https://github.com/chiyanram/skills/issues/180)) ([fda57e4](https://github.com/chiyanram/skills/commit/fda57e4be1ac28ad37444a5a95a477b0aae7f54a)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** spring rules cite two sources or the preference label ([#181](https://github.com/chiyanram/skills/issues/181)) ([3ae91ca](https://github.com/chiyanram/skills/commit/3ae91ca5bfb924d8f9d90bf490d1676f789c67bc)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)
* **code:** types rules cite two sources or the preference label ([#182](https://github.com/chiyanram/skills/issues/182)) ([7a6f307](https://github.com/chiyanram/skills/commit/7a6f30725f16b4c7408846deba9437d66bb46a31)), closes [agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)

## [0.16.0](https://github.com/chiyanram/skills/compare/rulebook--v0.15.0...rulebook--v0.16.0) (2026-10-31)

### Features

* **rulebook:** one SKILL.md router per domain, so references load ([#169](https://github.com/chiyanram/skills/issues/169)) ([7ce8e2d](https://github.com/chiyanram/skills/commit/7ce8e2dbe48fd5bd1f23c2ddedcc996c59e27388))

## [0.15.0](https://github.com/chiyanram/skills/compare/rulebook--v0.14.0...rulebook--v0.15.0) (2026-10-31)

### Features

* **obs:** tracing reference from industry sources ([#164](https://github.com/chiyanram/skills/issues/164)) ([f7980ed](https://github.com/chiyanram/skills/commit/f7980ed9451102247b6832356612af1237fe42d4))

## [0.14.0](https://github.com/chiyanram/skills/compare/rulebook--v0.13.0...rulebook--v0.14.0) (2026-10-31)

### Features

* **obs:** metrics reference from industry sources ([#163](https://github.com/chiyanram/skills/issues/163)) ([7ab70d7](https://github.com/chiyanram/skills/commit/7ab70d74d6f9918c43a5df7ed5d65045ef864e0a))

### Bug Fixes

* **obs:** review round 2 for the logging reference ([#166](https://github.com/chiyanram/skills/issues/166)) ([629c64f](https://github.com/chiyanram/skills/commit/629c64f035dffafb871e35a67c10e2d003d04f12))

## [0.13.0](https://github.com/chiyanram/skills/compare/rulebook--v0.12.0...rulebook--v0.13.0) (2026-10-31)

### Features

* **testing:** LLM testing references, fake tier and live tier ([#165](https://github.com/chiyanram/skills/issues/165)) ([3232cf1](https://github.com/chiyanram/skills/commit/3232cf1380c78a49c387a8be8b837de8216bf88a))

## [0.12.0](https://github.com/chiyanram/skills/compare/rulebook--v0.11.0...rulebook--v0.12.0) (2026-10-31)

### Features

* **obs:** logging reference from industry sources ([#161](https://github.com/chiyanram/skills/issues/161)) ([c82b50b](https://github.com/chiyanram/skills/commit/c82b50b15746746ba6a9ca4f932742a640e41225))

### Bug Fixes

* **migrations:** review round 1 for postgres-design, review and levels ([#162](https://github.com/chiyanram/skills/issues/162)) ([d8a8f3a](https://github.com/chiyanram/skills/commit/d8a8f3a7abee8f12883c76e33f249dc139b4c9a3))

## [0.11.0](https://github.com/chiyanram/skills/compare/rulebook--v0.10.0...rulebook--v0.11.0) (2026-10-31)

### Features

* **migrations:** review reference for safe changes to live tables ([#160](https://github.com/chiyanram/skills/issues/160)) ([697a3c1](https://github.com/chiyanram/skills/commit/697a3c1fecf67f041388fb87319257ccb6ad9f60))
* **obs:** levels reference, the log-level table from industry sources ([#158](https://github.com/chiyanram/skills/issues/158)) ([b534713](https://github.com/chiyanram/skills/commit/b534713d482a86b61b5028354555079ae6e22a6a))

## [0.10.0](https://github.com/chiyanram/skills/compare/rulebook--v0.9.0...rulebook--v0.10.0) (2026-10-31)

### Features

* **code:** security rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#150](https://github.com/chiyanram/skills/issues/150)) ([bf58042](https://github.com/chiyanram/skills/commit/bf58042cdf97236f6ae5f4cc69cc32a08abaf8ff))

## [0.9.0](https://github.com/chiyanram/skills/compare/rulebook--v0.8.0...rulebook--v0.9.0) (2026-10-31)

### Features

* **code:** angular-ui rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#151](https://github.com/chiyanram/skills/issues/151)) ([4ad861b](https://github.com/chiyanram/skills/commit/4ad861bd4939348a6b75e7fa990b7104fce3dc5e))
* **code:** messaging rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#149](https://github.com/chiyanram/skills/issues/149)) ([62353ea](https://github.com/chiyanram/skills/commit/62353ea8156e57267bcba66e52698ac0d006ab67))

## [0.8.0](https://github.com/chiyanram/skills/compare/rulebook--v0.7.0...rulebook--v0.8.0) (2026-10-31)

### Features

* **code:** concurrency rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#148](https://github.com/chiyanram/skills/issues/148)) ([3505519](https://github.com/chiyanram/skills/commit/3505519849aff3c28755fccd4edeeef6d3e8f03c))
* **code:** services rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#146](https://github.com/chiyanram/skills/issues/146)) ([1865f60](https://github.com/chiyanram/skills/commit/1865f6041fc1fe8220ecb7cfed02bf0f428feffe))
* **code:** spring rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#147](https://github.com/chiyanram/skills/issues/147)) ([49209e6](https://github.com/chiyanram/skills/commit/49209e6d80dbb2549cdedb681165c57f887f6a36))
* **migrations:** postgres-design reference from industry sources ([#157](https://github.com/chiyanram/skills/issues/157)) ([7f685cf](https://github.com/chiyanram/skills/commit/7f685cf2e1c20e1a9bb8ce1c3a7ae6fdb1f88e3d))

## [0.7.0](https://github.com/chiyanram/skills/compare/rulebook--v0.6.1...rulebook--v0.7.0) (2026-10-31)

### Features

* **code:** deslop rule skill ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#145](https://github.com/chiyanram/skills/issues/145)) ([38dbd61](https://github.com/chiyanram/skills/commit/38dbd619bf999f5cb207e782bdf8537e484573ab))

## [0.6.1](https://github.com/chiyanram/skills/compare/rulebook--v0.6.0...rulebook--v0.6.1) (2026-10-31)

### Bug Fixes

* **ci:** check only the PR's own commits for a skip-ci marker ([#156](https://github.com/chiyanram/skills/issues/156)) ([db7af03](https://github.com/chiyanram/skills/commit/db7af03f7bcf38bf43500aafdad862c4f2385e6b))

## [0.6.0](https://github.com/chiyanram/skills/compare/rulebook--v0.5.0...rulebook--v0.6.0) (2026-10-31)

### Features

* **code:** comments rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#143](https://github.com/chiyanram/skills/issues/143)) ([5f3b9e0](https://github.com/chiyanram/skills/commit/5f3b9e007861a5fc3a3d863e86fce41f3d1d45dc))
* **code:** errors rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#142](https://github.com/chiyanram/skills/issues/142)) ([001ad6e](https://github.com/chiyanram/skills/commit/001ad6e1d1234314761a4013d278d59f167b31e2))
* **code:** smells rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#144](https://github.com/chiyanram/skills/issues/144)) ([fef4eb5](https://github.com/chiyanram/skills/commit/fef4eb55d7ae7d4e48846cb27cd7c50f48713ab4))

## [0.5.0](https://github.com/chiyanram/skills/compare/rulebook--v0.4.0...rulebook--v0.5.0) (2026-10-30)

### Features

* **code:** java rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#141](https://github.com/chiyanram/skills/issues/141)) ([f1a4d94](https://github.com/chiyanram/skills/commit/f1a4d94c8f4ed9b3e0e88189e09c4e21d5ec1270))

## [0.4.0](https://github.com/chiyanram/skills/compare/rulebook--v0.3.0...rulebook--v0.4.0) (2026-10-30)

### Features

* **code:** types rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#140](https://github.com/chiyanram/skills/issues/140)) ([08c0e1b](https://github.com/chiyanram/skills/commit/08c0e1bdfc5637807c8753fb7c24a8a099f3d75b))

## [0.3.0](https://github.com/chiyanram/skills/compare/rulebook--v0.2.0...rulebook--v0.3.0) (2026-10-30)

### Features

* **code:** design rule file ([chiyanram/agent-factory#32](https://github.com/chiyanram/agent-factory/issues/32)) ([#139](https://github.com/chiyanram/skills/issues/139)) ([4bea42f](https://github.com/chiyanram/skills/commit/4bea42f73edcdecf06e73de08fcf77de5a71e551))

### Bug Fixes

* **repo:** link cross-repo issue references to their own repo in release notes ([#129](https://github.com/chiyanram/skills/issues/129)) ([ba2a7a2](https://github.com/chiyanram/skills/commit/ba2a7a21c0713104c8d89ad9e380f9c8559a4817)), closes [#N](https://github.com/chiyanram/skills/issues/N) [agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31) [owner/repo#N](https://github.com/owner/repo/issues/N) [repo#N](https://github.com/chiyanram/repo/issues/N) [owner/repo#N](https://github.com/owner/repo/issues/N) [agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)

## [0.2.0](https://github.com/chiyanram/skills/compare/rulebook--v0.1.0...rulebook--v0.2.0) (2026-10-30)

### Features

* **testing:** boundaries rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31), 1 of 11) ([#113](https://github.com/chiyanram/skills/issues/113)) ([7a4d5e0](https://github.com/chiyanram/skills/commit/7a4d5e04828e2822b77119697902a4bfa81082b7)), closes [skills#112](https://github.com/chiyanram/skills/issues/112)
* **testing:** coverage-design rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#116](https://github.com/chiyanram/skills/issues/116)) ([24f6c0b](https://github.com/chiyanram/skills/commit/24f6c0b2357279b720fa890bbb056cd340de6faa))
* **testing:** integration-tests rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#119](https://github.com/chiyanram/skills/issues/119)) ([55187cc](https://github.com/chiyanram/skills/commit/55187cc89840da348a911ed35d846ceab1f60605))
* **testing:** mutation rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#122](https://github.com/chiyanram/skills/issues/122)) ([09f7674](https://github.com/chiyanram/skills/commit/09f7674bbcdffc008feb432f848cb4fb08ba0176))
* **testing:** property-based rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#123](https://github.com/chiyanram/skills/issues/123)) ([70ef00f](https://github.com/chiyanram/skills/commit/70ef00f6e768831267e2fc1754a66ce3dc6713a7))
* **testing:** scenario-to-tests rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#121](https://github.com/chiyanram/skills/issues/121)) ([715aa11](https://github.com/chiyanram/skills/commit/715aa111795cecbf998b15e3b75f54a3909543fa))
* **testing:** smoke-specs rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#124](https://github.com/chiyanram/skills/issues/124)) ([b57c2f8](https://github.com/chiyanram/skills/commit/b57c2f8e38012e9d97549884f923e9d8d1f82b87))
* **testing:** spock rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#120](https://github.com/chiyanram/skills/issues/120)) ([366dcec](https://github.com/chiyanram/skills/commit/366dceccaa0bef2a7af300772922290527ef1c6b))
* **testing:** strategy rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#115](https://github.com/chiyanram/skills/issues/115)) ([782b7a7](https://github.com/chiyanram/skills/commit/782b7a7c3aac16315ff9853f71a1577d6b1837b4))
* **testing:** unit-tests rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#118](https://github.com/chiyanram/skills/issues/118)) ([7b25c8a](https://github.com/chiyanram/skills/commit/7b25c8ace1f6fdb1b98d332f998a43a0a3907cb4))
* **testing:** value-bar rule file ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#117](https://github.com/chiyanram/skills/issues/117)) ([cd0e23b](https://github.com/chiyanram/skills/commit/cd0e23ba493e0e9ba04a5eaa1e66d57fff1318f9))

### Bug Fixes

* **testing:** examples obey every rule; four rule conflicts resolved ([chiyanram/agent-factory#31](https://github.com/chiyanram/agent-factory/issues/31)) ([#126](https://github.com/chiyanram/skills/issues/126)) ([26d92b1](https://github.com/chiyanram/skills/commit/26d92b17c56b5e2dda022b4989606ff81e48e86b))

## 0.1.0 (2026-10-17)

### Features

* the `chiyanram` marketplace and the `rulebook` plugin, with an empty skills tree (G23 #93) ([4d69442](https://github.com/chiyanram/skills/commit/4d69442))
