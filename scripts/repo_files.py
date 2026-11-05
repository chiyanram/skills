"""The files a check reads: git's view of the tree when there is one, else a walk. Planted fixtures and the frozen
design archive (docs/archive/, whose old relative links are not kept up) are skipped."""
import subprocess
from pathlib import Path

SKIPPED = ("tests/fixtures/", "docs/archive/")


def files(root: Path, name_glob: str) -> list[Path]:
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "--", name_glob,
                             f"**/{name_glob}"], capture_output=True, text=True)
    if listed.returncode == 0:
        relative = sorted(set(listed.stdout.splitlines()))
    else:
        relative = sorted(str(p.relative_to(root)) for p in root.rglob(name_glob) if ".git" not in p.parts)
    return [root / r for r in relative if not r.startswith(SKIPPED) and (root / r).is_file()]
