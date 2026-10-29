import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"


def run_check(name: str, target: Path) -> subprocess.CompletedProcess:
    script = ROOT / "scripts" / f"check_{name}.py"
    return subprocess.run([sys.executable, str(script), str(target)], capture_output=True, text=True)
