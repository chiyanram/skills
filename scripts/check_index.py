"""Each plugin README links every skill, so a skill is never missing from its plugin's list. A plugin that ships
hooks/index.txt has the same text in the root README's AGENTS.md block, which `make index` writes.

A plugin with no README is skipped: check_plugin reports it.
"""
import json
import sys
from pathlib import Path

from agents_index import README, built
from check_links import LINK, prose_lines

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def linked(readme: Path) -> set[Path]:
    targets = {target.split("#", 1)[0] for _, line in prose_lines(readme.read_text()) for target in LINK.findall(line)}
    return {(readme.parent / target).resolve() for target in targets if target}


def agents_index_problems(root: Path, folder: Path) -> list[str]:
    found = built(root, folder)
    if found is None:
        return []
    current, updated = found
    if updated is None:
        return [f"{root / README}: no AGENTS.md block for {folder.name}'s hooks/index.txt; add the `make index` markers"]
    return [] if updated == current else [f"{root / README}: AGENTS.md block is stale; run `make index`"]


def plugin_problems(root: Path, entry: dict) -> list[str]:
    folder = root / entry["source"]
    readme = folder / "README.md"
    if not readme.is_file():
        return []
    listed = linked(readme)
    unlinked = [f"{readme}: skill `{skill.relative_to(folder)}` is not linked"
                for skill in sorted(folder.glob("skills/*/SKILL.md")) if skill.resolve() not in listed]
    return unlinked + agents_index_problems(root, folder)


def problems(root: Path) -> list[str]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    return [p for entry in entries for p in plugin_problems(root, entry)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
