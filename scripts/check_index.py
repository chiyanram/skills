"""Each plugin README links every skill router, and each router's index block is what `make index` builds from its
references, so a reference is never missing from its router and two PRs never merge rows by hand. A skill that ships
process/lanes-v2.json holds its phase diagram and lanes table once each, as `make index` builds them."""
import json
import sys
from pathlib import Path

from check_links import LINK, prose_lines
from index_table import table, unreadable, with_table
from lanes_render import files

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def linked(readme: Path) -> set[Path]:
    targets = {target.split("#", 1)[0] for _, line in prose_lines(readme.read_text()) for target in LINK.findall(line)}
    return {(readme.parent / target).resolve() for target in targets if target}


def router_problems(skill: Path) -> list[str]:
    router = skill / "SKILL.md"
    if not any(skill.glob("references/*.md")) or not router.is_file():
        return []  # check_routers reports a skill that ships references without a router
    current = router.read_text()
    built = with_table(current, table(skill))
    if built is None:
        return [f"{router}: no index block; add the `make index` markers"]
    return unreadable(skill) or ([] if built == current else [f"{router}: index is stale; run `make index`"])


def lanes_problems(skill: Path) -> list[str]:
    updated, found = files(skill)
    return found + [f"{path}: lanes block is stale; run make index" for path, text in updated.items()
                    if text != path.read_text()]


def plugin_problems(root: Path, entry: dict) -> list[str]:
    folder = root / entry["source"]
    readme = folder / "README.md"
    if not readme.is_file():
        return []  # check_plugin reports the missing README
    listed = linked(readme)
    unlinked = [f"{readme}: skill router `{router.relative_to(folder)}` is not linked"
                for router in sorted(folder.glob("skills/*/SKILL.md")) if router.resolve() not in listed]
    skills = sorted(folder.glob("skills/*/"))
    return unlinked + [p for skill in skills for p in router_problems(skill) + lanes_problems(skill)]


def problems(root: Path) -> list[str]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    return [p for entry in entries for p in plugin_problems(root, entry)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
