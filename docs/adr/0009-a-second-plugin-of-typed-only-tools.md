# 9. A second plugin, `toolbox`, of typed-only tools

Status: accepted (operator, 2026-11-09, #231)

Amends [ADR-0001](0001-one-plugin-one-folder-ships.md), [ADR-0005](0005-provenance-only-in-the-ledger.md) and
[ADR-0007](0007-releases-cut-from-commit-messages.md).

## Context

The operator picked a few tools from outside skill repos for this repo and others (#223, 2026-11-07): `correct`,
`software-factory`, `loop-me` with `grilling`, and a diagram brief built from `mermaidiff`'s method. They are not
rules. They do not belong in `rulebook`, whose skills load on their own when the work matches. The operator decided:

- they live in a new plugin, `toolbox@chiyanram`, in this repo beside `rulebook`;
- every skill in it is typed-only (`disable-model-invocation: true`), so it runs only when a person types it;
- no Grok or Cursor defaults, and no push or merge;
- each skill notes its source repo, commit and licence;
- a tool joins only after it is read in full, tied to a real moment in our work, and tried once on a named task.

ADR-0001 says the repo ships one plugin. ADR-0005 keeps every source out of `plugins/`. ADR-0007 releases one plugin.
The copied tools are MIT-licensed, and MIT asks that the copyright and permission notice go with every copy.

## Decision

The repo ships two plugins from their own folders: `rulebook` from `plugins/rulebook/` and `toolbox` from
`plugins/toolbox/`. The marketplace has one entry for each. Nothing outside those two folders ships.

**(a) Releases.** The toolbox has its own version, tag and changelog, from the same semantic-release setup.

- A commit scoped `toolbox` releases only the toolbox: `feat(toolbox)` is a minor, `fix(toolbox)` a patch.
- Every other scope that ships releases only the rulebook, as today. `research`, `review` and `repo` release nothing.
- `release.config.mjs` takes the plugin to release, and CI runs semantic-release once for each plugin.
- Tags are `rulebook--v<version>` and `toolbox--v<version>`, the form `claude plugin tag` uses.
- The toolbox changelog is `CHANGELOG-toolbox.md` at the root, beside the rulebook's. Neither ships.
- `check_versions.py` checks each plugin's marketplace entry against its own `plugin.json`. `set_version.py` writes one
  plugin's version.
- A squash merge has one scope, so a pull request changes one plugin.

**(b) Checks.** `make lint` and `make test` cover the toolbox as follows.

| check | for the toolbox |
|---|---|
| `check_skills.py`, `check_links.py`, `check_plugin.py`, `check_index.py`, `check_routers.py` | apply as they are |
| `check_versions.py` | applies, one version per plugin (a) |
| `check_sizes.py` | applies. The toolbox ships no `references/` folder, so the rule-word budget never fires; a copied skill's other files sit beside its `SKILL.md`, as in its source |
| `check_provenance.py` | applies to every toolbox `SKILL.md`. It skips the files beside it, whose links are the tool's own content |
| `check_routing.py` | skips a typed-only skill. Its description is not in the model's context and nothing routes to it |
| `check_ledger.py`, `check_process.py` | nothing to check: the toolbox has no rules and no process files |
| `claude plugin validate --strict` | runs on `plugins/toolbox` too |
| new `check_toolbox.py` | fails when a toolbox `SKILL.md` lacks `disable-model-invocation: true`; when a toolbox skill has no section in the notices file; or when a toolbox file holds a `git push`, a `gh pr merge`, a `.cursor/` path or a Grok model |

`make test` adds planted fixtures for each `check_toolbox.py` failure, for the `check_routing.py` skip and the
`check_provenance.py` scope, and a release-config test for each plugin. A toolbox skill has no role evals; its trial
result on #231 is its evidence.

**(c) Licence notices.** Each copied skill's source and licence go in one file,
`plugins/toolbox/THIRD_PARTY_NOTICES.md`, and nowhere else in the plugin.

- It has one section per skill: the source repo, the path, the pinned commit, the licence, and what we changed.
- Each licence's text follows once, with each holder's copyright line.
- It ships with the plugin, because the licence asks for the notice in every copy.
- `SKILL.md` bodies carry no source, credit or licence line. `check_provenance.py` keeps them clean.
- The rule of ADR-0005 still holds for `rulebook`. For the toolbox, this file is the one shipped place for provenance.

## Alternatives

- **(a) No version of its own**: the toolbox carries none, or rides the rulebook's version and changelog. Rejected.
  With none, users never see an update (ADR-0007). Riding the rulebook's version bumps the toolbox on every rulebook
  release with nothing changed, and a `rulebook--v` tag would name a toolbox release.
- **(b) Run the rulebook's checks unchanged.** Rejected. `check_routing.py` would demand routing cases for skills the
  router never sees. `check_provenance.py` would fail the vendor links in `software-factory`'s surveys, which are the
  tool itself.
- **(c) A source and licence line in each `SKILL.md`.** Rejected. It costs context on every run, it is the provenance
  ADR-0005 keeps out, and `check_provenance.py` would have to allow it in every skill.

## Consequences

- A project installs `rulebook`, `toolbox` or both. Neither depends on the other.
- A toolbox skill never loads on its own. A person types it, and it changes nothing the rulebook says.
- Removing a tool is a `fix(toolbox)` or a breaking `feat(toolbox)!` that drops its folder and its notice section.
- When accepted, ADR-0001, 0005 and 0007 get an "Amended by ADR-0009" line, and `AGENTS.md`, `CONTRIBUTING.md` and
  `README.md` stop saying the repo ships one plugin.
