// semantic-release config. A module, not JSON, because the release notes need a writer transform: the
// conventionalcommits preset links every `#N` in a subject to this repo, and scripts/release_links.mjs points
// `repo#N` and `owner/repo#N` at their own repo.
import { transformWithCrossRepoLinks } from './scripts/release_links.mjs'

export default {
  branches: ['main'],
  tagFormat: 'rulebook--v${version}',
  plugins: [
    [
      '@semantic-release/commit-analyzer',
      {
        preset: 'conventionalcommits',
        releaseRules: [
          { scope: 'research', release: false },
          { scope: 'review', release: false },
          { scope: 'repo', release: false },
        ],
      },
    ],
    [
      '@semantic-release/release-notes-generator',
      { preset: 'conventionalcommits', writerOpts: { transform: transformWithCrossRepoLinks } },
    ],
    [
      '@semantic-release/changelog',
      {
        changelogFile: 'CHANGELOG.md',
        changelogTitle:
          '# Changelog\n\nWhat the `rulebook` plugin ships, by version. semantic-release writes this file from the commit messages on\n`main`; do not edit it by hand. Design work under `research/` and `review/` ships nothing and is not listed.',
      },
    ],
    ['@semantic-release/exec', { prepareCmd: 'python3 scripts/set_version.py ${nextRelease.version}' }],
    [
      '@semantic-release/git',
      {
        assets: ['CHANGELOG.md', '.claude-plugin/marketplace.json', 'plugins/rulebook/.claude-plugin/plugin.json'],
        message: 'chore(release): rulebook ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}',
      },
    ],
    '@semantic-release/github',
  ],
}
