## What changes

<!-- One or two sentences. Name the reference or check you changed. -->

## Why

<!-- The issue this closes or advances, e.g. "Closes #NN" or "agent-factory#31". -->

## Checklist

- [ ] `make lint` and `make test` pass locally
- [ ] Every new or changed rule has the operator's yes and a row in `docs/rulebook/approved-rules.md`
- [ ] A new reference follows `docs/rulebook/reference-format.md` and is listed in `plugins/rulebook/README.md` and the root `README.md`
- [ ] The title is a Conventional Commit: `feat` or `fix` when the shipped plugin changes, so it gets released
- [ ] No hand edits to a `version` or to `CHANGELOG.md`: the release writes both
