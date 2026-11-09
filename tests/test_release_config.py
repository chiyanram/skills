import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.support import ROOT

MARKETPLACE = ".claude-plugin/marketplace.json"
PLUGINS = ("rulebook", "toolbox")

# commit -> (rulebook release, toolbox release). The rulebook column is what the one-plugin config released.
MATRIX = {
    "feat(crq): a rule": ("minor", None),
    "fix(testing): a wrong example": ("patch", None),
    "feat(crq)!: rename a rule id": ("major", None),
    "feat: no scope": ("minor", None),
    "feat(research): design work": (None, None),
    "docs(repo): an adr": (None, None),
    "feat(toolbox): a tool": (None, "minor"),
    "fix(toolbox): a tool's step": (None, "patch"),
    "feat(toolbox)!: drop a tool": (None, "major"),
}

LOAD = """
import { releaseConfig } from './release.config.mjs'
console.log(JSON.stringify(Object.fromEntries(JSON.parse(process.argv[1]).map((p) => [p, releaseConfig(p)]))))
"""

ANALYZE = """
import { analyzeCommits } from '@semantic-release/commit-analyzer'
import { releaseConfig } from './release.config.mjs'
const [plugins, messages] = JSON.parse(process.argv[1])
const logger = { log() {}, error() {} }
const out = {}
for (const plugin of plugins) {
  const [, options] = releaseConfig(plugin).plugins.find((p) => p[0] === '@semantic-release/commit-analyzer')
  out[plugin] = {}
  for (const message of messages)
    out[plugin][message] = await analyzeCommits(options, { commits: [{ message, hash: 'abc' }], logger, cwd: process.cwd() })
}
console.log(JSON.stringify(out))
"""

NOTES = """
import { generateNotes } from '@semantic-release/release-notes-generator'
import { releaseConfig } from './release.config.mjs'
const logger = { log() {}, error() {} }
const commits = ['feat(crq): a rule (#1)', 'feat(toolbox): a tool (#2)']
  .map((message, i) => ({ message, hash: `abc${i}`, commit: { short: `abc${i}` }, committerDate: '2026-01-01' }))
const out = {}
for (const plugin of JSON.parse(process.argv[1])) {
  const [, options] = releaseConfig(plugin).plugins.find((p) => p[0] === '@semantic-release/release-notes-generator')
  out[plugin] = await generateNotes(options, { commits, logger, cwd: process.cwd(),
    options: { repositoryUrl: 'https://github.com/chiyanram/skills.git' },
    lastRelease: { gitTag: `${plugin}--v0.1.0` }, nextRelease: { gitTag: `${plugin}--v0.2.0`, version: '0.2.0' } })
}
console.log(JSON.stringify(out))
"""


def node(script: str, argument, env: dict | None = None) -> dict:
    result = subprocess.run(["node", "--input-type=module", "-e", script, json.dumps(argument)], cwd=ROOT,
                            capture_output=True, text=True, env={**os.environ, **(env or {})})
    if result.returncode:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def plugin_options(config: dict, name: str) -> dict:
    return next(p[1] for p in config["plugins"] if isinstance(p, list) and p[0] == name)


class ReleaseConfigTest(unittest.TestCase):
    """release.config.mjs releases each plugin on its own line and stays in step with the manifests it bumps."""

    @classmethod
    def setUpClass(cls):
        cls.configs = node(LOAD, PLUGINS)
        cls.entries = json.loads((ROOT / MARKETPLACE).read_text())["plugins"]

    def test_should_have_no_other_config_that_semantic_release_would_load_first(self):
        # cosmiconfig takes package.json "release" and every .releaserc* ahead of release.config.mjs.
        self.assertNotIn("release", json.loads((ROOT / "package.json").read_text()))
        self.assertEqual(sorted(p.name for p in ROOT.glob(".releaserc*")), [])
        self.assertEqual(sorted(p.name for p in ROOT.glob(".config/releaserc*")), [])

    def test_should_release_the_rulebook_when_no_plugin_is_named(self):
        default = node("import c from './release.config.mjs'; console.log(JSON.stringify(c))", None,
                       env={"RELEASE_PLUGIN": ""})
        self.assertEqual(default, self.configs["rulebook"])

    def test_should_release_each_commit_for_its_own_plugin_only(self):
        got = node(ANALYZE, [PLUGINS, list(MATRIX)])
        for message, expected in MATRIX.items():
            for plugin, release in zip(PLUGINS, expected):
                with self.subTest(plugin=plugin, commit=message):
                    self.assertEqual(got[plugin][message], release)

    def test_should_list_only_its_own_commits_in_the_release_notes(self):
        notes = node(NOTES, PLUGINS)
        self.assertIn("a rule", notes["rulebook"])
        self.assertNotIn("a tool", notes["rulebook"])
        self.assertIn("a tool", notes["toolbox"])
        self.assertNotIn("a rule", notes["toolbox"])

    def test_should_tag_as_claude_plugin_tag_does(self):
        # `claude plugin tag` and dependency version ranges both use <plugin-name>--v<version>.
        for plugin in PLUGINS:
            with self.subTest(plugin):
                self.assertEqual(self.configs[plugin]["tagFormat"], f"{plugin}--v${{version}}")

    def test_should_keep_the_rulebook_release_as_it_was(self):
        config = self.configs["rulebook"]
        self.assertEqual(plugin_options(config, "@semantic-release/changelog")["changelogFile"], "CHANGELOG.md")
        self.assertEqual(plugin_options(config, "@semantic-release/git")["message"],
                         "chore(release): rulebook ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}")

    def test_should_commit_every_manifest_it_bumps(self):
        for entry in self.entries:
            with self.subTest(entry["name"]):
                config = self.configs[entry["name"]]
                assets = set(plugin_options(config, "@semantic-release/git")["assets"])
                changelog = plugin_options(config, "@semantic-release/changelog")["changelogFile"]
                manifest = f"{entry['source'].removeprefix('./')}/.claude-plugin/plugin.json"
                self.assertLessEqual({MARKETPLACE, manifest, changelog}, assets)

    def test_should_keep_the_changelog_title_the_file_starts_with(self):
        for plugin in PLUGINS:
            options = plugin_options(self.configs[plugin], "@semantic-release/changelog")
            changelog = ROOT / options["changelogFile"]
            if changelog.is_file():  # the first release writes it
                with self.subTest(plugin):
                    self.assertTrue(changelog.read_text().startswith(options["changelogTitle"] + "\n"))

    def test_should_bump_only_its_own_plugin_in_the_prepare_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / ".claude-plugin", root / ".claude-plugin")
            for entry in self.entries:
                source = entry["source"].removeprefix("./")
                shutil.copytree(ROOT / source / ".claude-plugin", root / source / ".claude-plugin")
            before = {e["name"]: e["version"] for e in self.entries}
            for entry in self.entries:
                command = plugin_options(self.configs[entry["name"]], "@semantic-release/exec")["prepareCmd"]
                args = command.replace("${nextRelease.version}", "9.9.9").split()
                self.assertEqual(args[:2], ["python3", "scripts/set_version.py"])
                result = subprocess.run([sys.executable, str(ROOT / args[1]), *args[2:]], cwd=root,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                after = {e["name"]: e["version"] for e in json.loads((root / MARKETPLACE).read_text())["plugins"]}
                self.assertEqual(after, {**before, entry["name"]: "9.9.9"})
                before = after


if __name__ == "__main__":
    unittest.main()
