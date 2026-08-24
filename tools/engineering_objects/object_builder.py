"""Build and refresh Engineering Object YAML files.

Version 2 integrates source-level `reported_process_points` into process
Engineering Objects, beginning with `electroplating.yaml`.

The builder preserves stable/manual object structure while refreshing only
evidence-derived fields.

Usage:

    python3 tools/engineering_objects/object_builder.py

Preview one object:

    python3 tools/engineering_objects/object_builder.py --object electroplating

Write all refreshed objects:

    python3 tools/engineering_objects/object_builder.py --write
"""

from __future__ import annotations

import argparse
import copy
import difflib
import json
from pathlib import Path
from typing import Any, Iterable

import yaml


MANAGED_FIELDS = {
    "evidence_sources",
    "current_evidence",
    "candidate_specifications",
    "open_specifications",
    "reported_process_points",
    "evidence_summary",
    "object_build",
}


OBJECT_RULES: dict[str, dict[str, Any]] = {
    "absorber": {
        "source_keywords": {
            "absorber",
            "bismuth",
            "gold",
            "grain",
            "morphology",
            "thickness",
            "spectral",
            "tail",
            "quantum efficiency",
            "thermalization",
        },
        "relationship_concepts": {
            "deposition_to_microstructure",
            "microstructure_to_trapping",
            "trapping_to_spectral_response",
            "thickness_to_detector_response",
            "thermal_design_coupling",
        },
        "open_concepts": {
            "grain_size_acceptance",
            "thickness_process_window",
            "process_tolerances",
            "repeatability",
            "yield",
        },
        "collect_reported_process_points": False,
    },
    "electroplating": {
        "source_keywords": {
            "electroplat",
            "plating",
            "deposition",
            "current density",
            "bias voltage",
            "plating rate",
            "bath",
            "seed layer",
            "grain",
            "morphology",
        },
        "relationship_keywords": {
            "current density",
            "grain size",
            "film thickness",
            "bath temperature",
            "crystal orientation",
            "electrical transport",
            "plating rate",
            "deposition",
        },
        "relationship_concepts": {
            "deposition_to_microstructure",
            "microstructure_to_trapping",
        },
        "open_concepts": {
            "process_tolerances",
            "repeatability",
            "yield",
            "grain_size_acceptance",
            "thickness_process_window",
        },
        "collect_reported_process_points": True,
    },
    "tes": {
        "source_keywords": {
            "tes",
            "transition-edge",
            "critical temperature",
            "tc",
            "heat capacity",
            "thermal conductance",
            "alpha",
            "beta",
            "energy resolution",
            "pulse",
        },
        "relationship_concepts": {
            "thermal_design_coupling",
            "trapping_to_spectral_response",
        },
        "open_concepts": {
            "repeatability",
            "yield",
        },
        "collect_reported_process_points": False,
    },
    "membrane": {
        "source_keywords": {
            "membrane",
            "sinx",
            "thermal conductance",
            "thermal link",
            "heat bath",
            "perimeter",
        },
        "relationship_concepts": {
            "thermal_design_coupling",
        },
        "open_concepts": {
            "repeatability",
        },
        "collect_reported_process_points": False,
    },
    "detector_module": {
        "source_keywords": {
            "detector",
            "pixel",
            "array",
            "module",
            "energy resolution",
            "pulse",
            "thermal conductance",
            "heat capacity",
            "spectral response",
        },
        "relationship_concepts": {
            "thermal_design_coupling",
            "trapping_to_spectral_response",
            "thickness_to_detector_response",
        },
        "open_concepts": {
            "repeatability",
            "yield",
            "process_tolerances",
        },
        "collect_reported_process_points": False,
    },
    "instrument_scaling": {
        "source_keywords": {
            "instrument",
            "array",
            "module",
            "pixel count",
            "scaling",
            "readout",
            "heat load",
        },
        "relationship_concepts": set(),
        "open_concepts": {
            "repeatability",
            "yield",
        },
        "collect_reported_process_points": False,
    },
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
        raise FileNotFoundError(path)

    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level YAML mapping")

    return data


def dump_yaml(data: dict[str, Any]) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=110,
    )


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, dict):
        return " ".join(
            f"{normalize_text(key)} {normalize_text(item)}"
            for key, item in value.items()
        ).lower()

    if isinstance(value, (list, tuple, set)):
        return " ".join(normalize_text(item) for item in value).lower()

    return str(value).lower()


def source_search_text(record: dict[str, Any]) -> str:
    fields = [
        record.get("title"),
        record.get("materials"),
        record.get("fabrication_methods"),
        record.get("design_variables"),
        record.get("reported_values"),
        record.get("measured_outcomes"),
        record.get("engineering_relationships"),
        record.get("engineering_constraints"),
        record.get("future_questions"),
        record.get("unreported_variables"),
        record.get("reported_process_points"),
    ]
    return normalize_text(fields)


