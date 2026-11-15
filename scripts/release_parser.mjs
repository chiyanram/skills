// How release.config.mjs and scripts/release_notes.mjs read a commit message. Only `type(scope)!:` or a footer line
// that starts with an upper-case `BREAKING CHANGE: ` or `BREAKING-CHANGE: ` is breaking, as Conventional Commits
// defines it. The parser's default notes pattern ignores case and skips leading `*`, `|` and spaces, so a PR body's
// prose line such as `**Breaking change:** no.` would count as breaking and cut a major release.
const NOTE_KEYWORDS = ['BREAKING CHANGE', 'BREAKING-CHANGE']

export const parserOpts = {
  noteKeywords: NOTE_KEYWORDS,
  notesPattern: (keywords) => new RegExp(`^(${keywords}): (.*)`),
}
