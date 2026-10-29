"""Each plugin ships from its own folder under plugins/, never the repo root, with a README and an icon; the repo has a LICENSE."""
import json
import sys
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")
PLUGINS = Path("plugins")


def plugin_problems(root: Path, entry: dict) -> list[str]:
    source = Path(entry["source"])
    where = f"{MARKETPLACE} plugins[{entry['name']}]"
    if source.parent != PLUGINS:
        return [f"{where}: source `{entry['source']}` is not a folder directly under {PLUGINS}/"]
    folder = root / source
    manifest = json.loads((folder / ".claude-plugin" / "plugin.json").read_text())
    icon = folder / manifest.get("icon", ".claude-plugin/icon.png")
    return [f"{where}: {path} is missing" for path in (folder / "README.md", icon) if not path.is_file()]


def problems(root: Path) -> list[str]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    found = [p for entry in entries for p in plugin_problems(root, entry)]
    if (root / ".claude-plugin" / "plugin.json").exists():
        found.append(f"{root / '.claude-plugin/plugin.json'}: the repo root is itself a plugin and would ship whole")
    if not (root / "LICENSE").is_file():
        found.append(f"{root / 'LICENSE'} is missing")
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
