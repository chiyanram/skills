# Changelog

What the `rulebook` plugin ships, by version. The format follows [Keep a Changelog](https://keepachangelog.com/), and
versions follow [Semantic Versioning](https://semver.org/). Design work under `research/` and `review/` is not listed
here: it ships nothing.

## 0.1.0 (unreleased)

The version both manifests carry. No release is tagged yet.

### Added

- The `chiyanram` marketplace and the `rulebook` plugin (G23 #93).
- `testing` references: strategy, value-bar, coverage-design, boundaries, unit-tests, spock, integration-tests,
  scenario-to-tests, property-based and mutation, with example files for strategy, spock and integration-tests
  (agent-factory#31).
- `make lint` checks: skill frontmatter, one version, links, size budgets, packaging, the plugin README index, and
  `claude plugin validate --strict` (#111).
- CI runs `make lint` and `make test` on every pull request and every push to `main`.
