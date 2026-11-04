# Development

How to set up the repo, run the checks and find your way around. For how to propose a change, see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Prerequisites

- Python 3.10 or newer. The checks use the standard library only.
- Node `^22.22.2` or `>=24.15`, for the release tooling that `make test` loads.
- The Claude Code CLI, for `claude plugin validate` in `make lint`:
  `npm install -g @anthropic-ai/claude-code`.
- `git` and, for issues, the GitHub CLI `gh`.

## Setup

```bash
git clone https://github.com/chiyanram/skills.git
cd skills
npm ci          # release tooling; nothing in node_modules ships
make check      # lint + test, the same as CI
```

To try your working copy in Claude Code, add the clone as a local marketplace:

```bash
claude plugin marketplace add ./
claude plugin install rulebook@chiyanram
```

## Make targets

| target | what it does |
|---|---|
| `make index` | rebuilds the reference table in each skill's `SKILL.md` from its references |
| `make lint` | runs every `scripts/check_*.py`, then `claude plugin validate --strict` on the repo and on the plugin |
| `make test` | runs the unit tests in `tests/` with `python3 -m unittest` |
| `make check` | `make lint` and `make test`, as CI runs them |
| `make help` | lists the targets |

Set `PYTHON` to use another interpreter, such as `make test PYTHON=python3.12`.

## Running tests

```bash
make test                                               # everything
python3 -m unittest tests.test_fixture_checks           # one module
python3 scripts/check_links.py .                        # one check against the repo
python3 scripts/check_links.py tests/fixtures/links/broken   # one check against a fixture
```

Each check exits `0` when clean and `1` with one line per problem. `tests/test_fixture_checks.py` lists, per check,
the fixtures that must pass and the planted ones that must fail.

To preview the next release, on `main` run `GITHUB_TOKEN=<token> npm run release:preview`.

## Project layout

```text
plugins/rulebook/
  .claude-plugin/plugin.json   plugin manifest; the release bumps its version
  README.md                    lists the skills
  skills/<domain>/SKILL.md     router: frontmatter + generated reference table
  skills/<domain>/references/  one file per topic; examples/ for overflow Good/Bad pairs
.claude-plugin/marketplace.json  the marketplace entry; same version as plugin.json
scripts/
  check_*.py                   one lint check each
  build_index.py, index_table.py   make index, and the table check_index.py compares against
  repo_files.py                the files a check reads (skips tests/fixtures/ and docs/archive/)
  set_version.py               writes the release version into both manifests
  release_links.mjs            cross-repo issue links in release notes
tests/
  test_*.py                    unit tests
  fixtures/<check>/<case>/     planted good and bad repos for each check
docs/
  rulebook/                    the rule ledger, the reference format, moved sources
  agents/                      conventions agent skills read: tracker, labels, domain docs
  archive/                     frozen design history; not checked, not maintained
release.config.mjs             semantic-release
.github/workflows/ci.yml       lint + test on every PR; release on push to main
```

## Troubleshooting

**`make lint` fails with `claude: command not found`.** Install the CLI:
`npm install -g @anthropic-ai/claude-code`.

**`check_index.py` says a table is stale.** Run `make index` and commit the router it rewrote. Never edit the table
by hand.

**`make test` fails in `test_release_config` or `test_release_links`.** Run `npm ci`; the tests load the release
config and its changelog preset from `node_modules`.

**`check_provenance.py` fails on a reference.** Move the citation, URL or date into the rule's ledger row, or wrap a
tool name that is the action itself in backticks.

**`check_sizes.py` says a rule is over 35 words.** Shorten the rule; move detail to When X, use Y or Decided edges.

**`claude plugin marketplace add` fails on clone.** The repo is private: run `gh auth setup-git` so git uses your
GitHub credentials.
