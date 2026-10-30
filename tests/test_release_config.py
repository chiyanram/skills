import json
import subprocess
import unittest

from tests.support import ROOT

MARKETPLACE = ".claude-plugin/marketplace.json"


def plugin_options(config: dict, name: str) -> dict:
    return next(p[1] for p in config["plugins"] if isinstance(p, list) and p[0] == name)


class ReleaseConfigTest(unittest.TestCase):
    """release.config.mjs stays in step with the manifests it releases."""

    @classmethod
    def setUpClass(cls):
        loaded = subprocess.run(["node", "--input-type=module", "-e",
                                 "import c from './release.config.mjs'; console.log(JSON.stringify(c))"],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        cls.config = json.loads(loaded.stdout)
        cls.entries = json.loads((ROOT / MARKETPLACE).read_text())["plugins"]

    def test_should_have_no_other_config_that_semantic_release_would_load_first(self):
        # cosmiconfig takes package.json "release" and every .releaserc* ahead of release.config.mjs.
        self.assertNotIn("release", json.loads((ROOT / "package.json").read_text()))
        self.assertEqual(sorted(p.name for p in ROOT.glob(".releaserc*")), [])
        self.assertEqual(sorted(p.name for p in ROOT.glob(".config/releaserc*")), [])

    def test_should_tag_as_claude_plugin_tag_does(self):
        # `claude plugin tag` and dependency version ranges both use <plugin-name>--v<version>.
        self.assertEqual(len(self.entries), 1, "one tagFormat cannot release two plugins")
        self.assertEqual(self.config["tagFormat"], f"{self.entries[0]['name']}--v${{version}}")

    def test_should_commit_every_manifest_it_bumps(self):
        manifests = {MARKETPLACE} | {f"{e['source'].removeprefix('./')}/.claude-plugin/plugin.json" for e in self.entries}
        assets = set(plugin_options(self.config, "@semantic-release/git")["assets"])
        self.assertLessEqual(manifests, assets)

    def test_should_keep_the_changelog_title_the_file_starts_with(self):
        title = plugin_options(self.config, "@semantic-release/changelog")["changelogTitle"]
        self.assertTrue((ROOT / "CHANGELOG.md").read_text().startswith(title + "\n"))


if __name__ == "__main__":
    unittest.main()
