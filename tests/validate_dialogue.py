#!/usr/bin/env python3
"""Validate dialogue graphs with the standard library, without Godot.

Entry points and allowed flag names live in data/dialogue_schema.json.
Every node reachable from an entry must have a path to a terminal. Cycles
are allowed when they have an exit; this does not prove a player takes it.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "dialogue_schema.json"
DIALOGUE_DIR = ROOT / "data" / "dialogue"


def validate_graph(graph, entries, schema, label="<graph>"):
    errors = []
    flags_used = set()
    def error(message):
        errors.append(f"{label}: {message}")

    if not isinstance(graph, dict) or not graph:
        return [f"{label}: graph must be a nonempty object of node IDs"], flags_used
    if not isinstance(entries, list) or not entries or any(not isinstance(e, str) or not e for e in entries):
        return [f"{label}: declare at least one nonempty entry ID"], flags_used

    edges = {key: set() for key in graph}
    terminals = set()
    allowed = schema["flags"]
    exclusive = schema["exclusive_flag_groups"]

    def check_flags(value, where):
        if not isinstance(value, dict):
            error(f"{where}: set_flag must be an object")
            return
        flags_used.update(value)
        for key, flag_value in value.items():
            if key not in allowed:
                error(f"{where}: unknown flag {key!r}")
            elif allowed[key] == "bool" and type(flag_value) is not bool:
                error(f"{where}: flag {key!r} must be boolean")
        for group in exclusive:
            if set(group) & value.keys():
                if not set(group) <= value.keys():
                    error(f"{where}: assign every mutually exclusive flag in {group}")
                elif any(type(value[k]) is not bool for k in group) or sum(value[k] is True for k in group) > 1:
                    error(f"{where}: flags in {group} must be boolean and at most one true")

    def target(node_id, value, where):
        if value is None:
            terminals.add(node_id)
        elif not isinstance(value, str) or not value:
            error(f"{where}: next must be a node ID or null")
        elif value not in graph:
            error(f"{where}: next points to missing node {value!r}")
        else:
            edges[node_id].add(value)

    for entry in entries:
        if entry not in graph:
            error(f"missing entry {entry!r}")
    for node_id, node in graph.items():
        where = repr(node_id)
        if not isinstance(node_id, str) or not node_id or not isinstance(node, dict):
            error(f"{where}: node ID must be nonempty and node must be an object")
            continue
        for key in set(node) - {"speaker", "text", "next", "choices", "set_flag"}:
            error(f"{where}: unsupported field {key!r}")
        for field in ("speaker", "text"):
            if field in node and not isinstance(node[field], str):
                error(f"{where}: {field} must be a string")
        if "set_flag" in node:
            check_flags(node["set_flag"], where)
        has_next, has_choices = "next" in node, "choices" in node
        if has_next == has_choices:
            error(f"{where}: specify exactly one of next or choices")
        if has_next:
            target(node_id, node["next"], where)
        if has_choices:
            choices = node["choices"]
            if not isinstance(choices, list) or not choices:
                error(f"{where}: choices must be a nonempty array")
                continue
            for index, choice in enumerate(choices):
                cw = f"{where} choice {index}"
                if not isinstance(choice, dict):
                    error(f"{cw}: must be an object")
                    continue
                for key in set(choice) - {"text", "next", "set_flag"}:
                    error(f"{cw}: unsupported field {key!r}")
                if not isinstance(choice.get("text"), str) or not choice["text"]:
                    error(f"{cw}: text must be a nonempty string")
                if "next" not in choice:
                    error(f"{cw}: next is required (use null to end)")
                else:
                    target(node_id, choice["next"], cw)
                if "set_flag" in choice:
                    check_flags(choice["set_flag"], cw)

    seen, stack = set(), [e for e in entries if e in graph]
    while stack:
        node = stack.pop()
        if node not in seen:
            seen.add(node)
            stack.extend(edges[node] - seen)
    for node in sorted(set(graph) - seen):
        error(f"{node!r}: unreachable from declared entries")

    can_end = set(terminals)
    changed = True
    while changed:
        before = len(can_end)
        can_end.update(node for node, targets in edges.items() if targets & can_end)
        changed = len(can_end) != before
    for node in sorted(seen - can_end):
        error(f"{node!r}: no path to a terminal")
    return errors, flags_used


def load_schema(path):
    schema = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(schema, dict) or not isinstance(schema.get("flags"), dict) or not isinstance(schema.get("entries"), dict) or not isinstance(schema.get("exclusive_flag_groups"), list):
        raise ValueError("schema needs flags, entries and exclusive_flag_groups")
    if any(not isinstance(k, str) or not k or v != "bool" for k, v in schema["flags"].items()):
        raise ValueError("schema flags must map nonempty names to bool")
    for group in schema["exclusive_flag_groups"]:
        if not isinstance(group, list) or len(group) < 2 or any(not isinstance(k, str) or k not in schema["flags"] for k in group) or len(set(group)) != len(group):
            raise ValueError("invalid mutually exclusive flag group")
    return schema


def main():
    try:
        schema = load_schema(SCHEMA_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read schema: {exc}")
        return 1
    paths = sorted(DIALOGUE_DIR.glob("*.json"))
    errors = []
    if not paths:
        errors.append("no dialogue graphs found")
    file_names = {p.name for p in paths}
    for name in sorted(set(schema["entries"]) - file_names):
        errors.append(f"schema declares missing graph {name!r}")
    for path in paths:
        if path.name not in schema["entries"]:
            errors.append(f"{path.name}: no entry points declared in schema")
            continue
        try:
            graph = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.name}: cannot parse JSON: {exc}")
            continue
        graph_errors, flags = validate_graph(graph, schema["entries"][path.name], schema, path.name)
        errors.extend(graph_errors)
        print(f"[{'FAIL' if graph_errors else 'OK'}] {path.name}; flags: {', '.join(sorted(flags)) or '(none)'}")
    for error in errors:
        print(f"  ERROR: {error}")
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
