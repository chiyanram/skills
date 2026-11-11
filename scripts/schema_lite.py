"""A small JSON Schema validator for the process schemas, with no dependency.

It knows the keywords the schemas under plugins/*/skills/*/process/schema/ use, from draft 2020-12: type, enum, const,
pattern, minLength, minItems, items (a schema or false), prefixItems, required, properties, additionalProperties
(false), allOf and anyOf. A schema that uses any other keyword is refused, so a schema never asks for a check this file
does not run.
"""
import re

ANNOTATIONS = {"$schema", "$id", "title", "description", "deprecated", "$comment"}
KEYWORDS = {"type", "enum", "const", "pattern", "minLength", "minItems", "items", "prefixItems", "required",
            "properties", "additionalProperties", "allOf", "anyOf"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def unknown_keywords(schema, where: str = "#") -> list[str]:
    """Keywords this validator does not run, anywhere in the schema."""
    if isinstance(schema, bool):
        return []
    found = [f"{where}: unsupported keyword `{k}`" for k in schema if k not in KEYWORDS | ANNOTATIONS]
    for key in ("items", "additionalProperties"):
        if isinstance(schema.get(key), dict):
            found += unknown_keywords(schema[key], f"{where}/{key}")
    for name, sub in schema.get("properties", {}).items():
        found += unknown_keywords(sub, f"{where}/properties/{name}")
    for key in ("prefixItems", "allOf", "anyOf"):
        for n, sub in enumerate(schema.get(key, [])):
            found += unknown_keywords(sub, f"{where}/{key}/{n}")
    return found


def is_type(value, name: str) -> bool:
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name in ("string", "array", "object", "null"):
        return isinstance(value, TYPES[name])
    return isinstance(value, bool) if name == "boolean" else False


def validate(value, schema, where: str = "") -> list[str]:
    """Each way `value` breaks `schema`, as one line naming where."""
    at = where or "the top level"
    if schema is False:
        return [f"{at}: not allowed"]
    if schema is True:
        return []
    found = []
    types = schema.get("type")
    if types is not None:
        names = types if isinstance(types, list) else [types]
        if not any(is_type(value, n) for n in names):
            return [f"{at}: {value!r} is not {' or '.join(names)}"]
    if "enum" in schema and value not in schema["enum"]:
        found.append(f"{at}: {value!r} is not one of {', '.join(map(str, schema['enum']))}")
    if "const" in schema and value != schema["const"]:
        found.append(f"{at}: {value!r} is not {schema['const']!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            found.append(f"{at}: is empty")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            found.append(f"{at}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            found.append(f"{at}: has {len(value)} items, needs at least {schema['minItems']}")
        prefix = schema.get("prefixItems", [])
        for n, item in enumerate(value):
            sub = prefix[n] if n < len(prefix) else schema.get("items", True)
            found += validate(item, sub, f"{where}[{n}]")
    if isinstance(value, dict):
        found += [f"{at}: `{k}` is missing" for k in schema.get("required", []) if k not in value]
        properties = schema.get("properties", {})
        for key, item in value.items():
            if key in properties:
                found += validate(item, properties[key], f"{where}.{key}" if where else key)
            elif schema.get("additionalProperties", True) is False:
                found.append(f"{at}: `{key}` is not a known field")
    for sub in schema.get("allOf", []):
        found += validate(value, sub, where)
    if "anyOf" in schema:
        tries = [validate(value, sub, where) for sub in schema["anyOf"]]
        if all(tries):
            found += [f"{at}: matches no allowed form ({'; '.join(t[0] for t in tries)})"]
    return found
