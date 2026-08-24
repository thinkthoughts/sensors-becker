"""Validate engineering knowledge artifacts against repository source records.

Initial target:
    engineering_navigator/absorber_manufacturing/knowledge/absorber_manufacturing.yaml

Checks:
- knowledge artifact has the expected top-level structure
- relationship IDs are unique
- relationship status values are recognized
- relationship endpoints and statements are present
- every SOURCE reference resolves to a completed source record
- engineering-decision SOURCE references resolve
- open-specification IDs are unique
- reported process-point SOURCE references resolve
- source_records declarations resolve

Usage:
    python3 tools/knowledge/knowledge_validator.py

Validate an explicit knowledge file:
    python3 tools/knowledge/knowledge_validator.py \
        --knowledge engineering_navigator/absorber_manufacturing/knowledge/absorber_manufacturing.yaml
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable

import yaml


ALLOWED_RELATIONSHIP_STATUSES = {
    "supported",
    "supported_interpretation",
    "supported_model",
    "candidate",
    "open",
}


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
        raise FileNotFoundError(f"Missing YAML file: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level YAML mapping")

    return data


def load_source_records(source_dir: Path) -> dict[str, Path]:
    """Return completed source IDs mapped to their canonical YAML paths."""

    records: dict[str, Path] = {}

    if not source_dir.is_dir():
        raise FileNotFoundError(f"Missing source-record directory: {source_dir}")

    for path in sorted(source_dir.glob("SOURCE_*.yaml")):
        if path.name.endswith(".scaffold.yaml"):
            continue

        record = load_yaml(path)
        source_id = record.get("source_id")

        if not source_id:
            raise KeyError(f"{path}: missing source_id")

        if source_id in records:
            raise ValueError(
                f"Duplicate source_id {source_id!r}: "
                f"{records[source_id]} and {path}"
            )

        records[str(source_id)] = path

    if not records:
        raise FileNotFoundError(
            f"No completed SOURCE_*.yaml records found in {source_dir}"
        )

    return records


def as_list(value: Any, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(value, list):
        errors.append(f"{label}: expected a list")
        return []
    return value


def validate_source_refs(
    refs: Any,
    *,
    label: str,
    known_sources: set[str],
    errors: list[str],
) -> None:
    refs_list = as_list(refs, label, errors)

    if not refs_list:
        errors.append(f"{label}: must contain at least one source")
        return

    for source_id in refs_list:
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"{label}: invalid source reference {source_id!r}")
            continue

        if source_id not in known_sources:
            errors.append(
                f"{label}: source {source_id!r} does not resolve to a "
                "completed source record"
            )


def validate_unique_ids(
    items: Iterable[Any],
    *,
    id_key: str,
    label: str,
    errors: list[str],
) -> None:
    seen: set[str] = set()

    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}]: expected a mapping")
            continue

        item_id = item.get(id_key)

        if not isinstance(item_id, str) or not item_id.strip():
            errors.append(f"{label}[{index}]: missing {id_key}")
            continue

        if item_id in seen:
            errors.append(f"{label}: duplicate {id_key} {item_id!r}")
        else:
            seen.add(item_id)


def validate_knowledge(
    knowledge: dict[str, Any],
    *,
    source_records: dict[str, Path],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    known_sources = set(source_records)

    required_top_level = [
        "schema_version",
        "repository",
        "engineering_driver",
        "knowledge_id",
        "knowledge_status",
        "purpose",
        "source_records",
        "reading_path",
        "manufacturing_inputs",
        "absorber_state",
        "detector_response",
        "relationships",
        "engineering_decisions",
        "completion_criteria_v1",
    ]

    for key in required_top_level:
        if key not in knowledge:
            errors.append(f"top-level: missing {key!r}")

    if knowledge.get("engineering_driver") != "absorber_manufacturing":
        errors.append(
            "engineering_driver: expected 'absorber_manufacturing', found "
            f"{knowledge.get('engineering_driver')!r}"
        )

    # Declared source records.
    declared = as_list(
        knowledge.get("source_records", []),
        "source_records",
        errors,
    )

    declared_ids: set[str] = set()

    for index, item in enumerate(declared):
        if not isinstance(item, dict):
            errors.append(f"source_records[{index}]: expected a mapping")
            continue

        source_id = item.get("source_id")

        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(f"source_records[{index}]: missing source_id")
            continue

        if source_id in declared_ids:
            errors.append(
                f"source_records: duplicate source_id {source_id!r}"
            )
        declared_ids.add(source_id)

        if source_id not in known_sources:
            errors.append(
                f"source_records[{index}]: {source_id!r} does not resolve "
                "to a completed source record"
            )

    # Relationships.
    relationships = as_list(
        knowledge.get("relationships", []),
        "relationships",
        errors,
    )

    validate_unique_ids(
        relationships,
        id_key="id",
        label="relationships",
        errors=errors,
    )

    referenced_sources: set[str] = set()

    for index, rel in enumerate(relationships):
        if not isinstance(rel, dict):
            continue

        prefix = f"relationships[{index}]"

        for key in ("from", "to", "status", "statement"):
            value = rel.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}: missing or empty {key!r}")

        status = rel.get("status")
        if (
            isinstance(status, str)
            and status
            and status not in ALLOWED_RELATIONSHIP_STATUSES
        ):
            errors.append(
                f"{prefix}: unsupported status {status!r}; expected one of "
                f"{sorted(ALLOWED_RELATIONSHIP_STATUSES)}"
            )

        refs = rel.get("sources", [])
        validate_source_refs(
            refs,
            label=f"{prefix}.sources",
            known_sources=known_sources,
            errors=errors,
        )

        if isinstance(refs, list):
            referenced_sources.update(
                source_id
                for source_id in refs
                if isinstance(source_id, str)
            )

    # Reported process points.
    process_points = as_list(
        knowledge.get("reported_process_points", []),
        "reported_process_points",
        errors,
    )

    for index, point in enumerate(process_points):
        if not isinstance(point, dict):
            errors.append(
                f"reported_process_points[{index}]: expected a mapping"
            )
            continue

        source_id = point.get("source")
        if not isinstance(source_id, str) or not source_id.strip():
            errors.append(
                f"reported_process_points[{index}]: missing source"
            )
        elif source_id not in known_sources:
            errors.append(
                f"reported_process_points[{index}]: source "
                f"{source_id!r} does not resolve"
            )
        else:
            referenced_sources.add(source_id)

    # Engineering decisions.
    decisions = knowledge.get("engineering_decisions", {})
    if not isinstance(decisions, dict):
        errors.append("engineering_decisions: expected a mapping")
        decisions = {}

    supported_now = as_list(
        decisions.get("supported_now", []),
        "engineering_decisions.supported_now",
        errors,
    )

    for index, decision in enumerate(supported_now):
        if not isinstance(decision, dict):
            errors.append(
                f"engineering_decisions.supported_now[{index}]: "
                "expected a mapping"
            )
            continue

        text = decision.get("decision")
        if not isinstance(text, str) or not text.strip():
            errors.append(
                f"engineering_decisions.supported_now[{index}]: "
                "missing decision"
            )

        refs = decision.get("sources", [])
        validate_source_refs(
            refs,
            label=(
                f"engineering_decisions.supported_now[{index}].sources"
            ),
            known_sources=known_sources,
            errors=errors,
        )

        if isinstance(refs, list):
            referenced_sources.update(
                source_id
                for source_id in refs
                if isinstance(source_id, str)
            )

    open_specs = as_list(
        decisions.get("open_specifications", []),
        "engineering_decisions.open_specifications",
        errors,
    )

    validate_unique_ids(
        open_specs,
        id_key="id",
        label="engineering_decisions.open_specifications",
        errors=errors,
    )

    for index, spec in enumerate(open_specs):
        if not isinstance(spec, dict):
            continue

        prefix = f"engineering_decisions.open_specifications[{index}]"

        for key in ("specification", "status", "reason"):
            value = spec.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}: missing or empty {key!r}")

        if spec.get("status") != "open":
            errors.append(
                f"{prefix}: expected status 'open', found "
                f"{spec.get('status')!r}"
            )

        refs = spec.get("sources", [])
        validate_source_refs(
            refs,
            label=f"{prefix}.sources",
            known_sources=known_sources,
            errors=errors,
        )

        if isinstance(refs, list):
            referenced_sources.update(
                source_id
                for source_id in refs
                if isinstance(source_id, str)
            )

    # Every source used in the knowledge body should also be declared.
    undeclared = sorted(referenced_sources - declared_ids)
    for source_id in undeclared:
        errors.append(
            f"source {source_id!r} is referenced by knowledge content "
            "but missing from source_records"
        )

    # Declared sources that are currently unused are worth noticing but
    # are not necessarily invalid.
    unused = sorted(declared_ids - referenced_sources)
    for source_id in unused:
        warnings.append(
            f"declared source {source_id!r} is not referenced by a "
            "relationship, decision, open specification, or process point"
        )

    # Basic reading-space integrity.
    for field in (
        "reading_path",
        "manufacturing_inputs",
        "absorber_state",
        "detector_response",
        "completion_criteria_v1",
    ):
        values = as_list(knowledge.get(field, []), field, errors)
        if not values:
            errors.append(f"{field}: must not be empty")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an engineering knowledge artifact."
    )
    parser.add_argument(
        "--knowledge",
        type=Path,
        help=(
            "Knowledge YAML path. Defaults to the absorber-manufacturing "
            "knowledge artifact."
        ),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Explicit sensors-becker repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

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

    source_dir = (
        root
        / "engineering_navigator"
        / "absorber_manufacturing"
        / "source_records"
    )

    knowledge = load_yaml(knowledge_path)
    source_records = load_source_records(source_dir)

    errors, warnings = validate_knowledge(
        knowledge,
        source_records=source_records,
    )

    print(f"Knowledge: {knowledge_path.relative_to(root)}")
    print(f"Completed source records: {len(source_records)}")
    print(f"Relationships: {len(knowledge.get('relationships', []))}")
    print(
        "Open specifications:",
        len(
            knowledge.get("engineering_decisions", {}).get(
                "open_specifications", []
            )
        ),
    )
    print(
        "Reported process points:",
        len(knowledge.get("reported_process_points", [])),
    )

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("\nKnowledge validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("\nKnowledge validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
