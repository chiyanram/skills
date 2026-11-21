"""Every SKILL.md has `name` and `description`; `name` equals its folder; `description` is at most 1024 characters;
the file is at most 120 lines; and each one-line frontmatter value parses as strict YAML, as other harnesses read it."""
import sys
from pathlib import Path

from repo_files import files

MAX_DESCRIPTION = 1024
MAX_LINES = 120
BLOCK_SCALARS = (">", "|", ">-", "|-")


PLAIN_START = tuple("[]{}&*!|>'\"%@`#,?-")


def plain_value_problem(value: str) -> str:
    """Why a one-line unquoted YAML value does not parse, or "" when it does. Other harnesses parse strict YAML."""
    if not value or value in BLOCK_SCALARS or value[0] in "\"'":
        return ""
    if ": " in value or value.endswith(":"):
        return "holds `: `; quote the value or use a `>-` block"
    if " #" in value:
        return "holds ` #`, which YAML reads as a comment; quote the value"
    if value.startswith(PLAIN_START):
        return f"starts with `{value[0]}`; quote the value"
    return ""


def frontmatter_problems(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---" or "---" not in lines[1:]:
        return []
    found = []
    for line in lines[1:lines.index("---", 1)]:
        if line[:1] not in (" ", "\t") and ":" in line:
            key, value = (part.strip() for part in line.split(":", 1))
            why = plain_value_problem(value)
            if why:
                found.append(f"`{key}` {why}")
    return found


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
    found += [f"{skill}: frontmatter {why}" for why in frontmatter_problems(skill.read_text())]
    if fields.get("name") and fields["name"] != folder:
        found.append(f"{skill}: name `{fields['name']}` differs from its folder `{folder}`")
    lines = len(skill.read_text().splitlines())
    if lines > MAX_LINES:
        found.append(f"{skill}: {lines} lines, over {MAX_LINES}; move detail into a notes file beside it")
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
