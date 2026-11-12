// The conventionalcommits preset links every `#N` in a commit subject to this repo, so `other#31` came out
// as a link to chiyanram/skills#31. This rewrites a `repo#N` or `owner/repo#N` link to point at its own repo; a bare
// repo name takes this repo's owner. Footer references (`Closes owner/repo#N`) are already linked right.
const CROSS_REPO = /(?<![\w./-])(?:([\w.-]+)\/)?([\w.-]+)\[#(\d+)\]\([^)\s]*\)/g

export function crossRepoLinks(subject, { host, owner }) {
  return subject.replace(CROSS_REPO, (_, refOwner, repo, issue) => {
    const name = `${refOwner ?? owner}/${repo}`
    return `[${name}#${issue}](${host}/${name}/issues/${issue})`
  })
}

// Each plugin's release notes list only its own commits: `keep(scope)` says whether a commit belongs to it.
export function forScope(keep, transformCommit) {
  return (commit, context) => (keep(commit.scope ?? '') ? transformCommit(commit, context) : null)
}
