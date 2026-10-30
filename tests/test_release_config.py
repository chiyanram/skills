import json
import unittest

from tests.support import ROOT

MARKETPLACE = ".claude-plugin/marketplace.json"


def plugin_options(config: dict, name: str) -> dict:
    return next(p[1] for p in config["plugins"] if isinstance(p, list) and p[0] == name)


class ReleaseConfigTest(unittest.TestCase):
    """.releaserc.json stays in step with the manifests it releases."""

    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / ".releaserc.json").read_text())
        cls.entries = json.loads((ROOT / MARKETPLACE).read_text())["plugins"]

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
