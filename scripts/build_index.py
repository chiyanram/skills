"""Rewrites the index block of each skill router from its references, and the root README's AGENTS.md block from
each plugin's hooks/index.txt (`make index`).

A skill that ships references with no router is skipped: check_routers reports it.
"""
import json
import sys
from pathlib import Path

from agents_index import README, built
from index_table import table, unreadable, with_table

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def build(skill: Path) -> list[str]:
    router = skill / "SKILL.md"
    if not any(skill.glob("references/*.md")) or not router.is_file():
        return []
    problems = unreadable(skill)
    updated = with_table(router.read_text(), table(skill))
    if updated is None:
        return [*problems, f"{router}: no index block to rewrite"]
    if not problems:
        router.write_text(updated)
    return problems


def build_agents_index(root: Path, folder: Path) -> list[str]:
    found = built(root, folder)
    if found is None:
        return []
    if found[1] is None:
        return [f"{root / README}: no AGENTS.md block for {folder.name}'s hooks/index.txt to rewrite"]
    (root / README).write_text(found[1])
    return []


if __name__ == "__main__":
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    skills = [skill for entry in entries for skill in sorted((root / entry["source"]).glob("skills/*/"))]
    found = [p for skill in skills for p in build(skill)]
    found += [p for entry in entries for p in build_agents_index(root, root / entry["source"])]
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
