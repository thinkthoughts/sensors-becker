#!/usr/bin/env python3
"""Build the repository-wide Engineering Navigator graph from driver specifications."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:
    raise SystemExit(
        "PyYAML is required. Install it with: python -m pip install pyyaml"
    ) from exc


GRAPH_VERSION = "1.0.0"
GENERATED_BY = "build_engineering_graph.py"

REQUIRED_DRIVER_FIELDS = {
    "id": str,
    "title": str,
    "status": str,
    "repository": str,
    "engineering_object": str,
    "objective": str,
    "current_status": str,
    "depends_on": list,
    "supports": list,
    "reading_points": list,
    "engineering_sessions": list,
    "engineering_artifacts": list,
    "generated_figures": list,
    "primary_sources": list,
    "future_sources": list,
    "current_questions": list,
    "next_engineering_driver": list,
}


class GraphBuildError(ValueError):
    """Raised where Engineering Navigator graph input is invalid."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Assemble engineering_navigator/engineering_graph.yaml "
            "from driver specification.yaml files."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("engineering_navigator"),
        help="Engineering Navigator directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output YAML path. Defaults to "
            "<root>/engineering_graph.yaml."
        ),
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 where the existing graph is missing or outdated.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise GraphBuildError(f"{path}: invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise GraphBuildError(f"{path}: expected one top-level mapping")

    return data


def validate_driver(spec: dict[str, Any], path: Path) -> None:
    for field, expected_type in REQUIRED_DRIVER_FIELDS.items():
        if field not in spec:
            raise GraphBuildError(f"{path}: missing field {field!r}")
        if not isinstance(spec[field], expected_type):
            raise GraphBuildError(
                f"{path}: field {field!r} must be "
                f"{expected_type.__name__}"
            )

    if spec["id"] != path.parent.name:
        raise GraphBuildError(
            f"{path}: driver id {spec['id']!r} must match "
            f"directory {path.parent.name!r}"
        )


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))


