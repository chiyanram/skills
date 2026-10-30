"""Each plugin README links every reference its skills ship, so the README's table never drifts from the files."""
import json
import sys
from pathlib import Path

from check_links import LINK, prose_lines

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def linked(readme: Path) -> set[Path]:
    targets = {target.split("#", 1)[0] for _, line in prose_lines(readme.read_text()) for target in LINK.findall(line)}
    return {(readme.parent / target).resolve() for target in targets if target}


def plugin_problems(root: Path, entry: dict) -> list[str]:
    folder = root / entry["source"]
    readme = folder / "README.md"
    if not readme.is_file():
        return []  # check_plugin reports the missing README
    listed = linked(readme)
    return [f"{readme}: reference `{reference.relative_to(folder)}` is not linked"
            for reference in sorted(folder.glob("skills/*/references/*.md")) if reference.resolve() not in listed]


def problems(root: Path) -> list[str]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    return [p for entry in entries for p in plugin_problems(root, entry)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
