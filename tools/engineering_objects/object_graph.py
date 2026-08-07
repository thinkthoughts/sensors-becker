"""Build the repository-wide Engineering Object graph."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def find_repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    for candidate in (start, *start.parents):
        if (candidate / "engineering_navigator").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not locate repository root containing engineering_navigator/."
    )


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level mapping")
    return data


def load_objects(object_dir: Path) -> dict[str, dict[str, Any]]:
    objects = {}
    for path in sorted(object_dir.glob("*.yaml")):
        obj = load_yaml(path)
        object_id = obj.get("id")
        if object_id:
            objects[object_id] = obj
    return objects


def build_graph(objects: dict[str, dict[str, Any]]) -> dict[str, Any]:
    nodes = []
    edges = []

    for object_id, obj in sorted(objects.items()):
        summary = obj.get("evidence_summary", {}) or {}
        nodes.append(
            {
                "id": object_id,
                "title": obj.get("title", object_id),
                "object_type": obj.get("object_type"),
                "status": obj.get("object_status"),
                "engineering_driver": obj.get("engineering_driver"),
                "source_count": summary.get(
                    "source_count",
                    len(obj.get("evidence_sources", [])),
                ),
                "candidate_specification_count": summary.get(
                    "candidate_specification_count",
                    len(obj.get("candidate_specifications", [])),
                ),
                "open_specification_count": summary.get(
                    "open_specification_count",
                    len(obj.get("open_specifications", [])),
                ),
            }
        )

        for relationship in obj.get("relationships", []):
            if not isinstance(relationship, dict):
                continue
            target = relationship.get("to")
            rel_type = relationship.get("type")
            if not target or not rel_type:
                continue

            edges.append(
                {
                    "from": object_id,
                    "to": target,
                    "type": rel_type,
                    "external": bool(
                        relationship.get("external", target not in objects)
                    ),
                }
            )

    return {
        "schema_version": "1.0.0",
        "graph_id": "engineering_object_graph",
        "nodes": nodes,
        "edges": edges,
    }


def graph_markdown(graph: dict[str, Any]) -> str:
    nodes = {node["id"]: node for node in graph["nodes"]}

    lines = [
        "# Engineering Object Graph",
        "",
        "Generated from `engineering_navigator/engineering_objects/*.yaml`.",
        "",
        "## Engineering Objects",
        "",
        "| Object | Type | Status | Sources | Candidate Specs | Open Specs |",
        "|---|---|---|---:|---:|---:|",
    ]

    for node in graph["nodes"]:
        lines.append(
            "| [{title}](engineering_objects/{id}.yaml) | {type} | {status} | "
            "{sources} | {candidates} | {open_specs} |".format(
                title=node["title"],
                id=node["id"],
                type=node.get("object_type") or "",
                status=node.get("status") or "",
                sources=node.get("source_count", 0),
                candidates=node.get("candidate_specification_count", 0),
                open_specs=node.get("open_specification_count", 0),
            )
        )

    lines.extend(
        [
            "",
            "## Relationships",
            "",
            "| From | Relationship | To |",
            "|---|---|---|",
        ]
    )

    for edge in graph["edges"]:
        source = nodes.get(edge["from"], {"title": edge["from"]})
        target = nodes.get(edge["to"], {"title": edge["to"]})

        source_link = (
            f"[{source['title']}](engineering_objects/{edge['from']}.yaml)"
            if edge["from"] in nodes
            else source["title"]
        )
        target_link = (
            f"[{target['title']}](engineering_objects/{edge['to']}.yaml)"
            if edge["to"] in nodes
            else f"`{edge['to']}`"
        )

        lines.append(
            f"| {source_link} | `{edge['type']}` | {target_link} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "*Admissible generalizations trail leading specifications.*",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Engineering Object graph YAML and Markdown."
    )
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write graph files. Otherwise preview paths/counts only.",
    )
    args = parser.parse_args()

    repo_root = (
        args.repo_root.resolve()
        if args.repo_root
        else find_repo_root()
    )
    object_dir = (
        repo_root / "engineering_navigator" / "engineering_objects"
    )

    objects = load_objects(object_dir)
    graph = build_graph(objects)

    yaml_path = (
        repo_root / "engineering_navigator" / "engineering_object_graph.yaml"
    )
    md_path = (
        repo_root / "engineering_navigator" / "engineering_object_graph.md"
    )

    print(f"objects: {len(graph['nodes'])}")
    print(f"relationships: {len(graph['edges'])}")
    print(f"yaml: {yaml_path.relative_to(repo_root)}")
    print(f"markdown: {md_path.relative_to(repo_root)}")

    if not args.write:
        print("Preview only. Re-run with --write to generate graph files.")
        return 0

    yaml_path.write_text(
        yaml.safe_dump(
            graph,
            sort_keys=False,
            allow_unicode=True,
            width=110,
        ),
        encoding="utf-8",
    )
    md_path.write_text(
        graph_markdown(graph),
        encoding="utf-8",
    )

    print(f"generated: {yaml_path.relative_to(repo_root)}")
    print(f"generated: {md_path.relative_to(repo_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
