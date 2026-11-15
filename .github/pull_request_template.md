Why: <the reason for this change, in one sentence>. Spec: #<the approved spec; with no spec, the issue>

Breaking change: <no; or yes, and what a project or tool must change. A yes also takes "!" after the title's scope and a "BREAKING CHANGE:" footer above the Closes line>
Rollback: <revert this PR; no released format changes. Or how to switch it off>
Where to look: <one to three places where a mistake would cost most>

## Evidence at <commit>

| criterion | command or test | result |
|---|---|---|
| <AC-1, as the spec words it> | <the test by name, or the command> | <passed> |

## Change

<each changed file marked A, M or D; for one file, a single "Change:" line>

## Checklist

- [ ] Tests: <the planted cases under `tests/fixtures/` added or changed for each check; or none, and why>
- [ ] Docs: <`README.md`, `CONTRIBUTING.md`, `PRINCIPLES.md` or a plugin README changed; or none, and why>
- [ ] Rules: <each new or changed rule has the operator's yes and a row in `docs/rulebook/approved-rules.md`; or none>
- [ ] Formats: <a released format changed as a new `-vN` file, and what a tool must learn to read it; or none>
- [ ] Generic: no project name, provenance or history note in `plugins/`; no `version` or `CHANGELOG*.md` edited by hand
- [ ] Checks: `make index`, `make lint` and `make test` green
- [ ] Release: <which plugin this releases, and as what, by the title's type; or nothing ships>

Closes #<issue>
