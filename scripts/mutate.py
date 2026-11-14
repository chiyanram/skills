"""Lists each schema keyword and `if` guard that no test kills: makes one mutant at a time, runs the test command
against it, and names each mutant whose test command still exits 0 (a survivor).

Usage: `python3 scripts/mutate.py <file> "<test command>"`. A `*.schema.json` file gets one mutant per occurrence of a
keyword in KEYWORDS, with the whole keyword removed. A `*.py` file gets one mutant per `if` statement, with its test
negated as `not (...)`. The test command first runs once on the unmutated file; if it fails there, the script makes no
mutant and exits 2. The file is restored to its original bytes after each mutant,
also when the run is stopped by SIGINT or SIGTERM. It exits 0 when every mutant is killed and 1 otherwise. A survivor
can be an equivalent mutant, one that changes no behaviour; a person judges each one.

`schema_mutants` and `py_mutants` are pure; `run` and `main` touch the file and run the command.
"""
import ast
import copy
import json
import os
import signal
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

KEYWORDS = ("additionalProperties", "required", "minItems", "minLength", "const", "enum", "pattern", "items",
            "prefixItems")
NAMED = ("properties", "patternProperties", "$defs", "definitions")


def schema_mutants(doc) -> Iterator[tuple[str, object]]:
    """Each (JSON path, mutated doc) with one KEYWORDS occurrence removed. Keys under NAMED are names, not keywords."""
    def paths(node, here: tuple, named: bool) -> Iterator[tuple]:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in KEYWORDS and not named:
                    yield here + (key,)
                yield from paths(value, here + (key,), key in NAMED and not named)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                yield from paths(value, here + (index,), False)

    for path in paths(doc, (), False):
        mutated = copy.deepcopy(doc)
        parent = mutated
        for step in path[:-1]:
            parent = parent[step]
        del parent[path[-1]]
        yield "/".join(str(step) for step in path), mutated


class Negate(ast.NodeTransformer):
    """Wraps the test of the `target`-th `if` statement, counted in source order from 0, in `not (...)`."""

    def __init__(self, target: int):
        self.target, self.seen, self.lineno = target, -1, 0

    def visit_If(self, node: ast.If) -> ast.If:
        self.seen += 1
        if self.seen == self.target:
            node.test, self.lineno = ast.UnaryOp(op=ast.Not(), operand=node.test), node.lineno
        return self.generic_visit(node)


def py_mutants(source: str) -> Iterator[tuple[int, str]]:
    """Each (line number, mutated source) with one `if` statement's test negated."""
    count = sum(isinstance(node, ast.If) for node in ast.walk(ast.parse(source)))
    for target in range(count):
        negate = Negate(target)
        tree = ast.fix_missing_locations(negate.visit(ast.parse(source)))
        yield negate.lineno, ast.unparse(tree) + "\n"


def run(file: Path, text: str, command: str) -> bool:
    """True when the test command exits 0 with `text` in `file`. The file gets its original bytes back afterwards.

    The command writes no bytecode: Python reuses a cached .pyc whose source has the same size and modification second,
    so two mutants written in the same second would otherwise run the first one's code.
    """
    original = file.read_bytes()
    try:
        file.write_text(text)
        return subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"}).returncode == 0
    finally:
        file.write_bytes(original)


def mutants(file: Path) -> Iterator[tuple[str, str]]:
    """Each (name, mutated text) for the file's kind."""
    if file.name.endswith(".schema.json"):
        for path, doc in schema_mutants(json.loads(file.read_text())):
            yield path, json.dumps(doc, indent=2) + "\n"
    elif file.suffix == ".py":
        for lineno, text in py_mutants(file.read_text()):
            yield f"line {lineno}", text
    else:
        raise SystemExit(f"mutate: {file}: not a *.schema.json or *.py file")


def terminate(signum, frame):
    raise SystemExit(128 + signum)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print('usage: mutate.py <file> "<test command>"', file=sys.stderr)
        return 2
    file, command = Path(argv[0]), argv[1]
    signal.signal(signal.SIGTERM, terminate)
    killed = total = 0
    try:
        if not run(file, file.read_text(), command):
            print(f"mutate: baseline is red: {command!r} fails on the unmutated file", file=sys.stderr)
            return 2
        for name, text in list(mutants(file)):
            total += 1
            if run(file, text, command):
                print(f"survivor: {name}")
            else:
                killed += 1
    except KeyboardInterrupt:
        return 128 + signal.SIGINT
    print(f"{killed}/{total} killed")
    return 0 if killed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
