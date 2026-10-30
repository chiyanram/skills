"""Write one version into every manifest: each marketplace plugin entry and each plugin.json.

semantic-release runs it in its prepare step (.releaserc.json). It edits the `"version"` value in place, so the rest of
each file keeps its formatting, then reads the files back to prove the edit landed.
"""
import json
import re
import sys
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
VERSION_FIELD = re.compile(r'("version"\s*:\s*")[^"]*(")')


def manifests(root: Path) -> list[Path]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    return [root / MARKETPLACE] + [root / entry["source"] / ".claude-plugin" / "plugin.json" for entry in entries]


def set_version(root: Path, version: str) -> list[str]:
    if not SEMVER.match(version):
        return [f"`{version}` is not a semantic version such as 1.2.3"]
    found = []
    for manifest in manifests(root):
        text, count = VERSION_FIELD.subn(rf"\g<1>{version}\g<2>", manifest.read_text())
        if not count:
            found.append(f"{manifest}: no version field to set")
            continue
        manifest.write_text(text)
        json.loads(text)
    return found


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: set_version.py <version> [root]")
    found = set_version(Path(sys.argv[2] if len(sys.argv) > 2 else "."), sys.argv[1])
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
