"""Size budgets for the agent instructions.

- root AGENTS.md under 200 lines
- each root-to-leaf AGENTS.md chain within Codex's 32 KiB
"""
import sys
from pathlib import Path

from repo_files import files

ROOT_AGENTS_MAX_LINES = 199
CHAIN_MAX_BYTES = 32 * 1024


def root_agents(root: Path) -> list[str]:
    agents = root / "AGENTS.md"
    lines = len(agents.read_text().splitlines()) if agents.is_file() else 0
    return [f"{agents}: {lines} lines, over {ROOT_AGENTS_MAX_LINES}"] if lines > ROOT_AGENTS_MAX_LINES else []


def chains(root: Path) -> list[str]:
    found = []
    for leaf in files(root, "AGENTS.md"):
        ancestors = [d / "AGENTS.md" for d in [leaf.parent, *leaf.parent.parents] if d.is_relative_to(root)]
        size = sum(a.stat().st_size for a in ancestors if a.is_file())
        if size > CHAIN_MAX_BYTES:
            found.append(f"{leaf}: AGENTS.md chain from the root is {size} bytes, over {CHAIN_MAX_BYTES}")
    return found


def problems(root: Path) -> list[str]:
    return root_agents(root) + chains(root)


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
