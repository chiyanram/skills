"""Every SKILL.md has `name` and `description`; `name` equals its folder; `description` is at most 1024 characters."""
import sys
from pathlib import Path

from repo_files import files

MAX_DESCRIPTION = 1024
BLOCK_SCALARS = (">", "|", ">-", "|-")


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---" or "---" not in lines[1:]:
        return {}
    fields: dict[str, str] = {}
    key = ""
    for line in lines[1:lines.index("---", 1)]:
        if line[:1] in (" ", "\t") and key:
            fields[key] = (fields[key] + " " + line.strip()).strip()
        elif ":" in line:
            key, value = (part.strip() for part in line.split(":", 1))
            fields[key] = "" if value in BLOCK_SCALARS else value.strip("\"'")
    return fields


def problems_in(skill: Path) -> list[str]:
    fields = frontmatter(skill.read_text())
    folder = skill.parent.name
    found = [f"{skill}: missing `{key}` in frontmatter" for key in ("name", "description") if not fields.get(key)]
    if fields.get("name") and fields["name"] != folder:
        found.append(f"{skill}: name `{fields['name']}` differs from its folder `{folder}`")
    if len(fields.get("description", "")) > MAX_DESCRIPTION:
        found.append(f"{skill}: description is {len(fields['description'])} characters, over {MAX_DESCRIPTION}")
    return found


def problems(root: Path) -> list[str]:
    return [p for skill in files(root, "SKILL.md") for p in problems_in(skill)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
