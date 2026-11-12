"""Each plugin carries one version: its marketplace entry and its plugin.json agree. Plugins version apart."""
import json
import sys
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def plugin_problems(root: Path, entry: dict) -> list[str]:
    where = f"{MARKETPLACE} plugins[{entry['name']}]"
    manifest = Path(entry["source"]) / ".claude-plugin" / "plugin.json"
    listed, own = entry.get("version", ""), json.loads((root / manifest).read_text()).get("version", "")
    found = [f"{place}: no version" for place, version in ((where, listed), (str(manifest), own)) if not version]
    if listed and own and listed != own:
        found.append(f"{where} says {listed} but {manifest} says {own}")
    return found


def problems(root: Path) -> list[str]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    return [p for entry in entries for p in plugin_problems(root, entry)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
