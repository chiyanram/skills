# Contributing

This repo ships two plugins: [`rulebook`](plugins/rulebook/), and [`toolbox`](plugins/toolbox/), typed-only tools.
Coding agents also read [AGENTS.md](AGENTS.md).

**The one hard rule:** no rule enters a skill without the operator's explicit yes. A rule that is not approved stays
out, even when an agent likes it or another repo has it.

## Set up

You need Python 3.10 or newer, Node `^22.22.2` or `>=24.15`, `git`, the GitHub CLI `gh`, and the Claude Code CLI
(`npm install -g @anthropic-ai/claude-code`). The `python3` that macOS ships is 3.9, which fails the checks; install a
newer one and run `PYTHON=python3.12 make check`.

```bash
git clone https://github.com/chiyanram/skills.git
cd skills
npm ci          # release tooling; nothing in node_modules ships
make check      # lint + test, the same as CI; `make help` lists every target
```

To try your working copy in Claude Code: `claude plugin marketplace add ./`, then
`claude plugin install rulebook@chiyanram`.

Each `scripts/check_*.py` says in its docstring what it fails, and runs on one folder:
`python3 scripts/check_links.py tests/fixtures/links/broken`.

## How a change lands

One issue, one branch, one pull request.

1. Open or claim an issue from a template: *Bug*, *Feature*, *Task* or *Grilling*. Labels:
   [triage labels](docs/agents/triage-labels.md).
2. Branch from the latest `main` in its own worktree, never in the main checkout:

   ```bash
   git fetch origin main
   git worktree add .claude/worktrees/123-spock-cleanup -b feat/123-spock-cleanup origin/main
   ```

3. Make the change. Run `make index`, `make lint` and `make test`.
4. Open a pull request against `main` from [the template](.github/pull_request_template.md), with every line filled
   in. CI must be green before merge.
5. To take in a newer `main`, rebase onto it and push with `--force-with-lease`. Never merge `main` into the branch.
   Once it is merged, remove the worktree.

A good pull request does one thing and adds a test with every change to a check. No `version` or `CHANGELOG*.md` is
edited by hand: the release writes them.

## Commit messages

Pull requests are squash-merged, so the commit on `main` is the **PR title** and the **PR description**.