def build_graph(
    specifications: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    driver_ids = set(specifications)

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []

    for driver_id in sorted(specifications):
        spec = specifications[driver_id]

        nodes.append(
            {
                "id": driver_id,
                "title": spec["title"],
                "status": spec["status"],
                "engineering_object": spec["engineering_object"],
                "objective": spec["objective"],
                "current_status": spec["current_status"],
                "reading_points": unique(spec["reading_points"]),
                "engineering_sessions": unique(
                    spec["engineering_sessions"]
                ),
                "engineering_artifacts": unique(
                    spec["engineering_artifacts"]
                ),
                "generated_figures": unique(spec["generated_figures"]),
                "primary_sources": unique(spec["primary_sources"]),
                "future_sources": unique(spec["future_sources"]),
                "current_questions": unique(spec["current_questions"]),
                "specification": (
                    f"{driver_id}/specification.yaml"
                ),
                "page": f"{driver_id}/index.md",
            }
        )

        for dependency in unique(spec["depends_on"]):
            edge = {
                "source": dependency,
                "relation": "supports",
                "target": driver_id,
                "declared_by": driver_id,
                "declared_as": "depends_on",
            }
            edges.append(edge)

            if dependency not in driver_ids:
                unresolved.append(
                    {
                        "id": dependency,
                        "referenced_by": driver_id,
                        "field": "depends_on",
                    }
                )

        for supported in unique(spec["supports"]):
            edge = {
                "source": driver_id,
                "relation": "supports",
                "target": supported,
                "declared_by": driver_id,
                "declared_as": "supports",
            }
            edges.append(edge)

            if supported not in driver_ids:
                unresolved.append(
                    {
                        "id": supported,
                        "referenced_by": driver_id,
                        "field": "supports",
                    }
                )

        for next_driver in unique(
            spec["next_engineering_driver"]
        ):
            edge = {
                "source": driver_id,
                "relation": "continues_to",
                "target": next_driver,
                "declared_by": driver_id,
                "declared_as": "next_engineering_driver",
            }
            edges.append(edge)

            if next_driver not in driver_ids:
                unresolved.append(
                    {
                        "id": next_driver,
                        "referenced_by": driver_id,
                        "field": "next_engineering_driver",
                    }
                )

        for navigation_target in unique(
            spec.get("continue_navigation", [])
        ):
            edge = {
                "source": driver_id,
                "relation": "navigates_to",
                "target": navigation_target,
                "declared_by": driver_id,
                "declared_as": "continue_navigation",
            }
            edges.append(edge)

            if navigation_target not in driver_ids:
                unresolved.append(
                    {
                        "id": navigation_target,
                        "referenced_by": driver_id,
                        "field": "continue_navigation",
                    }
                )

    deduplicated_edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str, str, str]] = set()

    for edge in edges:
        key = (
            edge["source"],
            edge["relation"],
            edge["target"],
            edge["declared_as"],
        )
        if key not in seen_edges:
            seen_edges.add(key)
            deduplicated_edges.append(edge)

    unresolved_unique: list[dict[str, str]] = []
    seen_unresolved: set[tuple[str, str, str]] = set()

    for item in unresolved:
        key = (
            item["id"],
            item["referenced_by"],
            item["field"],
        )
        if key not in seen_unresolved:
            seen_unresolved.add(key)
            unresolved_unique.append(item)

    reading_point_index: dict[str, list[str]] = {}
    session_index: dict[str, list[str]] = {}
    artifact_index: dict[str, list[str]] = {}
    figure_index: dict[str, list[str]] = {}

    for node in nodes:
        driver_id = node["id"]

        for reading_point in node["reading_points"]:
            reading_point_index.setdefault(
                reading_point, []
            ).append(driver_id)

        for session in node["engineering_sessions"]:
            session_index.setdefault(session, []).append(driver_id)

        for artifact in node["engineering_artifacts"]:
            artifact_index.setdefault(artifact, []).append(driver_id)

        for figure in node["generated_figures"]:
            figure_index.setdefault(figure, []).append(driver_id)

    repository_names = sorted(
        {spec["repository"] for spec in specifications.values()}
    )

    return {
        "graph": {
            "id": "sensors_becker_engineering_graph",
            "version": GRAPH_VERSION,
            "generated_by": GENERATED_BY,
            "repositories": repository_names,
            "driver_count": len(nodes),
            "edge_count": len(deduplicated_edges),
            "unresolved_reference_count": len(unresolved_unique),
        },
        "drivers": nodes,
        "relationships": deduplicated_edges,
        "indexes": {
            "reading_points": reading_point_index,
            "engineering_sessions": session_index,
            "engineering_artifacts": artifact_index,
            "generated_figures": figure_index,
        },
        "unresolved_driver_references": unresolved_unique,
    }


def render_yaml(graph: dict[str, Any]) -> str:
    return yaml.safe_dump(
        graph,
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    output = (
        args.output.resolve()
        if args.output is not None
        else root / "engineering_graph.yaml"
    )

    paths = sorted(root.glob("*/specification.yaml"))
    if not paths:
        raise GraphBuildError(
            f"No specification.yaml files found under {root}"
        )

    specifications: dict[str, dict[str, Any]] = {}

    for path in paths:
        spec = load_yaml(path)
        validate_driver(spec, path)

        driver_id = spec["id"]
        if driver_id in specifications:
            raise GraphBuildError(
                f"Duplicate engineering driver id: {driver_id}"
            )
        specifications[driver_id] = spec

    expected = render_yaml(build_graph(specifications))

    if args.check:
        if not output.exists():
            print(f"missing: {output}", file=sys.stderr)
            return 1

        current = output.read_text(encoding="utf-8")
        if current != expected:
            print(f"outdated: {output}", file=sys.stderr)
            return 1

        print(f"verified: {output.relative_to(root.parent)}")
        return 0

    output.write_text(expected, encoding="utf-8")
    print(f"generated: {output.relative_to(root.parent)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GraphBuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