def load_source_records(source_dir: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    for path in sorted(source_dir.glob("SOURCE_*.yaml")):
        if path.name.endswith(".scaffold.yaml"):
            continue

        record = load_yaml(path)
        source_id = record.get("source_id")

        if not source_id:
            raise KeyError(f"{path}: missing source_id")

        if source_id in records:
            raise ValueError(f"Duplicate source_id: {source_id}")

        records[source_id] = record

    if not records:
        raise FileNotFoundError(
            f"No SOURCE_*.yaml records found in {source_dir}"
        )

    return records


def load_synthesis_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "relationship_concepts": [],
            "candidate_specifications": [],
            "open_specifications": [],
        }

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one JSON object")

    return data


def source_matches_object(
    record: dict[str, Any],
    rule: dict[str, Any],
) -> bool:
    text = source_search_text(record)

    return any(
        keyword.lower() in text
        for keyword in rule.get("source_keywords", set())
    )


def relevant_sources(
    records: dict[str, dict[str, Any]],
    rule: dict[str, Any],
) -> list[str]:
    return sorted(
        source_id
        for source_id, record in records.items()
        if source_matches_object(record, rule)
    )


def relationship_search_text(item: dict[str, Any]) -> str:
    """Return normalized searchable text for one source relationship."""
    fields = [
        item.get("concept"),
        item.get("relationship"),
        item.get("engineering_effect"),
        item.get("from"),
        item.get("to"),
        item.get("basis"),
        item.get("status"),
    ]
    return normalize_text(fields)


def relationship_matches_object(
    item: dict[str, Any],
    rule: dict[str, Any],
) -> bool:
    """Return True where a source relationship belongs to this Engineering Object."""
    text = relationship_search_text(item)

    relationship_keywords = set(
        rule.get(
            "relationship_keywords",
            rule.get("source_keywords", set()),
        )
    )

    return any(
        keyword.lower() in text
        for keyword in relationship_keywords
    )


def normalize_relationship(
    item: dict[str, Any],
    source_id: str,
) -> dict[str, Any] | None:
    """Normalize supported source-relationship schemas for Engineering Objects."""

    relationship = str(item.get("relationship", "")).strip()
    engineering_effect = str(item.get("engineering_effect", "")).strip()

    # Existing SOURCE_00-SOURCE_03-style relationship record.
    if relationship and engineering_effect:
        result: dict[str, Any] = {
            "statement": relationship,
            "engineering_effect": engineering_effect,
            "source": source_id,
        }

    # SOURCE_04-style directional engineering relationship.
    elif relationship and item.get("from") and item.get("to"):
        source_variable = str(item.get("from")).strip()
        target_variable = str(item.get("to")).strip()
        basis = str(item.get("basis", "")).strip()

        result = {
            "statement": (
                f"{source_variable} -> {target_variable}: {relationship}"
            ),
            "engineering_effect": basis,
            "source": source_id,
        }

        if item.get("status"):
            result["evidence_status"] = item["status"]

    else:
        return None

    if "source_pages" in item:
        result["source_pages"] = item.get("source_pages", [])

    if "source_sections" in item:
        result["source_sections"] = item.get("source_sections", [])

    return result


