"""Build and refresh Engineering Object YAML files.

The object builder sits between structured source records / synthesis outputs
and repository-wide engineering objects.

It preserves the stable identity and manually curated structure of each
engineering object while refreshing evidence-derived fields.

Expected repository layout:

engineering_navigator/
    absorber_manufacturing/
        source_records/
            SOURCE_*.yaml

    engineering_objects/
        absorber.yaml
        electroplating.yaml
        tes.yaml
        membrane.yaml
        detector_module.yaml

outputs/
    engineering_questions/
        absorber_manufacturing/
            SYNTHESIS_01/
                synthesis_summary.json

Usage:

    python3 tools/engineering_objects/object_builder.py

Preview one object:

    python3 tools/engineering_objects/object_builder.py --object absorber

Write all refreshed objects:

    python3 tools/engineering_objects/object_builder.py --write

Write one object:

    python3 tools/engineering_objects/object_builder.py \
        --object absorber \
        --write

The builder is conservative:
- it does not invent source evidence;
- it preserves object fields that are not generated;
- it refreshes only fields explicitly managed by this module.
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
    },
}


def find_repo_root(start: Path | None = None) -> Path:
    """Find repository root containing engineering_navigator/."""
    start = (start or Path.cwd()).resolve()

    for candidate in (start, *start.parents):
        if (candidate / "engineering_navigator").is_dir():
            return candidate

    raise FileNotFoundError(
        "Could not locate repository root containing engineering_navigator/."
    )


def load_yaml(path: Path) -> dict[str, Any]:
    """Load one YAML mapping."""
    if not path.exists():
        raise FileNotFoundError(path)

    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise TypeError(f"{path}: expected one top-level YAML mapping")

    return data


def dump_yaml(data: dict[str, Any]) -> str:
    """Serialize repository YAML consistently."""
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        width=110,
    )


def normalize_text(value: Any) -> str:
    """Convert arbitrary nested evidence to searchable lowercase text."""
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
    """Build searchable text from source-record engineering evidence."""
    fields = [
        record.get("title"),
        record.get("materials"),
        record.get("fabrication_methods"),
        record.get("design_variables"),
        record.get("measured_outcomes"),
        record.get("engineering_relationships"),
        record.get("engineering_constraints"),
        record.get("future_questions"),
        record.get("unreported_variables"),
    ]
    return normalize_text(fields)


def load_source_records(source_dir: Path) -> dict[str, dict[str, Any]]:
    """Load completed SOURCE_*.yaml records from one source-record directory."""
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
    """Load synthesis_summary.json if present."""
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
    """Return True where source evidence is relevant to the object."""
    text = source_search_text(record)

    return any(
        keyword.lower() in text
        for keyword in rule.get("source_keywords", set())
    )


def relevant_sources(
    records: dict[str, dict[str, Any]],
    rule: dict[str, Any],
) -> list[str]:
    """Return canonical source IDs relevant to one object."""
    return sorted(
        source_id
        for source_id, record in records.items()
        if source_matches_object(record, rule)
    )


def relevant_relationships(
    records: dict[str, dict[str, Any]],
    source_ids: Iterable[str],
) -> list[dict[str, Any]]:
    """Collect source-derived engineering relationships for an object."""
    results: list[dict[str, Any]] = []

    for source_id in source_ids:
        record = records[source_id]

        for item in record.get("engineering_relationships", []):
            if not isinstance(item, dict):
                continue

            relationship = str(item.get("relationship", "")).strip()
            effect = str(item.get("engineering_effect", "")).strip()

            if not relationship:
                continue

            results.append(
                {
                    "statement": relationship,
                    "engineering_effect": effect,
                    "source": source_id,
                    "source_pages": item.get("source_pages", []),
                }
            )

    return results


def relevant_candidate_specs(
    synthesis: dict[str, Any],
    rule: dict[str, Any],
) -> list[dict[str, Any]]:
    """Select synthesis candidate specifications for one object."""
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
    """Select synthesis open specifications for one object."""
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


def build_evidence_summary(
    object_id: str,
    evidence_sources: list[str],
    evidence: list[dict[str, Any]],
    candidate_specs: list[dict[str, Any]],
    open_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create a compact machine-readable object status summary."""
    return {
        "object_id": object_id,
        "source_count": len(evidence_sources),
        "relationship_count": len(evidence),
        "candidate_specification_count": len(candidate_specs),
        "open_specification_count": len(open_specs),
    }


def refresh_object(
    current: dict[str, Any],
    records: dict[str, dict[str, Any]],
    synthesis: dict[str, Any],
) -> dict[str, Any]:
    """Return one refreshed Engineering Object mapping."""
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
    evidence = relevant_relationships(records, evidence_sources)
    candidate_specs = relevant_candidate_specs(synthesis, rule)
    open_specs = relevant_open_specs(synthesis, rule)

    updated["evidence_sources"] = evidence_sources
    updated["current_evidence"] = evidence
    updated["candidate_specifications"] = candidate_specs
    updated["open_specifications"] = open_specs
    updated["evidence_summary"] = build_evidence_summary(
        object_id,
        evidence_sources,
        evidence,
        candidate_specs,
        open_specs,
    )
    updated["object_build"] = {
        "builder": "engineering-objects-object-builder-v1",
        "managed_fields": sorted(MANAGED_FIELDS),
    }

    return updated


def unified_diff(
    path: Path,
    old_text: str,
    new_text: str,
) -> str:
    """Return a unified diff for preview mode."""
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
    """Preview or write refreshed Engineering Object YAML files."""
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

    paths = [
        path
        for path in paths
        if path.name != "README.yaml"
    ]

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
        help="Refresh one object by id, e.g. absorber",
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
