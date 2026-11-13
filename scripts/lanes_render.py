"""Builds a skill's phase diagram and lanes table from its process/lanes-v2.json, so the prose cannot drift from the
graph (`make index` writes the blocks, `check_index` fails a stale one).

`files(skill)` reads the skill; every other function is pure. A block sits between its own START and END markers in
exactly one markdown file of the skill.
"""
import json
import textwrap
from collections.abc import Callable
from pathlib import Path

from check_process import lanes_v2_problems, load_schemas
from lanes_graph import edges, entry_phase, phase_ids

FLOW_WIDTH, PROSE_WIDTH = 100, 120
ARROW, CONTINUATION = " ─▶ ", "   ─▶ "
SILENT = {"next", "end", "human, then same"}
HUMAN = "human"


def start(name: str) -> str:
    return f"<!-- {name}: built by make index from process/lanes-v2.json; do not edit by hand -->"


def end(name: str) -> str:
    return f"<!-- /{name} -->"


def actors(doc: dict) -> dict[str, str]:
    return {phase["id"]: phase["actor"] for phase in doc["phases"]}


def label(phase: str, actor: str) -> str:
    """A phase id, marked `HUMAN` when a person runs it."""
    return f"HUMAN {phase}" if actor == HUMAN else phase


def wrapped(labels: list[str]) -> list[str]:
    """The labels joined by arrows, wrapped greedily at FLOW_WIDTH columns with an indented arrow on each new line."""
    lines = [labels[0]]
    for item in labels[1:]:
        if len(lines[-1] + ARROW + item) > FLOW_WIDTH:
            lines.append(CONTINUATION + item)
        else:
            lines[-1] += ARROW + item
    return lines


def target(value: str | dict) -> str:
    return value if isinstance(value, str) else value["to"]


def cap(value: str | dict, caps: dict) -> str:
    """The cap a counted edge spends, as `cap <name> = <value>`, or "" for an edge that counts nothing."""
    counted = value.get("counts") if isinstance(value, dict) else None
    return f"cap {counted} = {caps[counted]}" if counted else ""


def edge_rows(doc: dict) -> list[list[str]]:
    """Each outcome that does not simply move on, end or wait for the human: phase, outcome, target, cap."""
    return [[phase, outcome, f"─▶ {target(value)}", cap(value, doc["caps"])]
            for phase, outcome, value in edges(doc) if target(value) not in SILENT]


def columns(rows: list[list[str]]) -> list[str]:
    """The rows with each cell padded to its column's width, two spaces apart."""
    widths = [max(len(row[n]) for row in rows) for n in range(len(rows[0]))] if rows else []
    return ["  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip() for row in rows]


def diagram(doc: dict) -> list[str]:
    """The phase order with each human phase marked, then each back edge, cap edge or human hand-off."""
    who = actors(doc)
    flow = wrapped([label(phase, who[phase]) for phase in phase_ids(doc)])
    return ["```text", *flow, "", *columns(edge_rows(doc)), "```"]


def cell(entry: str | dict) -> str:
    """A lane entry: a phase id, or `<phase> (when <condition>)`."""
    return entry if isinstance(entry, str) else f"{entry['phase']} (when {entry['when']})"


def gates(lane: dict, who: dict[str, str]) -> str:
    """The lane's phases a person runs."""
    return ", ".join(entry_phase(e) for e in lane["phases"] if who[entry_phase(e)] == HUMAN) or "—"


def conditions_used(doc: dict) -> list[str]:
    """Each condition a lane entry names, in order of first use."""
    named = [entry["when"] for lane in doc["lanes"] for entry in lane["phases"] if isinstance(entry, dict)]
    return list(dict.fromkeys(named))


def lanes_table(doc: dict) -> list[str]:
    """One row per lane in file order, then each condition the rows use with its text."""
    who = actors(doc)
    rows = [f"| {lane['lane']} | {' → '.join(cell(e) for e in lane['phases'])} | {gates(lane, who)} |"
            for lane in doc["lanes"]]
    notes = [line for name in conditions_used(doc)
             for line in ["", *textwrap.wrap(f"{name}: {doc['conditions'][name]}", PROSE_WIDTH)]]
    return ["| lane | phases | human gates |", "|---|---|---|", *rows, *notes]


BLOCKS: dict[str, Callable[[dict], list[str]]] = {"lanes-diagram": diagram, "lanes-table": lanes_table}


def with_block(text: str, name: str, lines: list[str]) -> str | None:
    """The text with the block's body replaced, or None unless it holds one START and one END marker after it."""
    if text.count(start(name)) != 1 or text.count(end(name)) != 1:
        return None
    head, rest = text.split(start(name), 1)
    if end(name) not in rest:
        return None
    return head + "\n".join([start(name), *lines, end(name)]) + rest.split(end(name), 1)[1]


def placement(skill: Path, name: str, texts: dict[Path, str]) -> list[str]:
    """Why the block is not in exactly one file, once, with its END marker after START; else nothing."""
    holders = [path for path, text in texts.items() if start(name) in text]
    if not holders:
        return [f"{skill}: no `{name}` block in its markdown files; add its make index markers"]
    if len(holders) > 1:
        return [f"{path}: holds a `{name}` block, which is in {len(holders)} files" for path in holders]
    if with_block(texts[holders[0]], name, []) is None:
        return [f"{holders[0]}: the `{name}` block needs one START marker and one END marker after it"]
    return []


def rendered(text: str, doc: dict) -> str:
    """The text with each block it holds built from the doc."""
    for name, render in BLOCKS.items():
        text = with_block(text, name, render(doc)) if start(name) in text else text
    return text


def valid(lanes: Path) -> tuple[dict, list[str]]:
    """The lanes-v2 doc, or the schema lines when a process schema is missing, or one line when the doc is not valid."""
    schemas, found = load_schemas(lanes.parent)
    if found:
        return {}, found
    roles = schemas["card"]["properties"]["role"]["enum"]
    if lanes_v2_problems(lanes, schemas["lanes-v2"], roles):
        return {}, [f"{lanes}: not valid; run check_process.py"]
    return json.loads(lanes.read_text()), []


def files(skill: Path) -> tuple[dict[Path, str], list[str]]:
    """Each markdown file holding a block, with its blocks built, or the problems that stop the build."""
    lanes = skill / "process" / "lanes-v2.json"
    if not lanes.is_file():
        return {}, []
    doc, found = valid(lanes)
    if found:
        return {}, found
    texts = {path: path.read_text() for path in sorted(skill.rglob("*.md"))}
    found = [line for name in BLOCKS for line in placement(skill, name, texts)]
    if found:
        return {}, found
    holders = [path for path, text in texts.items() if any(start(name) in text for name in BLOCKS)]
    return {path: rendered(texts[path], doc) for path in holders}, []
