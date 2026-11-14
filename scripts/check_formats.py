"""A format file a release holds never changes: a change is a new -v(N+1) file beside it.

The newest `rulebook--v*` tag is the release. Every `*-v<N>.schema.json` under a skill's `process/schema/` that the tag
holds must match the working tree byte for byte, and must still be there. A tool pins a release and reads that
version's format, so an edit in place breaks the tool on its next update. A schema no release holds yet may change.
"""
import fnmatch
import re
import subprocess
import sys
from pathlib import Path

TAGS = "rulebook--v*"
SCHEMA = "plugins/*/skills/*/process/schema/*.schema.json"
VERSIONED = re.compile(r"^(?P<name>.+)-v(?P<n>\d+)\.schema\.json$")


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True)


def newest_tag(root: Path) -> str | None:
    listed = git(root, "tag", "--list", TAGS, "--sort=-v:refname")
    tags = listed.stdout.decode().split() if listed.returncode == 0 else []
    return tags[0] if tags else None


def released_formats(root: Path, tag: str) -> list[str]:
    listed = git(root, "ls-tree", "-r", "--name-only", tag, "--", "plugins/").stdout.decode().splitlines()
    return [path for path in listed if fnmatch.fnmatch(path, SCHEMA) and VERSIONED.match(Path(path).name)]


def file_problems(root: Path, tag: str, path: str) -> list[str]:
    released = git(root, "show", f"{tag}:{path}")
    if released.returncode != 0:
        return [f"{path}: cannot read it from {tag}; fetch the full history with `git fetch --unshallow --tags`"]
    current = root / path
    match = VERSIONED.match(current.name)
    successor = f"{match['name']}-v{int(match['n']) + 1}.schema.json"
    if not current.is_file():
        return [f"{path}: removed, but {tag} holds it; a released format stays"]
    if current.read_bytes() != released.stdout:
        return [f"{path}: differs from {tag}; restore it and add {successor} beside it instead"]
    return []


def problems(root: Path) -> list[str]:
    top = git(root, "rev-parse", "--show-toplevel")
    if top.returncode != 0 or Path(top.stdout.decode().strip()).resolve() != root.resolve():
        return [f"{root}: not the root of a git repository; the check reads the newest {TAGS} tag"]
    tag = newest_tag(root)
    if tag is None:
        return [f"{root}: no {TAGS} tag; run `git fetch --tags`"]
    return [p for path in released_formats(root, tag) for p in file_problems(root, tag, path)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
