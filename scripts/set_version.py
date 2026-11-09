"""Write one plugin's version into its marketplace entry and its plugin.json.

semantic-release runs it in its prepare step, once per plugin (release.config.mjs). It edits the `"version"` value in
place, so the rest of each file keeps its formatting, then reads the files back to prove only that plugin moved.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
VERSION_FIELD = re.compile(r'("version"\s*:\s*")[^"]*(")')
ENTRY = re.compile(r"\{[^{}]*\}")


def listed(root: Path) -> dict[str, dict]:
    return {e["name"]: e for e in json.loads((root / MARKETPLACE).read_text()).get("plugins", [])}


def set_text(text: str, version: str, plugin: str | None = None) -> str | None:
    """`text` with the version set: of the entry named `plugin`, or of the whole file. None when there is none."""
    for match in ENTRY.finditer(text) if plugin else [re.match(r"[\s\S]*", text)]:
        if plugin and plugin not in re.findall(r'"name"\s*:\s*"([^"]*)"', match.group(0)):
            continue
        edited, count = VERSION_FIELD.subn(rf"\g<1>{version}\g<2>", match.group(0), count=1)
        if count:
            return text[:match.start()] + edited + text[match.end():]
    return None


def set_version(root: Path, version: str, plugin: str) -> list[str]:
    if not SEMVER.match(version):
        return [f"`{version}` is not a semantic version such as 1.2.3"]
    before = {name: entry.get("version") for name, entry in listed(root).items()}
    if plugin not in before:
        return [f"{MARKETPLACE}: no plugin `{plugin}`; plugins are {', '.join(before)}"]
    manifest = root / listed(root)[plugin]["source"] / ".claude-plugin" / "plugin.json"
    for path, scope in ((root / MARKETPLACE, plugin), (manifest, None)):
        text = set_text(path.read_text(), version, scope)
        if text is None:
            return [f"{path}: no version field to set for `{plugin}`"]
        path.write_text(text)
    after = {name: entry.get("version") for name, entry in listed(root).items()}
    if after != {**before, plugin: version} or json.loads(manifest.read_text()).get("version") != version:
        return [f"versions are {after} and {manifest} says {json.loads(manifest.read_text()).get('version')}"]
    return []


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("version")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--plugin", required=True, help="the marketplace name of the plugin to release")
    args = parser.parse_args()
    found = set_version(Path(args.root), args.version, args.plugin)
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
