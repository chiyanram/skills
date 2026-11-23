---
description: Sort and delete the code comments that check_comments.py bans, file an issue for each hack a comment excused, and shrink scripts/comment-baseline.json.
disable-model-invocation: true
---

# Delete comments

Code says what it does. `scripts/check_comments.py` keeps a comment only when the code cannot say it; its docstring
lists what it keeps. This command deletes the rest.

## Scope

Use the files or folder the operator names: $ARGUMENTS. Otherwise use the files in `scripts/comment-baseline.json`,
largest count first. Work in your own worktree, as the `AGENTS.md` MUSTs say.

## Steps

1. List the banned lines: `python3 scripts/check_comments.py .`. Each finding names the file and its line numbers.
2. Sort each comment, and act:

   | kind | test | action |
   |---|---|---|
   | tautology | the code, its name or its type already says it | delete |
   | stale | it names code or behaviour that is not true now (read the code) | delete |
   | excuse | it explains away a hack, a "for now", a gap, a cast or a symptom guard | delete, and note the hack |
   | decision record | a true, non-obvious why that code cannot show | one or two sentences in the module docstring or header; an ADR draft only when it spans modules |

   If you are not sure, delete. Do not make a comment shorter to keep it. Do not add a link to keep one.
3. Edit comments only. Read the diff line by line: any change outside a comment or a docstring is a code change, so
   undo it.
4. File one issue for each module with excuses (`type:task`, per `docs/agents/issue-tracker.md`). Name each hack's
   symbol, what it does, and the fix. Put each ADR draft in the issue for the operator.
5. Run `python3 scripts/check_comments.py --shrink .`, then `make lint` and `make test`.
6. Report: lines deleted, the baseline before and after, the issues filed, the ADR drafts, and the comments you kept
   with a doubt.
