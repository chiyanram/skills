import unittest

from tests.test_release_config import node

# The shape of the release notes (#276): emoji sections, one bullet per change
# as `**scope** — subject · #ticket (PR #pr)`, and an update line for the plugin.
NOTES = """
import { generateNotes } from '@semantic-release/release-notes-generator'
import { releaseConfig } from './release.config.mjs'
const logger = { log() {}, error() {} }
const [plugin, messages] = JSON.parse(process.argv[1])
const commits = messages.map((message, i) => ({ message, hash: `abc${i}`, commit: { short: `abc${i}` }, committerDate: '2026-01-01' }))
const [, options] = releaseConfig(plugin).plugins.find((p) => p[0] === '@semantic-release/release-notes-generator')
console.log(JSON.stringify(await generateNotes(options, { commits, logger, cwd: process.cwd(),
  options: { repositoryUrl: 'https://github.com/chiyanram/skills.git' },
  lastRelease: { gitTag: `${plugin}--v0.1.0` }, nextRelease: { gitTag: `${plugin}--v0.2.0`, version: '0.2.0' } })))
"""

REPO = "https://github.com/chiyanram/skills"
COMMITS = [
    "feat(crq): a rule (#10) (#11)",
    "fix(code): a wrong example (chiyanram/other#320) (#12)",
    "perf(code): a faster check (#13)",
    "feat(planning)!: rename a rule id (#14)\n\nBREAKING CHANGE: rule GA3 is removed.\n\n"
    "Co-Authored-By: A Tool <noreply@example.com>\nClaude-Session: https://example.com/s",
    "docs(repo): an adr (#15)",
    "ci(repo): a workflow (#16)",
    "fix(repo): a release-tooling fix (#17)",
    "feat(research): a design note (#18)",
    "feat(review): a review finding (#19)",
]


class ReleaseNotesTest(unittest.TestCase):
    """scripts/release_notes.mjs gives every plugin the same release-note sections and bullet shape."""

    @classmethod
    def setUpClass(cls):
        cls.notes = node(NOTES, ["rulebook", COMMITS])

    def test_should_group_changes_under_emoji_sections(self):
        for section in ("### ⚠️ Breaking changes", "### ✨ Features", "### 🐛 Fixes", "### ⚡ Performance"):
            with self.subTest(section):
                self.assertIn(section, self.notes)

    def test_should_render_one_bullet_with_its_ticket_and_pr(self):
        self.assertIn(f"* **crq** — a rule · [#10]({REPO}/issues/10) (PR [#11]({REPO}/pull/11))", self.notes)

    def test_should_link_a_reference_to_its_own_repo(self):
        self.assertIn("[chiyanram/other#320](https://github.com/chiyanram/other/issues/320)", self.notes)

    def test_should_list_the_breaking_change_under_its_scope(self):
        self.assertIn("* **planning** — rule GA3 is removed.", self.notes)

    def test_should_leave_git_trailers_out_of_a_breaking_change_note(self):
        self.assertNotIn("Co-Authored-By", self.notes)
        self.assertNotIn("Claude-Session", self.notes)

    def test_should_hide_changes_that_ship_nothing(self):
        self.assertNotIn("an adr", self.notes)
        self.assertNotIn("a workflow", self.notes)

    def test_should_hide_design_work_even_when_it_is_a_feat_or_fix(self):
        for subject in ("a release-tooling fix", "a design note", "a review finding"):
            with self.subTest(subject):
                self.assertNotIn(subject, self.notes)

    def test_should_end_with_the_update_command_for_the_plugin(self):
        for plugin in ("rulebook", "toolbox"):
            with self.subTest(plugin):
                notes = node(NOTES, [plugin, [f"feat({plugin}): a change (#1)"]])
                self.assertIn(f"Update: `claude plugin update {plugin}@chiyanram`", notes)


if __name__ == "__main__":
    unittest.main()
