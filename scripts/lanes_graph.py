"""The cross-references and map values of a lanes-v2 document, which its schema cannot check.

`problems(doc, roles)` takes a document that already validates against lanes-v2.schema.json and the role names the
card schema allows. It runs each rule in RULES. A rule is a pure function (doc, roles) -> lines, and each line names
the lane, the phase or the outcome it is about.
"""
ENDS = {"next", "end", "human", "human, then same"}
ACTORS = {"human", "engine"}
EDGE_KEYS = {"to", "counts"}
FLOOR, LAST = "approval", "timeline-record"


def phase_ids(doc: dict) -> list[str]:
    return [phase["id"] for phase in doc["phases"]]


def entry_phase(entry) -> str:
    """A lane entry is a phase id, or {phase, when}."""
    return entry if isinstance(entry, str) else entry["phase"]


def is_edge(value) -> bool:
    """An edge object: a string `to` and an optional string `counts`, nothing else."""
    return (isinstance(value, dict) and set(value) <= EDGE_KEYS and isinstance(value.get("to"), str)
            and isinstance(value.get("counts", ""), str))


def edges(doc: dict) -> list[tuple[str, str, object]]:
    """Every (phase id, outcome, value) in the phase order."""
    return [(phase["id"], outcome, value) for phase in doc["phases"] for outcome, value in phase["outcomes"].items()]


def twice(doc: dict, roles: list[str]) -> list[str]:
    ids = phase_ids(doc)
    return [f"phase `{p}`: appears {ids.count(p)} times in the phase order" for p in dict.fromkeys(ids)
            if ids.count(p) > 1]


def unknown_lane_phases(doc: dict, roles: list[str]) -> list[str]:
    ids = set(phase_ids(doc))
    return [f"lane `{lane['lane']}`: phase `{entry_phase(entry)}` is not in the phase order"
            for lane in doc["lanes"] for entry in lane["phases"] if entry_phase(entry) not in ids]


def out_of_order(doc: dict, roles: list[str]) -> list[str]:
    rank = {p: n for n, p in reversed(list(enumerate(phase_ids(doc))))}
    found = []
    for lane in doc["lanes"]:
        names = [entry_phase(entry) for entry in lane["phases"] if entry_phase(entry) in rank]
        found += [f"lane `{lane['lane']}`: phase `{after}` comes after `{before}`, against the phase order"
                  for before, after in zip(names, names[1:]) if rank[after] <= rank[before]]
    return found


def no_outcomes(doc: dict, roles: list[str]) -> list[str]:
    return [f"phase `{phase['id']}`: has no outcomes" for phase in doc["phases"] if not phase["outcomes"]]


def bad_edges(doc: dict, roles: list[str]) -> list[str]:
    return [f"phase `{phase}`, outcome `{outcome}`: is neither a string nor an object with a string `to`"
            for phase, outcome, value in edges(doc) if not isinstance(value, str) and not is_edge(value)]


def bad_targets(doc: dict, roles: list[str]) -> list[str]:
    allowed = ENDS | set(phase_ids(doc))
    targets = [(phase, outcome, value if isinstance(value, str) else value["to"])
               for phase, outcome, value in edges(doc) if isinstance(value, str) or is_edge(value)]
    return [f"phase `{phase}`, outcome `{outcome}`: points at `{target}`, which is not a phase id, next, end, human "
            f"or `human, then same`" for phase, outcome, target in targets if target not in allowed]


def uncapped_counts(doc: dict, roles: list[str]) -> list[str]:
    return [f"phase `{phase}`, outcome `{outcome}`: counts `{value['counts']}`, which has no cap"
            for phase, outcome, value in edges(doc)
            if is_edge(value) and "counts" in value and value["counts"] not in doc["caps"]]


def bad_caps(doc: dict, roles: list[str]) -> list[str]:
    return [f"cap `{name}`: {value!r} is not an integer of at least 1" for name, value in doc["caps"].items()
            if isinstance(value, bool) or not isinstance(value, int) or value < 1]


def unknown_conditions(doc: dict, roles: list[str]) -> list[str]:
    return [f"lane `{lane['lane']}`: phase `{entry['phase']}` has when `{entry['when']}`, which names no condition"
            for lane in doc["lanes"] for entry in lane["phases"]
            if isinstance(entry, dict) and entry["when"] not in doc["conditions"]]


def empty_conditions(doc: dict, roles: list[str]) -> list[str]:
    return [f"condition `{name}`: its text is empty" for name, text in doc["conditions"].items()
            if not isinstance(text, str) or not text.strip()]


def no_floor(doc: dict, roles: list[str]) -> list[str]:
    return [f"lane `{lane['lane']}`: no plain `{FLOOR}` entry (the approval floor)" for lane in doc["lanes"]
            if lane["lane"] != "tiny" and FLOOR not in lane["phases"]]


def bad_ending(doc: dict, roles: list[str]) -> list[str]:
    return [f"lane `{lane['lane']}`: does not end with a plain `{LAST}` entry" for lane in doc["lanes"]
            if lane["phases"][-1:] != [LAST]]


def unknown_actors(doc: dict, roles: list[str]) -> list[str]:
    allowed = ACTORS | set(roles)
    return [f"phase `{phase['id']}`: actor `{phase['actor']}` is not a card role, human or engine"
            for phase in doc["phases"] if phase["actor"] not in allowed]


def low_lens_cap(doc: dict, roles: list[str]) -> list[str]:
    return [f"lane `{lane['lane']}`: lens_cap {lane['lens_cap']} is below 1" for lane in doc["lanes"]
            if isinstance(lane["lens_cap"], int) and lane["lens_cap"] < 1]


def bad_lane_raise(doc: dict, roles: list[str]) -> list[str]:
    target = doc["lane_raise"]["to"]
    return [] if target in phase_ids(doc) else [f"lane_raise: `to` names `{target}`, which is not a phase id"]


RULES = [twice, unknown_lane_phases, out_of_order, no_outcomes, bad_edges, bad_targets, uncapped_counts, bad_caps,
         unknown_conditions, empty_conditions, no_floor, bad_ending, unknown_actors, low_lens_cap, bad_lane_raise]


def problems(doc: dict, roles: list[str]) -> list[str]:
    return [line for rule in RULES for line in rule(doc, roles)]
