---
type: llm
---

The Makefile is the project's front door: `make test` adds a flag the raw command lacks, and the README's line is stale.

PASS if the brief gives `make build`, `make test` and `make run` as the commands, taken from the Makefile, and does not give a raw `./gradlew` command as the way to build or test.

FAIL if the brief's main build or test command is `./gradlew build` or another raw build-tool call.
