"""Query absorber-manufacturing knowledge with graph traversal.

Examples:
    python3 tools/knowledge/knowledge_query.py grain
    python3 tools/knowledge/knowledge_query.py thickness
    python3 tools/knowledge/knowledge_query.py spectral
    python3 tools/knowledge/knowledge_query.py "current density"

The query now does two things:
1. keyword-match relevant knowledge entries;
2. traverse the relationship graph outward from matched engineering nodes.

This remains a navigation layer over the canonical knowledge YAML.
It does not invent new causal relationships.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import yaml


MAX_DEFAULT_DEPTH = 4


def find_repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "engineering_navigator").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not locate repository root containing engineering_navigator/."
    )


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level YAML mapping")
    return data


def normalize(value: Any) -> str:
    text = str(value).lower()
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def query_tokens(query: str) -> list[str]:
    q = normalize(query)
    aliases = {
        "grain": ["grain", "grain size", "grain boundary", "microstructure"],
        "thickness": ["thickness", "absorber thickness", "bi thickness"],
        "spectral": ["spectral", "low energy tail", "energy resolution"],
        "current density": ["current density", "electroplating current density"],
        "current": ["current", "current density"],
        "temperature": ["temperature", "bath temperature"],
        "thermal": ["thermal", "thermalization", "heat capacity", "thermal conductance"],
    }
    return aliases.get(q, [q])


def text_matches(value: Any, tokens: list[str]) -> bool:
    text = normalize(value)
    return any(token in text for token in tokens)


def relationship_matches(rel: dict[str, Any], tokens: list[str]) -> bool:
    return any(
        text_matches(rel.get(field), tokens)
        for field in ("id", "from", "to", "status", "statement", "effect", "sources")
    )


def decision_matches(item: dict[str, Any], tokens: list[str]) -> bool:
    return any(
        text_matches(item.get(field), tokens)
        for field in ("decision", "sources")
    )


def open_spec_matches(item: dict[str, Any], tokens: list[str]) -> bool:
    return any(
        text_matches(item.get(field), tokens)
        for field in ("id", "specification", "reason", "sources")
    )


def process_point_matches(point: dict[str, Any], tokens: list[str]) -> bool:
    return text_matches(point, tokens)


def build_graph(
    relationships: list[dict[str, Any]],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, list[dict[str, Any]]],
]:
    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for rel in relationships:
        if not isinstance(rel, dict):
            continue
        source = rel.get("from")
        target = rel.get("to")
        if not source or not target:
            continue
        outgoing[source].append(rel)
        incoming[target].append(rel)

    return outgoing, incoming


def matched_nodes(
    relationships: list[dict[str, Any]],
    tokens: list[str],
) -> set[str]:
    nodes: set[str] = set()

    for rel in relationships:
        if not isinstance(rel, dict):
            continue
        for field in ("from", "to"):
            node = rel.get(field)
            if node and text_matches(node, tokens):
                nodes.add(node)

    return nodes


def traverse_from_nodes(
    start_nodes: set[str],
    relationships: list[dict[str, Any]],
    *,
    max_depth: int = MAX_DEFAULT_DEPTH,
) -> list[dict[str, Any]]:
    """Traverse outward and inward without inventing new edges."""

    outgoing, incoming = build_graph(relationships)
    queue = deque((node, 0) for node in sorted(start_nodes))
    seen_nodes = set(start_nodes)
    seen_edges: set[str] = set()
    traversed: list[dict[str, Any]] = []

    while queue:
        node, depth = queue.popleft()
        if depth >= max_depth:
            continue

        # Forward engineering consequence.
        for rel in outgoing.get(node, []):
            rel_id = rel.get("id") or json.dumps(rel, sort_keys=True)
            if rel_id not in seen_edges:
                traversed.append(
                    {
                        **rel,
                        "_direction": "forward",
                        "_depth": depth + 1,
                    }
                )
                seen_edges.add(rel_id)

            target = rel.get("to")
            if target and target not in seen_nodes:
                seen_nodes.add(target)
                queue.append((target, depth + 1))

        # Immediate upstream context.
        for rel in incoming.get(node, []):
            rel_id = rel.get("id") or json.dumps(rel, sort_keys=True)
            if rel_id not in seen_edges:
                traversed.append(
                    {
                        **rel,
                        "_direction": "upstream",
                        "_depth": depth + 1,
                    }
                )
                seen_edges.add(rel_id)

            source = rel.get("from")
            if source and source not in seen_nodes:
                seen_nodes.add(source)
                queue.append((source, depth + 1))

    traversed.sort(key=lambda x: (x.get("_depth", 99), x.get("id", "")))
    return traversed


def query_knowledge(
    knowledge: dict[str, Any],
    query: str,
    *,
    max_depth: int = MAX_DEFAULT_DEPTH,
) -> dict[str, Any]:
    tokens = query_tokens(query)
    relationships = [
        rel for rel in knowledge.get("relationships", [])
        if isinstance(rel, dict)
    ]

    direct_relationships = [
        rel for rel in relationships
        if relationship_matches(rel, tokens)
    ]

    starts = matched_nodes(relationships, tokens)

    # If query matched relationship text but not endpoint names, seed traversal
    # from those relationship endpoints.
    for rel in direct_relationships:
        if rel.get("from"):
            starts.add(rel["from"])
        if rel.get("to"):
            starts.add(rel["to"])

    graph_path = traverse_from_nodes(
        starts,
        relationships,
        max_depth=max_depth,
    )

    decisions = [
        item
        for item in knowledge.get("engineering_decisions", {}).get(
            "supported_now", []
        )
        if isinstance(item, dict) and decision_matches(item, tokens)
    ]

    open_specs = [
        item
        for item in knowledge.get("engineering_decisions", {}).get(
            "open_specifications", []
        )
        if isinstance(item, dict) and open_spec_matches(item, tokens)
    ]

    process_points = [
        point
        for point in knowledge.get("reported_process_points", [])
        if isinstance(point, dict) and process_point_matches(point, tokens)
    ]

    return {
        "query": query,
        "matched_nodes": sorted(starts),
        "direct_relationships": direct_relationships,
        "engineering_path": graph_path,
        "supported_decisions": decisions,
        "open_specifications": open_specs,
        "reported_process_points": process_points,
    }


def sources_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value or "")


def print_path(path: list[dict[str, Any]]) -> None:
    if not path:
        return

    print("\nENGINEERING PATH")
    print("----------------")

    for rel in path:
        source = rel.get("from")
        target = rel.get("to")
        status = rel.get("status")
        depth = rel.get("_depth")
        direction = rel.get("_direction")

        arrow = "->"
        prefix = "  " * max(int(depth or 1) - 1, 0)

        print(f"\n{prefix}{source} {arrow} {target}")
        print(f"{prefix}  status: {status}")
        print(f"{prefix}  {rel.get('statement')}")
        if rel.get("effect"):
            print(f"{prefix}  effect: {rel.get('effect')}")
        print(f"{prefix}  evidence: {sources_text(rel.get('sources'))}")
        print(f"{prefix}  traversal: {direction}, depth {depth}")


def print_process_points(points: list[dict[str, Any]]) -> None:
    if not points:
        return

    print("\nREPORTED PROCESS POINTS")
    print("-----------------------")
    for point in points:
        source = point.get("source", "unknown")
        print(f"\nPROCESS POINT — {source}")
        for key, value in point.items():
            if key == "source":
                continue
            print(f"  {key}: {value}")


def print_result(result: dict[str, Any]) -> None:
    query = result["query"]
    print(f"\n{query.upper()}")
    print("=" * len(query))

    if result["matched_nodes"]:
        print("\nMATCHED NODES")
        print("-------------")
        for node in result["matched_nodes"]:
            print(f"- {node}")

    print_path(result["engineering_path"])

    if result["supported_decisions"]:
        print("\nSUPPORTED ENGINEERING DECISIONS")
        print("-------------------------------")
        for item in result["supported_decisions"]:
            print(f"\n- {item.get('decision')}")
            print(f"  evidence: {sources_text(item.get('sources'))}")

    if result["open_specifications"]:
        print("\nOPEN SPECIFICATIONS")
        print("-------------------")
        for spec in result["open_specifications"]:
            print(f"\n- {spec.get('specification')}")
            print(f"  why open: {spec.get('reason')}")
            print(f"  evidence: {sources_text(spec.get('sources'))}")

    print_process_points(result["reported_process_points"])

    if not any(
        [
            result["engineering_path"],
            result["supported_decisions"],
            result["open_specifications"],
            result["reported_process_points"],
        ]
    ):
        print("\nNo matching knowledge entries.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query and traverse absorber-manufacturing knowledge."
    )
    parser.add_argument("query")
    parser.add_argument("--knowledge", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument(
        "--depth",
        type=int,
        default=MAX_DEFAULT_DEPTH,
        help=f"Maximum graph traversal depth (default: {MAX_DEFAULT_DEPTH}).",
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.depth < 0:
        raise ValueError("--depth must be >= 0")

    root = (
        args.repo_root.expanduser().resolve()
        if args.repo_root
        else find_repo_root()
    )

    knowledge_path = (
        args.knowledge.expanduser().resolve()
        if args.knowledge
        else (
            root
            / "engineering_navigator"
            / "absorber_manufacturing"
            / "knowledge"
            / "absorber_manufacturing.yaml"
        )
    )

    result = query_knowledge(
        load_yaml(knowledge_path),
        args.query,
        max_depth=args.depth,
    )

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
