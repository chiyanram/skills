# Third-party notices

Each toolbox skill below is copied or adapted from another repo. This file is the one place in the plugin that says
where each came from, at which commit, under which licence, and what we changed. The licence texts follow. A skill
written in this repo has no source to name; it is listed under [Written here](#written-here) instead.

## correct

- Source: cursor/plugins, `pstack/skills/correct/SKILL.md` (pstack)
- Commit: 2776ddd2355d6d6c8747d3964600f28daf62f049
- Licence: MIT, Copyright (c) 2026 Lauren Tan
- Changes: it proposes each fix and commits only what the operator approves; it leaves sharing commits to the operator;
  it also reads the traces of agent runs and finds the turns they waste, with a table of waste kinds; it ends with a
  `caught:` line.

## loop-me

- Source: mattpocock/skills, `skills/in-progress/loop-me/SKILL.md` (in progress upstream)
- Commit: 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d
- Licence: MIT, Copyright (c) 2026 Matt Pocock
- Changes: it loads the rulebook's `grilling` skill; one question at a time, in plain words.

## diagram-brief

- Source: osmangoninahid/mermaidiff, `skill/SKILL.md` and `skill/format.md`
- Commit: 688dd59c25f94867e6b611f2d5391b7864395a2c
- Licence: MIT, Copyright (c) 2026 Osman Goni Nahid
- Changes: its method only, rewritten: a `diff` call tree instead of a coloured sequence diagram, with proof,
  message vs diff, callers and may-break parts. None of its text, code, collector or viewer is copied.

## software-factory

- Source: mattpocock/skills, `skills/in-progress/software-factory/` (`SKILL.md` and its surveys; in progress upstream)
- Commit: 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d
- Licence: MIT, Copyright (c) 2026 Matt Pocock
- Changes: none; copied as written, and typed-only upstream.

## onboard

- Source: mattpocock/skills, `skills/engineering/setup-matt-pocock-skills/SKILL.md`
- Commit: 697d4ce9742da558fd1ba6697c8e9775e2e302dd
- Licence: MIT, Copyright (c) 2026 Matt Pocock
- Changes: its method only, rewritten (explore, show a draft, write one block in place in the file that exists). It
  writes the rulebook's block (commands, stack notes, codebase health), not the issue tracker, labels or domain docs.

## create-verification-skill

- Source: cursor/plugins, `pstack/skills/create-verification-skill/` (`SKILL.md` and `references/feature-map-example/`) (pstack)
- Commit: bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7
- Licence: MIT, Copyright (c) 2026 Lauren Tan
- Changes: the generated skill goes in `.claude/skills/verify-<app>/`, not the Cursor folder; it names the maintenance tool
  as `/toolbox:maintain-verification-skill`. The feature-map example is copied as written.

## maintain-verification-skill

- Source: cursor/plugins, `pstack/skills/maintain-verification-skill/SKILL.md` (pstack)
- Commit: bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7
- Licence: MIT, Copyright (c) 2026 Lauren Tan
- Changes: a "changed" pass ends in one commit made with the operator's yes, and the operator pushes it and opens the
  PR, where the source ships a PR itself; `.claude/skills/verify-*/` paths, not the Cursor folder.

## Written here

- `break-design`
- `weigh-source`

## MIT License

Applies to every copied section above, each with its own copyright line:

- Copyright (c) 2026 Lauren Tan
- Copyright (c) 2026 Matt Pocock
- Copyright (c) 2026 Osman Goni Nahid

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
