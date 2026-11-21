"""A rulebook skill runs for whoever installs it, a person or any agent, so it names no engine or engine role.

Fails when a rulebook `SKILL.md`, or a notes file beside it, names an engine, an engine's role or its role cards:
`coordinator`, `onboarder`, `agent-factory`, `role card`, `the engine` or `an engine`. A block that `make index`
builds is skipped, because its text comes from a reference. References and `process/` are not read.
"""
import re
import sys
from pathlib import Path

SKILLS = Path("plugins/rulebook/skills")
DENIED = re.compile(r"\b(coordinator|onboarder|agent-factory|role cards?|the engine|an engine)\b", re.I)
GENERATED = re.compile(r"<!-- (index|lanes-diagram|lanes-table)\b.*?<!-- /\1 -->", re.S)


def lines(path: Path) -> list[tuple[int, str]]:
    text = GENERATED.sub(lambda block: "\n" * block.group(0).count("\n"), path.read_text())
    return list(enumerate(text.splitlines(), 1))


def problems(root: Path) -> list[str]:
    found = []
    for router in sorted((root / SKILLS).glob("*/SKILL.md")):
        for path in sorted(router.parent.glob("*.md")):
            found += [f"{path}:{number}: names \"{hit.group(0)}\"; a skill must run without an engine or its roles"
                      for number, line in lines(path) for hit in DENIED.finditer(line)]
    return found


if __name__ == "__main__":
    found = problems(Path(sys.argv[1] if len(sys.argv) > 1 else "."))
    if found:
        print("\n".join(found))
    sys.exit(1 if found else 0)
