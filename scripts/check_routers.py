"""Each skill folder that ships references has a SKILL.md router linking every one, because an agent reaches a
reference only through its skill."""
import json
import sys
from pathlib import Path

from check_links import LINK, prose_lines

MARKETPLACE = Path(".claude-plugin/marketplace.json")


def linked(router: Path) -> set[Path]:
    targets = {target.split("#", 1)[0] for _, line in prose_lines(router.read_text()) for target in LINK.findall(line)}
    return {(router.parent / target).resolve() for target in targets if target}


def skill_problems(skill: Path) -> list[str]:
    references = sorted(skill.glob("references/*.md"))
    if not references:
        return []
    router = skill / "SKILL.md"
    if not router.is_file():
        return [f"{skill}: ships {len(references)} references but has no SKILL.md router"]
    listed = linked(router)
    return [f"{router}: reference `{reference.relative_to(skill)}` is not linked"
            for reference in references if reference.resolve() not in listed]


def problems(root: Path) -> list[str]:
    entries = json.loads((root / MARKETPLACE).read_text()).get("plugins", [])
    return [p for entry in entries for skill in sorted((root / entry["source"]).glob("skills/*/"))
            for p in skill_problems(skill)]


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
