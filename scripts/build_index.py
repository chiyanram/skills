"""Rewrites the index block of each skill router from its references, and the lanes blocks of a skill from its
process/lanes-v2.json (`make index`)."""
import json
import sys
from pathlib import Path

from index_table import table, unreadable, with_table
from lanes_render import files

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def build(skill: Path) -> list[str]:
    router = skill / "SKILL.md"
    if not any(skill.glob("references/*.md")) or not router.is_file():
        return []  # check_routers reports a skill that ships references without a router
    problems = unreadable(skill)
    updated = with_table(router.read_text(), table(skill))
    if updated is None:
        return [*problems, f"{router}: no index block to rewrite"]
    if not problems:
        router.write_text(updated)
    return problems


def build_lanes(skill: Path) -> list[str]:
    updated, problems = files(skill)
    for path, text in updated.items():
        path.write_text(text)
    return problems


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    skills = [skill for entry in entries for skill in sorted((root / entry["source"]).glob("skills/*/"))]
    found = [p for skill in skills for p in build(skill) + build_lanes(skill)]  # the lanes blocks read the new router
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
