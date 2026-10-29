"""Every manifest carries one version: each marketplace plugin entry and each plugin.json."""
import json
import sys
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def versions(root: Path) -> dict[str, str]:
    market = json.loads((root / MARKETPLACE).read_text())
    found = {}
    for entry in market.get("plugins", []):
        found[f"{MARKETPLACE} plugins[{entry['name']}]"] = entry.get("version", "")
        manifest = Path(entry["source"]) / ".claude-plugin" / "plugin.json"
        found[str(manifest)] = json.loads((root / manifest).read_text()).get("version", "")
    return found


def problems(root: Path) -> list[str]:
    found = versions(root)
    missing = [f"{where}: no version" for where, version in found.items() if not version]
    drift = [f"manifests disagree on version: {found}"] if len(set(found.values()) - {""}) > 1 else []
    return missing + drift


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
