"""Rewrites the root README's AGENTS.md block from each plugin's hooks/index.txt (`make index`)."""
import json
import sys
from pathlib import Path

from agents_index import README, built

MARKETPLACE = Path(".claude-plugin/marketplace.json")


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
    found = [p for entry in entries for p in build_agents_index(root, root / entry["source"])]
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
