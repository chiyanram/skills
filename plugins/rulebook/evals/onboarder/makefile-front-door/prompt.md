---
description: A repo whose Makefile wraps the build tool. The onboarder should name the make targets, confirmed from the Makefile, not the raw build-tool commands.
expected_outcome: The brief's commands are make targets (make build, make test, make run) read from the Makefile; no raw ./gradlew command is given as the way to build or test.
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---

With crq, write this project's brief, as the onboarder. Show the build, test and run commands section.

```make
# Makefile
.PHONY: build test run
build: ## compile and package
	./gradlew assemble
test: ## unit and integration tests
	./gradlew check -PwithContainers
run: ## start the api on port 8085
	./gradlew bootRun
```

`README.md` says: "Build with ./gradlew build."