- **Title**: `type(scope): lower-case summary (#issue)`: a type from the [Releases](#releases) table, a lower-case
  scope and imperative summary, and the issue as `(#N)` or `(owner/repo#N)`. `!` after the scope marks a breaking
  change. Check it with `python3 scripts/pr_title.py "<title>"`, as CI does.
- **Description**: the template's shape: the `Why:` line, the breaking-change, rollback and where-to-look lines, the
  evidence, the change and the checklist, footers last. Check it with `python3 scripts/pr_body.py < body.md`.
- **A breaking change** carries three marks that agree: `Breaking change: yes`, `!` after the scope, and a
  `BREAKING CHANGE:` footer. semantic-release reads only the `!` and the footer.
- **No tool or co-author lines**: no `Co-Authored-By`, no "Generated with" line.

## What a skill must be

- **Knowledge only.** A plugin holds instructions, data and small check scripts, never engine code, and it works
  with no engine installed (`check_plugin.py`, `check_generic.py`).
- **One text, two readers.** The writer follows a rule and the reviewer checks that same text. A finding names the
  skill and its section; a rule has no ID.
- **Short, with its reason.** The instruction, then the failure it prevents. Where a rule came from goes in the pull
  request, never in the skill (`check_provenance.py`).
- **One job.** `SKILL.md` is a short procedure, read whole, 120 lines or fewer (`check_skills.py`). A notes file beside
  it holds what only some runs need. A skill that does two jobs becomes two skills.
- **Only what the model would get wrong.** A Good / Bad pair only where the model's default is wrong, in a neutral
  domain, never a real project's names.
- **From our own failures.** A lesson from real use lands as a rule with its reason (`/rulebook:skill-feedback`).
- **A check beats prose.** Where a script or lint can check it, ship the script.
- **Proved no worse.** A skill change ships with eval proof, sized by the skill's tier
  ([Prove a skill change](#prove-a-skill-change)).

A rulebook skill can be loaded by the model; a toolbox skill is typed-only. A skill that another skill calls must be
one the model can load.

## Add a rule or a skill

1. Read the issue, and list what already covers its topic, so the change only fills gaps.
2. Find two independent sources for each part of each rule: a file and line pinned to a commit, or an official doc and
   its section. Read production incidents too.
3. Show the operator one table, one row per rule: the rule as it would ship, where it goes, its sources and your pick.
   The operator's yes starts the work.
4. Write the rule into its skill, with its *because* and any exception inline. Add an eval case that fails without it.
5. Have a fresh reviewer check each rule and Good / Bad pair. A fix that changes a rule's meaning goes back to the
   operator.
6. Open the pull request with `Closes #N` and the sources in its body. The operator merges.

A new skill is a new folder with one row in its plugin README and one in the root README.

## Add a check

1. Plant a failing fixture under `tests/fixtures/<check>/`, or write it to a temp dir when it is a `SKILL.md`.
2. Add it to the test that expects the check to fail. Watch it fail.
3. Write `scripts/check_<name>.py`, with a docstring that says what it fails. Read files through
   `scripts/repo_files.py`, which skips `tests/fixtures/`.
4. Add it to `make lint` in the [Makefile](Makefile).

When review finds a case a check missed, plant that case first and watch it fail, then fix the check.

## Add a tool

A toolbox tool is `plugins/toolbox/skills/<name>/SKILL.md` with `disable-model-invocation: true`, and it never pushes
or merges. Either copy it from another repo and add a `## <name>` section to `plugins/toolbox/THIRD_PARTY_NOTICES.md`
with its `Source:`, `Commit:`, `Licence:` and changes, or write it here and list it under that file's
`## Written here`. Add its row to the [toolbox README](plugins/toolbox/README.md) and title the PR
`feat(toolbox): …`.

## Prove a skill change

A skill change ships with proof that it is no worse: an eval run you can trust, with an approved baseline. Every run is
a real model call, so it runs by hand, never in CI; CI checks the committed proof with `check_eval_proof.py`. The
tiers, the rules for a run and the commands are in [evals/skills/README.md](evals/skills/README.md).

## Releases

A merge to `main` runs the checks only. Releases are manual: `gh workflow run release.yml --ref main` runs the
checks, then semantic-release. The squash-merged PR title decides the release.

| commit | release | use it when |
|---|---|---|
| `feat(<domain>): …` | minor | a new rule or skill |
| `fix(<domain>): …` | patch | a shipped rule, example or check says something wrong |
| `feat(<domain>)!: …`, or a `BREAKING CHANGE:` footer | major | a rule is removed or reversed, or a skill is renamed or removed |
| `docs`, `chore`, `test`, `ci`, `build`, `refactor`, `style` | none | anything that does not change what ships |
| any type with scope `research`, `review` or `repo` | none | design work, even when it is a `feat` |
| `feat(toolbox)`, `fix(toolbox)`, `feat(toolbox)!` | the toolbox only | a tool is added, changed or removed |

Each plugin releases on its own line, so a pull request changes one plugin. A release sets that plugin's version
(`scripts/set_version.py`), writes its changelog, tags `<plugin>--v<version>` and creates a GitHub release. Preview the
next one with `GITHUB_TOKEN=<token> npm run release:preview` (`RELEASE_PLUGIN=toolbox` for the toolbox).

## Troubleshooting

| symptom | fix |
|---|---|
| `make lint`: `claude: command not found` | `npm install -g @anthropic-ai/claude-code` |
| `check_index.py`: the AGENTS.md block is stale | run `make index` and commit the README it rewrote |
| `make test` fails in `test_release_*` | run `npm ci`; the tests load the release config from `node_modules` |
| `check_provenance.py` fails on a skill file | move the citation, URL or date into the pull request body |
| `check_history.py` fails a line you added | say what and why; the PR and git log keep who, when and the issue |
| `check_comments.py` fails a file | say it in code or the module docstring; after you delete comments, run `python3 scripts/check_comments.py --shrink` |
| the release fails with `RELEASE_TOKEN is not set` | add a repository secret `RELEASE_TOKEN`: the owner's token with Contents read and write |

## Code of conduct

Be kind and assume good intent. Critique the change, not the person.
