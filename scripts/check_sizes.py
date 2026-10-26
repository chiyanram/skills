"""Size budgets from agent-factory docs/adr/0003-rulebook-layout-across-tools.md.

- root AGENTS.md under 200 lines (ADR-0003:14)
- each rule in a reference's `## Rules` section at most 35 words (ADR-0003:20-21)
- each root-to-leaf AGENTS.md chain within Codex's 32 KiB (G20; agent-factory research/22:11,22)
"""
import re
import sys
from pathlib import Path

from repo_files import files

ROOT_AGENTS_MAX_LINES = 199
RULE_MAX_WORDS = 35
CHAIN_MAX_BYTES = 32 * 1024
LIST_ITEM = re.compile(r"^(?:[-*+]|\d+\.)\s+")


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


def rules(reference: Path) -> list[str]:
    section = re.split(r"^## ", reference.read_text(), flags=re.M)
    body = next((s for s in section if s.startswith("Rules\n")), "")
    items = re.split(r"^(?=(?:[-*+]|\d+\.)\s)", body.split("\n", 1)[-1], flags=re.M)
    return [LIST_ITEM.sub("", item).strip() for item in items if LIST_ITEM.match(item)]


def long_rules(root: Path) -> list[str]:
    references = [f for f in files(root, "*.md") if f.parent.name == "references" and f.parent.parent.parent.name == "skills"]
    return [f"{ref}: rule is {len(rule.split())} words, over {RULE_MAX_WORDS}: {rule[:60]}…"
            for ref in references for rule in rules(ref) if len(rule.split()) > RULE_MAX_WORDS]


def problems(root: Path) -> list[str]:
    return root_agents(root) + chains(root) + long_rules(root)


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
