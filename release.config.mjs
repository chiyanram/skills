// semantic-release config, one release line per plugin (ADR-0009). A module, not JSON, because the release notes need
// their own templates and transform, which live in scripts/release_notes.mjs (#276).
// RELEASE_PLUGIN picks the plugin; CI runs it once for each. Scope `toolbox` releases only the toolbox (ADR-0009).
import { releaseNotes } from './scripts/release_notes.mjs'

const DESIGN = ['research', 'review', 'repo'].map((scope) => ({ scope, release: false }))

// commit-analyzer keeps the highest release among matching rules, and a later `false` beats an earlier one, so the
// catch-all comes first: every commit is "no release" unless a toolbox-scoped rule below raises it.
const TOOLBOX_ONLY = [
  { release: false },
  { breaking: true, scope: 'toolbox', release: 'major' },
  { revert: true, scope: 'toolbox', release: 'patch' },
  { type: 'feat', scope: 'toolbox', release: 'minor' },
  { type: 'fix', scope: 'toolbox', release: 'patch' },
  { type: 'perf', scope: 'toolbox', release: 'patch' },
]

const PLUGINS = {
  rulebook: {
    releaseRules: [...DESIGN, { scope: 'toolbox', release: false }],
    keep: (scope) => scope !== 'toolbox',
    changelogFile: 'CHANGELOG.md',
    changelogTitle:
      '# Changelog\n\nWhat the `rulebook` plugin ships, by version. semantic-release writes this file from the commit messages on\n`main`; do not edit it by hand. Design work under `research/` and `review/` ships nothing and is not listed.',
  },
  toolbox: {
    releaseRules: TOOLBOX_ONLY,
    keep: (scope) => scope === 'toolbox',
    changelogFile: 'CHANGELOG-toolbox.md',
    changelogTitle:
      '# Changelog\n\nWhat the `toolbox` plugin ships, by version. semantic-release writes this file from the `toolbox`-scoped\ncommit messages on `main`; do not edit it by hand.',
  },
}

export function releaseConfig(plugin) {
  const settings = PLUGINS[plugin]
  if (!settings) throw new Error(`RELEASE_PLUGIN must be one of ${Object.keys(PLUGINS).join(', ')}, not ${plugin}`)
  return {
    branches: ['main'],
    tagFormat: `${plugin}--v\${version}`,
    plugins: [
      ['@semantic-release/commit-analyzer', { preset: 'conventionalcommits', releaseRules: settings.releaseRules }],
      ['@semantic-release/release-notes-generator', releaseNotes(plugin, settings.keep)],
      ['@semantic-release/changelog', { changelogFile: settings.changelogFile, changelogTitle: settings.changelogTitle }],
      ['@semantic-release/exec', { prepareCmd: `python3 scripts/set_version.py \${nextRelease.version} . --plugin ${plugin}` }],
      [
        '@semantic-release/git',
        {
          assets: [settings.changelogFile, '.claude-plugin/marketplace.json', `plugins/${plugin}/.claude-plugin/plugin.json`],
          message: `chore(release): ${plugin} \${nextRelease.version} [skip ci]\n\n\${nextRelease.notes}`,
        },
      ],
      '@semantic-release/github',
    ],
  }
}

export default releaseConfig(process.env.RELEASE_PLUGIN || 'rulebook')