def relevant_relationships(
    records: dict[str, dict[str, Any]],
    source_ids: Iterable[str],
    rule: dict[str, Any],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for source_id in source_ids:
        record = records[source_id]

        for item in record.get("engineering_relationships", []):
            if not isinstance(item, dict):
                continue

            if not relationship_matches_object(item, rule):
                continue

            normalized = normalize_relationship(item, source_id)

            if normalized is not None:
                results.append(normalized)

    return results

def relevant_candidate_specs(
    synthesis: dict[str, Any],
    rule: dict[str, Any],
) -> list[dict[str, Any]]:
    allowed = set(rule.get("relationship_concepts", set()))
    results: list[dict[str, Any]] = []

    for item in synthesis.get("candidate_specifications", []):
        if not isinstance(item, dict):
            continue

        if item.get("concept") not in allowed:
            continue

        results.append(
            {
                "spec_id": item.get("spec_id"),
                "concept": item.get("concept"),
                "specification": item.get("specification"),
                "evidence": item.get("evidence", []),
                "state": item.get("state"),
                "next_validation": item.get("next_validation"),
            }
        )

    return results


def relevant_open_specs(
    synthesis: dict[str, Any],
    rule: dict[str, Any],
) -> list[dict[str, Any]]:
    allowed = set(rule.get("open_concepts", set()))
    results: list[dict[str, Any]] = []

    for item in synthesis.get("open_specifications", []):
        if not isinstance(item, dict):
            continue

        if item.get("concept") not in allowed:
            continue

        results.append(
            {
                "concept": item.get("concept"),
                "open_specification": item.get("open_specification"),
                "gap_sources": item.get("gap_sources", []),
                "source_count": item.get("source_count", 0),
                "next_measurement": item.get("next_measurement"),
            }
        )

    return results


def collect_reported_process_points(
    records: dict[str, dict[str, Any]],
    source_ids: Iterable[str],
) -> list[dict[str, Any]]:
    """Collect and de-duplicate source-supported process operating points."""

    points: list[dict[str, Any]] = []
    seen: set[str] = set()

    for source_id in source_ids:
        record = records[source_id]

        for raw in record.get("reported_process_points", []):
            if not isinstance(raw, dict):
                continue

            point = copy.deepcopy(raw)

            # Preserve source identity even where an older record omitted it.
            point.setdefault("source", source_id)

            # Stable de-duplication across rebuilds and overlapping records.
            fingerprint = json.dumps(
                point,
                sort_keys=True,
                ensure_ascii=False,
                default=str,
            )

            if fingerprint in seen:
                continue

            seen.add(fingerprint)
            points.append(point)

    return points


def build_evidence_summary(
    object_id: str,
    evidence_sources: list[str],
    evidence: list[dict[str, Any]],
    candidate_specs: list[dict[str, Any]],
    open_specs: list[dict[str, Any]],
    process_points: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "object_id": object_id,
        "source_count": len(evidence_sources),
        "relationship_count": len(evidence),
        "candidate_specification_count": len(candidate_specs),
        "open_specification_count": len(open_specs),
        "reported_process_point_count": len(process_points),
    }


def refresh_object(
    current: dict[str, Any],
    records: dict[str, dict[str, Any]],
    synthesis: dict[str, Any],
) -> dict[str, Any]:
    object_id = current.get("id")

    if not object_id:
        raise KeyError("Engineering Object is missing id")

    rule = OBJECT_RULES.get(object_id)

    if rule is None:
        raise KeyError(
            f"No object-builder rule registered for {object_id!r}"
        )

    updated = copy.deepcopy(current)

    evidence_sources = relevant_sources(records, rule)
    evidence = relevant_relationships(
        records,
        evidence_sources,
        rule,
    )
    candidate_specs = relevant_candidate_specs(synthesis, rule)
    open_specs = relevant_open_specs(synthesis, rule)

    if rule.get("collect_reported_process_points", False):
        process_points = collect_reported_process_points(
            records,
            evidence_sources,
        )
    else:
        process_points = []

    updated["evidence_sources"] = evidence_sources
    updated["current_evidence"] = evidence
    updated["candidate_specifications"] = candidate_specs
    updated["open_specifications"] = open_specs

    # Only process Engineering Objects receive this generated field.
    if rule.get("collect_reported_process_points", False):
        updated["reported_process_points"] = process_points
    else:
        updated.pop("reported_process_points", None)

    updated["evidence_summary"] = build_evidence_summary(
        object_id,
        evidence_sources,
        evidence,
        candidate_specs,
        open_specs,
        process_points,
    )

    updated["object_build"] = {
        "builder": "engineering-objects-object-builder-v2",
        "managed_fields": sorted(MANAGED_FIELDS),
    }

    return updated


def unified_diff(
    path: Path,
    old_text: str,
    new_text: str,
) -> str:
    return "".join(
        difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=str(path),
            tofile=f"{path} (generated)",
        )
    )


def build_objects(
    *,
    repo_root: Path,
    object_id: str | None = None,
    write: bool = False,
) -> int:
    source_dir = (
        repo_root
        / "engineering_navigator"
        / "absorber_manufacturing"
        / "source_records"
    )
    object_dir = (
        repo_root
        / "engineering_navigator"
        / "engineering_objects"
    )
    synthesis_path = (
        repo_root
        / "outputs"
        / "engineering_questions"
        / "absorber_manufacturing"
        / "SYNTHESIS_01"
        / "synthesis_summary.json"
    )

    records = load_source_records(source_dir)
    synthesis = load_synthesis_summary(synthesis_path)

    if object_id:
        paths = [object_dir / f"{object_id}.yaml"]
    else:
        paths = sorted(object_dir.glob("*.yaml"))

    if not paths:
        raise FileNotFoundError(
            f"No Engineering Object YAML files found in {object_dir}"
        )

    changed = 0

    for path in paths:
        current = load_yaml(path)
        updated = refresh_object(current, records, synthesis)

        old_text = dump_yaml(current)
        new_text = dump_yaml(updated)

        if old_text == new_text:
            print(f"unchanged: {path.relative_to(repo_root)}")
            continue

        changed += 1

        if write:
            path.write_text(new_text, encoding="utf-8")
            print(f"generated: {path.relative_to(repo_root)}")
        else:
            print(unified_diff(path, old_text, new_text), end="")

    if not write:
        if changed:
            print(
                "\nPreview only. Re-run with --write to update "
                "Engineering Object files."
            )
        else:
            print("No Engineering Object changes detected.")

    return changed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refresh Engineering Object YAML files from source evidence."
    )
    parser.add_argument(
        "--object",
        dest="object_id",
        help="Refresh one object by id, e.g. electroplating",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write refreshed YAML files instead of previewing diffs.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Explicit sensors-becker repository root.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    repo_root = (
        args.repo_root.resolve()
        if args.repo_root
        else find_repo_root()
    )

    build_objects(
        repo_root=repo_root,
        object_id=args.object_id,
        write=args.write,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
