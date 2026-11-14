"""The toolbox plugin holds typed-only tools, each with its licence notice, and none that pushes or merges.

Fails when a toolbox `SKILL.md` lacks `disable-model-invocation: true`; when a toolbox skill has no section in
`THIRD_PARTY_NOTICES.md` naming its source, commit and licence and is not listed under its `## Written here` section;
when that list names no toolbox skill; or when a toolbox file holds a `git push`, a `gh pr merge`, a `.cursor/` path or
a Grok model. A repo without `plugins/toolbox/` passes.
"""
import re
import sys
from pathlib import Path

from check_skills import frontmatter

TOOLBOX = Path("plugins/toolbox")
NOTICES = "THIRD_PARTY_NOTICES.md"
NOTICE_FIELDS = ("Source:", "Commit:", "Licence:")
WRITTEN_HERE = "Written here"
LISTED = re.compile(r"^- +`?([\w-]+)`?", re.M)
FORBIDDEN = [
    (re.compile(r"\bgit\s+push\b"), "a `git push`"),
    (re.compile(r"\bgh\s+pr\s+merge\b"), "a `gh pr merge`"),
    (re.compile(r"(?<![\w-])\.cursor/"), "a `.cursor/` path"),
    (re.compile(r"\bgrok-[\w.-]+", re.I), "a Grok model"),
]


def notice_sections(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    parts = re.split(r"^## +", path.read_text(), flags=re.M)[1:]
    return {part.split("\n", 1)[0].strip().strip("`"): part for part in parts}


def written_here(sections: dict[str, str]) -> set[str]:
    """The skills this repo wrote, listed one per `- name` line under `## Written here`: they need no notice."""
    return set(LISTED.findall(sections.get(WRITTEN_HERE, "")))


def skill_problems(skill: Path, sections: dict[str, str], notices: Path) -> list[str]:
    router = skill / "SKILL.md"
    found = []
    if frontmatter(router.read_text()).get("disable-model-invocation") != "true":
        found.append(f"{router}: a toolbox skill must be typed-only; add `disable-model-invocation: true`")
    if skill.name in written_here(sections):
        return found
    section = sections.get(skill.name)
    if section is None:
        found.append(f"{notices}: no `## {skill.name}` section with its source, commit and licence, and not listed "
                     f"under `## {WRITTEN_HERE}`")
    else:
        found += [f"{notices}: section `{skill.name}` has no `{field}` line" for field in NOTICE_FIELDS
                  if field not in section]
    return found


def forbidden(path: Path) -> list[str]:
    try:
        lines = path.read_text().splitlines()
    except UnicodeDecodeError:
        return []
    return [f"{path}:{number}: {what} in a toolbox file" for number, line in enumerate(lines, 1)
            for pattern, what in FORBIDDEN if pattern.search(line)]


def problems(root: Path) -> list[str]:
    folder = root / TOOLBOX
    if not folder.is_dir():
        return []
    notices = folder / NOTICES
    sections = notice_sections(notices)
    found = [] if notices.is_file() else [f"{notices} is missing"]
    skills = sorted(router.parent for router in folder.glob("skills/*/SKILL.md"))
    found += [p for skill in skills for p in skill_problems(skill, sections, notices)]
    found += [f"{notices}: `## {WRITTEN_HERE}` lists `{name}`, which is no toolbox skill"
              for name in sorted(written_here(sections) - {skill.name for skill in skills})]
    return found + [p for path in sorted(folder.rglob("*")) if path.is_file() for p in forbidden(path)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
