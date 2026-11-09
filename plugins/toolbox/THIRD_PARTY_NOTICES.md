# Third-party notices

Each toolbox skill below is copied or adapted from another repo. This file is the one place in the plugin that says
where each came from, at which commit, under which licence, and what we changed (ADR-0009). The licence texts follow.

## correct

- Source: cursor/plugins, `pstack/skills/correct/SKILL.md` (pstack)
- Commit: 2776ddd2355d6d6c8747d3964600f28daf62f049
- Licence: MIT, Copyright (c) 2026 Lauren Tan
- Changes: it proposes each fix and commits only what the operator approves; it leaves sharing commits to the operator.

## grilling

- Source: mattpocock/skills, `skills/productivity/grilling/SKILL.md`
- Commit: 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d
- Licence: MIT, Copyright (c) 2026 Matt Pocock
- Changes: one question at a time instead of a round, in plain words without the skill's own terms; typed-only.

## loop-me

- Source: mattpocock/skills, `skills/in-progress/loop-me/SKILL.md` (in progress upstream)
- Commit: 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d
- Licence: MIT, Copyright (c) 2026 Matt Pocock
- Changes: it reads the toolbox `grilling` skill as a file, because a typed-only skill cannot invoke another; one
  question at a time, in plain words.

## diagram-brief

- Source: osmangoninahid/mermaidiff, `skill/SKILL.md` and `skill/format.md`
- Commit: 688dd59c25f94867e6b611f2d5391b7864395a2c
- Licence: MIT, Copyright (c) 2026 Osman Goni Nahid
- Changes: its method only, rewritten: a `diff` call tree instead of a coloured sequence diagram, with proof,
  message vs diff, callers and may-break parts. None of its text, code, collector or viewer is copied.

## MIT License

Applies to every section above, each with its own copyright line:

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
