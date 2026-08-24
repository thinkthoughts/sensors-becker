"""Query absorber-manufacturing knowledge with disciplined graph traversal.

Key refinement:
- anchor matching uses node names/aliases only;
- relationship prose no longer seeds traversal;
- text-matched relationships are shown separately as supplemental context.

Examples:
    python3 tools/knowledge/knowledge_query.py grain
    python3 tools/knowledge/knowledge_query.py thickness
    python3 tools/knowledge/knowledge_query.py spectral
    python3 tools/knowledge/knowledge_query.py "current density"
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


NODE_ALIASES = {
    "grain": {
        "grain_size",
        "grain_boundary_density",
    },
    "thickness": {
        "absorber_thickness",
    },
    "spectral": {
        "spectral_response",
        "low_energy_tail",
        "energy_resolution",
    },
    "current density": {
        "electroplating_current_density",
    },
    "current": {
        "electroplating_current_density",
    },
    "temperature": {
        "bath_temperature",
        "TES_critical_temperature",
    },
    "thermal": {
        "thermalization",
        "heat_capacity",
        "heat_capacity_and_thermal_conductance",
    },
    "tail": {
        "low_energy_tail",
    },
    "absorptivity": {
        "X_ray_absorptivity",
    },
}


def all_nodes(relationships: list[dict[str, Any]]) -> set[str]:
    nodes: set[str] = set()
    for rel in relationships:
        if not isinstance(rel, dict):
            continue
        source = rel.get("from")
        target = rel.get("to")
        if isinstance(source, str) and source:
            nodes.add(source)
        if isinstance(target, str) and target:
            nodes.add(target)
    return nodes


def anchor_nodes(
    relationships: list[dict[str, Any]],
    query: str,
) -> set[str]:
    """Match only graph node names and explicit aliases."""

    q = normalize(query)
    nodes = all_nodes(relationships)
    anchors: set[str] = set()

    # Explicit alias mapping first.
    for alias, mapped_nodes in NODE_ALIASES.items():
        if q == normalize(alias):
            anchors.update(node for node in mapped_nodes if node in nodes)

    # Direct node-name matching.
    for node in nodes:
        node_text = normalize(node)
        if q == node_text or q in node_text:
            anchors.add(node)

    return anchors


def relationship_text_matches(
    rel: dict[str, Any],
    query: str,
) -> bool:
    """Supplemental text matching; never used to seed traversal."""

    q = normalize(query)
    fields = [
        rel.get("statement"),
        rel.get("effect"),
        rel.get("status"),
        rel.get("sources"),
    ]
    return any(q in normalize(value) for value in fields)


def decision_matches(item: dict[str, Any], query: str) -> bool:
    q = normalize(query)
    return any(
        q in normalize(item.get(field))
        for field in ("decision", "sources")
    )


def open_spec_matches(item: dict[str, Any], query: str) -> bool:
    q = normalize(query)
    return any(
        q in normalize(item.get(field))
        for field in ("specification", "reason", "sources")
    )


def process_point_matches(point: dict[str, Any], query: str) -> bool:
    q = normalize(query)

    aliases = {
        "thickness": ["bismuth_thickness_um"],
        "current": ["current_density_mA_per_cm2"],
        "current density": ["current_density_mA_per_cm2"],
        "temperature": ["bath_temperature", "bath_temperature_C"],
        "grain": ["grain_size_nm"],
        "rate": ["plating_rate_nm_per_min"],
        "voltage": ["bias_voltage_V"],
    }

    if q in normalize(point):
        return True

    for alias, keys in aliases.items():
        if q == normalize(alias):
            if any(key in point for key in keys):
                return True

    return False


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


def traverse(
    start_nodes: set[str],
    relationships: list[dict[str, Any]],
    *,
    max_depth: int,
) -> dict[str, list[dict[str, Any]]]:
    """Return upstream and downstream traversals with real graph depths."""

    outgoing, incoming = build_graph(relationships)

    downstream: list[dict[str, Any]] = []
    upstream: list[dict[str, Any]] = []

    def walk(
        adjacency: dict[str, list[dict[str, Any]]],
        direction: str,
    ) -> list[dict[str, Any]]:
        queue = deque((node, 0) for node in sorted(start_nodes))
        seen_nodes = set(start_nodes)
        seen_edges: set[str] = set()
        results: list[dict[str, Any]] = []

        while queue:
            node, depth = queue.popleft()

            if depth >= max_depth:
                continue

            for rel in adjacency.get(node, []):
                rel_id = rel.get("id") or json.dumps(rel, sort_keys=True)

                if rel_id not in seen_edges:
                    results.append(
                        {
                            **rel,
                            "_direction": direction,
                            "_depth": depth + 1,
                        }
                    )
                    seen_edges.add(rel_id)

                next_node = (
                    rel.get("to")
                    if direction == "downstream"
                    else rel.get("from")
                )

                if next_node and next_node not in seen_nodes:
                    seen_nodes.add(next_node)
                    queue.append((next_node, depth + 1))

        results.sort(
            key=lambda item: (
                item.get("_depth", 99),
                item.get("id", ""),
            )
        )
        return results

    downstream = walk(outgoing, "downstream")
    upstream = walk(incoming, "upstream")

    return {
        "upstream": upstream,
        "downstream": downstream,
    }


def query_knowledge(
    knowledge: dict[str, Any],
    query: str,
    *,
    max_depth: int = MAX_DEFAULT_DEPTH,
) -> dict[str, Any]:
    relationships = [
        rel
        for rel in knowledge.get("relationships", [])
        if isinstance(rel, dict)
    ]

    anchors = anchor_nodes(relationships, query)

    paths = traverse(
        anchors,
        relationships,
        max_depth=max_depth,
    ) if anchors else {"upstream": [], "downstream": []}

    supplemental = [
        rel
        for rel in relationships
        if relationship_text_matches(rel, query)
        and rel.get("id")
        not in {
            item.get("id")
            for item in paths["upstream"] + paths["downstream"]
        }
    ]

    decisions = [
        item
        for item in knowledge.get("engineering_decisions", {}).get(
            "supported_now", []
        )
        if isinstance(item, dict) and decision_matches(item, query)
    ]

    open_specs = [
        item
        for item in knowledge.get("engineering_decisions", {}).get(
            "open_specifications", []
        )
        if isinstance(item, dict) and open_spec_matches(item, query)
    ]

    process_points = [
        point
        for point in knowledge.get("reported_process_points", [])
        if isinstance(point, dict) and process_point_matches(point, query)
    ]

    return {
        "query": query,
        "anchor_nodes": sorted(anchors),
        "upstream_path": paths["upstream"],
        "downstream_path": paths["downstream"],
        "supplemental_relationships": supplemental,
        "supported_decisions": decisions,
        "open_specifications": open_specs,
        "reported_process_points": process_points,
    }


def sources_text(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value or "")


def print_relationship(rel: dict[str, Any]) -> None:
    prefix = "  " * max(int(rel.get("_depth", 1)) - 1, 0)

    print(
        f"\n{prefix}{rel.get('from')} -> {rel.get('to')}"
    )
    print(f"{prefix}  status: {rel.get('status')}")
    print(f"{prefix}  {rel.get('statement')}")
    if rel.get("effect"):
        print(f"{prefix}  effect: {rel.get('effect')}")
    print(
        f"{prefix}  evidence: {sources_text(rel.get('sources'))}"
    )
    if rel.get("_depth") is not None:
        print(
            f"{prefix}  depth: {rel.get('_depth')}"
        )


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

    if result["anchor_nodes"]:
        print("\nANCHOR NODES")
        print("------------")
        for node in result["anchor_nodes"]:
            print(f"- {node}")

    if result["upstream_path"]:
        print("\nUPSTREAM")
        print("--------")
        for rel in result["upstream_path"]:
            print_relationship(rel)

    if result["downstream_path"]:
        print("\nDOWNSTREAM")
        print("----------")
        for rel in result["downstream_path"]:
            print_relationship(rel)

    if result["supplemental_relationships"]:
        print("\nRELATED EVIDENCE")
        print("----------------")
        for rel in result["supplemental_relationships"]:
            print_relationship(rel)

    if result["supported_decisions"]:
        print("\nSUPPORTED ENGINEERING DECISIONS")
        print("-------------------------------")

        for item in result["supported_decisions"]:
            print(f"\n- {item.get('decision')}")
            print(
                f"  evidence: {sources_text(item.get('sources'))}"
            )

    if result["open_specifications"]:
        print("\nOPEN SPECIFICATIONS")
        print("-------------------")

        for spec in result["open_specifications"]:
            print(f"\n- {spec.get('specification')}")
            print(f"  why open: {spec.get('reason')}")
            print(
                f"  evidence: {sources_text(spec.get('sources'))}"
            )

    print_process_points(result["reported_process_points"])

    if not any(
        [
            result["anchor_nodes"],
            result["supplemental_relationships"],
            result["supported_decisions"],
            result["open_specifications"],
            result["reported_process_points"],
        ]
    ):
        print("\nNo matching knowledge entries.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query absorber-manufacturing engineering knowledge."
    )
    parser.add_argument("query")
    parser.add_argument("--knowledge", type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument(
        "--depth",
        type=int,
        default=MAX_DEFAULT_DEPTH,
        help=f"Traversal depth (default: {MAX_DEFAULT_DEPTH})",
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
