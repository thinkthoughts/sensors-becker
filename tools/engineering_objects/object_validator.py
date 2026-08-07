"""Validate Engineering Object YAML files and cross-object relationships."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = {
    "schema_version",
    "repository",
    "id",
    "title",
    "engineering_driver",
    "object_type",
    "object_status",
    "objective",
    "evidence_sources",
    "relationships",
}

ALLOWED_RELATION_TYPES = {
    "manufactured_by",
    "thermally_coupled_to",
    "thermally_supported_by",
    "integrates_into",
    "produces",
    "constrains_component_quality",
    "receives_thermal_energy_from",
    "thermally_linked_by",
    "thermally_links",
    "supports_detector_thermal_path",
    "contains",
    "supports",
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
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level mapping")
    return data


def load_objects(object_dir: Path) -> dict[str, dict[str, Any]]:
    objects = {}
    for path in sorted(object_dir.glob("*.yaml")):
        obj = load_yaml(path)
        object_id = obj.get("id")
        if not object_id:
            raise ValueError(f"{path}: missing id")
        if object_id in objects:
            raise ValueError(f"Duplicate Engineering Object id: {object_id}")
        objects[object_id] = obj
    if not objects:
        raise FileNotFoundError(f"No Engineering Object YAML files in {object_dir}")
    return objects


def load_source_ids(repo_root: Path) -> set[str]:
    ids = set()
    for path in (
        repo_root / "engineering_navigator"
    ).glob("*/source_records/SOURCE_*.yaml"):
        if path.name.endswith(".scaffold.yaml"):
            continue
        try:
            record = load_yaml(path)
        except Exception:
            continue
        source_id = record.get("source_id")
        if source_id:
            ids.add(str(source_id))
    return ids


def validate_object(
    object_id: str,
    obj: dict[str, Any],
    all_objects: dict[str, dict[str, Any]],
    source_ids: set[str],
) -> list[str]:
    errors = []

    missing = sorted(REQUIRED_FIELDS.difference(obj))
    for field in missing:
        errors.append(f"{object_id}: missing required field {field!r}")

    if obj.get("id") != object_id:
        errors.append(
            f"{object_id}: YAML id {obj.get('id')!r} does not match filename/object key"
        )

    evidence_sources = obj.get("evidence_sources", [])
    if not isinstance(evidence_sources, list):
        errors.append(f"{object_id}: evidence_sources must be a list")
    else:
        for source_id in evidence_sources:
            if source_id not in source_ids:
                errors.append(
                    f"{object_id}: unknown evidence source {source_id!r}"
                )

    relationships = obj.get("relationships", [])
    if not isinstance(relationships, list):
        errors.append(f"{object_id}: relationships must be a list")
    else:
        for index, rel in enumerate(relationships):
            if not isinstance(rel, dict):
                errors.append(
                    f"{object_id}: relationships[{index}] must be a mapping"
                )
                continue

            target = rel.get("to")
            rel_type = rel.get("type")

            if not target:
                errors.append(
                    f"{object_id}: relationships[{index}] missing 'to'"
                )
            elif target not in all_objects:
                # External/future object edges are allowed only if explicitly marked.
                if not rel.get("external", False):
                    errors.append(
                        f"{object_id}: relationship target {target!r} "
                        "does not exist; add the object or set external: true"
                    )

            if not rel_type:
                errors.append(
                    f"{object_id}: relationships[{index}] missing 'type'"
                )
            elif rel_type not in ALLOWED_RELATION_TYPES:
                errors.append(
                    f"{object_id}: unsupported relationship type {rel_type!r}"
                )

    for field in (
        "candidate_specifications",
        "open_specifications",
        "current_evidence",
    ):
        if field in obj and not isinstance(obj[field], list):
            errors.append(f"{object_id}: {field} must be a list")

    summary = obj.get("evidence_summary")
    if summary is not None:
        if not isinstance(summary, dict):
            errors.append(f"{object_id}: evidence_summary must be a mapping")
        elif summary.get("object_id") not in (None, object_id):
            errors.append(
                f"{object_id}: evidence_summary.object_id mismatch"
            )

    return errors


def validate_repository(repo_root: Path) -> list[str]:
    object_dir = (
        repo_root / "engineering_navigator" / "engineering_objects"
    )
    objects = load_objects(object_dir)
    source_ids = load_source_ids(repo_root)

    errors = []
    for object_id, obj in objects.items():
        errors.extend(
            validate_object(object_id, obj, objects, source_ids)
        )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Engineering Object YAML files."
    )
    parser.add_argument("--repo-root", type=Path)
    args = parser.parse_args()

    repo_root = (
        args.repo_root.resolve()
        if args.repo_root
        else find_repo_root()
    )

    errors = validate_repository(repo_root)

    if errors:
        print("Engineering Object validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Engineering Object validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
