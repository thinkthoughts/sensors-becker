"""Reusable source-record extraction utilities for sensors-becker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
import csv
import json
import shutil
import zipfile

import yaml


class SourceRecordError(ValueError):
    """Raised where a source record or export package is invalid."""


@dataclass(frozen=True)
class SourcePaths:
    repo_root: Path
    source_record: Path
    output_dir: Path
    export_dir: Path
    export_zip: Path


def is_repo_root(path: Path) -> bool:
    """Return True where path looks like the sensors-becker repository root."""
    return (
        path.is_dir()
        and (path / "engineering_navigator").is_dir()
        and (
            path
            / "engineering_navigator"
            / "absorber_manufacturing"
            / "source_records"
        ).is_dir()
    )


def locate_repo_root(
    *,
    start: Path | None = None,
    override: str | Path | None = None,
    repository_url: str = "https://github.com/thinkthoughts/sensors-becker.git",
    auto_clone_colab: bool = True,
) -> Path:
    """Locate a local checkout or clone it under /content in Colab."""

    candidates: list[Path] = []
    if override is not None:
        candidates.append(Path(override).expanduser().resolve())

    start_path = (start or Path.cwd()).resolve()
    candidates.extend([start_path, *start_path.parents])
    candidates.extend(
        [
            Path("/content/sensors-becker"),
            Path("/home/dan/sensors-becker"),
            Path.home() / "sensors-becker",
        ]
    )

    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if is_repo_root(candidate):
            return candidate

    colab_target = Path("/content/sensors-becker")
    if auto_clone_colab and Path("/content").exists():
        if colab_target.exists() and not is_repo_root(colab_target):
            raise FileExistsError(
                f"{colab_target} exists but is not a valid sensors-becker checkout."
            )
        if not colab_target.exists():
            import subprocess

            subprocess.run(
                ["git", "clone", repository_url, str(colab_target)],
                check=True,
            )
        if is_repo_root(colab_target):
            return colab_target

    checked = "\n".join(f"  - {path}" for path in candidates)
    raise FileNotFoundError(
        "Could not locate the sensors-becker repository.\n"
        f"Checked:\n{checked}\n"
        "Set REPO_ROOT_OVERRIDE to the absolute repository path."
    )


def build_source_paths(
    repo_root: Path,
    *,
    source_filename: str,
    source_id: str,
) -> SourcePaths:
    """Build canonical input, output, and export paths."""

    driver_dir = (
        repo_root
        / "engineering_navigator"
        / "absorber_manufacturing"
    )
    source_record = driver_dir / "source_records" / source_filename
    output_dir = (
        repo_root
        / "outputs"
        / "engineering_questions"
        / "absorber_manufacturing"
        / source_id
    )
    export_dir = repo_root / "exports" / source_id
    export_zip = repo_root / "exports" / f"{source_id}_export.zip"

    output_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)
    export_zip.parent.mkdir(parents=True, exist_ok=True)

    if not source_record.exists():
        available = sorted(
            path.name
            for path in (driver_dir / "source_records").glob("*.yaml")
        )
        raise FileNotFoundError(
            f"Source record not found: {source_record}\n"
            f"Available records: {available}"
        )

    return SourcePaths(
        repo_root=repo_root,
        source_record=source_record,
        output_dir=output_dir,
        export_dir=export_dir,
        export_zip=export_zip,
    )


def load_source_record(path: Path) -> dict[str, Any]:
    """Load and validate the source-record scaffold."""

    try:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SourceRecordError(f"{path}: invalid YAML: {exc}") from exc

    if not isinstance(record, dict):
        raise SourceRecordError(f"{path}: expected one top-level mapping")

    required = {
        "source_id": str,
        "title": str,
        "record_status": str,
        "extraction_status": str,
    }
    for field, expected_type in required.items():
        if field not in record:
            raise SourceRecordError(f"{path}: missing required field {field!r}")
        if not isinstance(record[field], expected_type):
            raise SourceRecordError(
                f"{path}: {field!r} must be {expected_type.__name__}"
            )

    return record


def validate_completed_record(record: Mapping[str, Any]) -> list[str]:
    """Return a list of validation errors; an empty list means PASS."""

    errors: list[str] = []

    required_nonempty = [
        "authors",
        "materials",
        "fabrication_methods",
        "design_variables",
        "reported_values",
        "measured_outcomes",
        "equations",
        "engineering_relationships",
        "engineering_constraints",
        "future_questions",
    ]

    for field in required_nonempty:
        value = record.get(field)
        if not isinstance(value, list) or not value:
            errors.append(f"{field} must be a nonempty list")

    for index, item in enumerate(record.get("reported_values", [])):
        if not isinstance(item, dict):
            errors.append(f"reported_values[{index}] must be a mapping")
            continue
        if "source_page" not in item:
            errors.append(f"reported_values[{index}] lacks source_page")
        for required in ("object", "variable", "value", "unit"):
            if required not in item:
                errors.append(
                    f"reported_values[{index}] lacks {required!r}"
                )

    for index, item in enumerate(record.get("equations", [])):
        if not isinstance(item, dict):
            errors.append(f"equations[{index}] must be a mapping")
            continue
        for required in (
            "id",
            "expression",
            "display",
            "variables",
            "source_page",
            "role",
        ):
            if required not in item:
                errors.append(f"equations[{index}] lacks {required!r}")

    for field in (
        "engineering_relationships",
        "engineering_constraints",
        "measured_outcomes",
        "assumptions",
    ):
        for index, item in enumerate(record.get(field, [])):
            if not isinstance(item, dict):
                errors.append(f"{field}[{index}] must be a mapping")

    return errors


def write_completed_record(
    record: Mapping[str, Any],
    paths: SourcePaths,
) -> dict[str, Path]:
    """Write canonical YAML and tabular outputs, returning actual paths."""

    errors = validate_completed_record(record)
    if errors:
        raise SourceRecordError(
            "Completed source-record validation failed:\n- "
            + "\n- ".join(errors)
        )

    backup_path = paths.source_record.with_name(
        paths.source_record.stem + ".scaffold.yaml"
    )
    if not backup_path.exists():
        shutil.copy2(paths.source_record, backup_path)

    yaml_text = yaml.safe_dump(
        dict(record),
        sort_keys=False,
        allow_unicode=True,
        width=110,
    )
    paths.source_record.write_text(yaml_text, encoding="utf-8")

    values_csv = paths.output_dir / f"{record['source_id']}_reported_values.csv"
    relationships_json = (
        paths.output_dir
        / f"{record['source_id']}_engineering_relationships.json"
    )
    summary_csv = (
        paths.output_dir
        / f"{record['source_id']}_extraction_summary.csv"
    )

    reported_values = list(record["reported_values"])
    fieldnames: list[str] = []
    for row in reported_values:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    with values_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reported_values)

    relationships_json.write_text(
        json.dumps(
            record["engineering_relationships"],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    summary_rows = [
        {"section": field, "records": len(record.get(field, []))}
        for field in (
            "materials",
            "fabrication_methods",
            "design_variables",
            "reported_values",
            "measured_outcomes",
            "equations",
            "engineering_relationships",
            "engineering_constraints",
            "assumptions",
            "future_questions",
            "unreported_variables",
        )
    ]
    with summary_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["section", "records"])
        writer.writeheader()
        writer.writerows(summary_rows)

    return {
        "canonical_yaml": paths.source_record,
        "scaffold_backup": backup_path,
        "reported_values_csv": values_csv,
        "engineering_relationships_json": relationships_json,
        "extraction_summary_csv": summary_csv,
    }


def build_export_package(
    written_files: Mapping[str, Path],
    paths: SourcePaths,
) -> Path:
    """Copy review artifacts into exports/SOURCE_00 and create one ZIP."""

    shutil.rmtree(paths.export_dir, ignore_errors=True)
    paths.export_dir.mkdir(parents=True, exist_ok=True)

    exportable_keys = (
        "canonical_yaml",
        "reported_values_csv",
        "engineering_relationships_json",
        "extraction_summary_csv",
    )

    for key in exportable_keys:
        source = written_files.get(key)
        if source is None:
            raise SourceRecordError(f"Missing written file entry: {key}")
        if not source.exists():
            raise FileNotFoundError(f"Output file does not exist: {source}")
        shutil.copy2(source, paths.export_dir / source.name)

    if paths.export_zip.exists():
        paths.export_zip.unlink()

    with zipfile.ZipFile(
        paths.export_zip,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in sorted(paths.export_dir.iterdir()):
            if path.is_file():
                archive.write(path, arcname=path.name)

    if not paths.export_zip.exists() or paths.export_zip.stat().st_size == 0:
        raise SourceRecordError("Export ZIP was not created correctly")

    return paths.export_zip


def download_in_colab(path: Path) -> bool:
    """Download path in Colab. Return False outside Colab."""

    try:
        from google.colab import files  # type: ignore
    except ImportError:
        return False

    files.download(str(path))
    return True
