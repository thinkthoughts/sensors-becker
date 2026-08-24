"""Reusable process-window construction for Engineering Objects.

This module converts repository evidence into a structured engineering
process-window view without inventing unsupported tolerances.

It distinguishes:

- observed operating points;
- source-supported process variables;
- coupled detector responses;
- candidate process-window dimensions;
- unresolved numerical ranges;
- validation measurements needed to establish those ranges.

The module is intentionally conservative: where replicated evidence is absent,
the numeric range remains unresolved.

Typical use:

    from tools.optimization.process_window_builder import build_process_window

    result = build_process_window(
        engineering_objects={
            "absorber": absorber,
            "electroplating": electroplating,
            "tes": tes,
        },
        source_records=records,
        process_object_id="electroplating",
        response_object_ids=["absorber", "tes"],
    )
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, asdict
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ProcessWindowConfig:
    """Configuration for one process-window synthesis."""

    process_object_id: str
    response_object_ids: tuple[str, ...]
    leading_process_variables: tuple[str, ...]
    leading_response_variables: tuple[str, ...]
    process_value_aliases: tuple[str, ...]


@dataclass(frozen=True)
class ProcessWindowResult:
    """Structured process-window result."""

    process_variables: pd.DataFrame
    quantitative_evidence: pd.DataFrame
    operating_points: pd.DataFrame
    coupled_variables: pd.DataFrame
    candidate_process_window: pd.DataFrame
    validation_matrix: pd.DataFrame
    status: dict[str, Any]


DEFAULT_ELECTROPLATED_BI_CONFIG = ProcessWindowConfig(
    process_object_id="electroplating",
    response_object_ids=("absorber", "tes"),
    leading_process_variables=(
        "Bi_thickness",
        "grain_size",
        "current_density",
        "bias_voltage",
        "plating_rate",
    ),
    leading_response_variables=(
        "low_energy_tail_fraction",
        "quantum_efficiency",
        "energy_resolution",
        "C",
        "G",
    ),
    process_value_aliases=(
        "Bi_thickness",
        "current_density",
        "bias_voltage",
        "plating_rate",
        "Au_seed_thickness",
        "average_grain_size",
        "average_grain_radius",
        "diffraction_grain_size",
        "SEM_grain_size",
        "quantum_efficiency",
        "C",
        "G",
        "delta_E",
        "predicted_delta_E",
        "residual_resistance_ratio",
        "cloud_size",
    ),
)


def _require_mapping(
    mapping: Mapping[str, Any],
    key: str,
    *,
    label: str,
) -> Mapping[str, Any]:
    value = mapping.get(key)
    if not isinstance(value, Mapping):
        raise KeyError(f"{label} {key!r} is missing or is not a mapping")
    return value


def build_process_variable_table(
    process_object: Mapping[str, Any],
) -> pd.DataFrame:
    """Return process-object variables with unresolved range fields."""

    rows: list[dict[str, Any]] = []

    for item in process_object.get("variables", []):
        if not isinstance(item, Mapping):
            continue

        variable_id = item.get("id")
        if not variable_id:
            continue

        rows.append(
            {
                "variable": variable_id,
                "unit": item.get("unit", ""),
                "current_numeric_evidence": "",
                "candidate_range": "",
                "range_status": "not_yet_established",
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "variable",
            "unit",
            "current_numeric_evidence",
            "candidate_range",
            "range_status",
        ],
    )


def collect_quantitative_evidence(
    source_records: Mapping[str, Mapping[str, Any]],
    aliases: Sequence[str],
) -> pd.DataFrame:
    """Flatten source reported_values and keep only relevant variables."""

    allowed = set(aliases)
    rows: list[dict[str, Any]] = []

    for source_id, record in source_records.items():
        for item in record.get("reported_values", []):
            if not isinstance(item, Mapping):
                continue

            variable = item.get("variable")
            if variable not in allowed:
                continue

            rows.append(
                {
                    "source_id": source_id,
                    "object": item.get("object"),
                    "variable": variable,
                    "value": item.get("value"),
                    "unit": item.get("unit"),
                    "condition": item.get("condition"),
                    "source_page": item.get("source_page"),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "source_id",
                "object",
                "variable",
                "value",
                "unit",
                "condition",
                "source_page",
            ]
        )

    return (
        pd.DataFrame(rows)
        .sort_values(["variable", "source_id", "object"])
        .reset_index(drop=True)
    )


def collect_operating_points(
    process_object: Mapping[str, Any],
) -> pd.DataFrame:
    """Collect source-supported operating points from a process object."""

    rows: list[dict[str, Any]] = []

    for point in process_object.get("reported_process_points", []):
        if not isinstance(point, Mapping):
            continue
        rows.append(dict(point))

    return pd.DataFrame(rows)


def build_coupled_variable_table(
    engineering_objects: Mapping[str, Mapping[str, Any]],
    object_ids: Sequence[str],
) -> pd.DataFrame:
    """Collect variables from process-response Engineering Objects."""

    rows: list[dict[str, Any]] = []

    for object_id in object_ids:
        obj = _require_mapping(
            engineering_objects,
            object_id,
            label="Engineering Object",
        )

        for item in obj.get("variables", []):
            if not isinstance(item, Mapping):
                continue
            variable_id = item.get("id")
            if not variable_id:
                continue

            rows.append(
                {
                    "engineering_object": object_id,
                    "variable": variable_id,
                    "unit": item.get("unit", ""),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=["engineering_object", "variable", "unit"]
        )

    return (
        pd.DataFrame(rows)
        .drop_duplicates()
        .sort_values(["engineering_object", "variable"])
        .reset_index(drop=True)
    )


def _observed_values_for(
    quantitative_evidence: pd.DataFrame,
    variable_names: Sequence[str],
) -> list[str]:
    """Return readable observed evidence with object and source provenance."""

    if quantitative_evidence.empty:
        return []

    subset = quantitative_evidence[
        quantitative_evidence["variable"].isin(variable_names)
    ]

    values: list[str] = []

    for _, row in subset.iterrows():
        value = row.get("value")
        unit = row.get("unit") or ""
        source = row.get("source_id") or ""
        obj = row.get("object")
        condition = row.get("condition")

        text = f"{value} {unit}".strip()

        if obj and not pd.isna(obj):
            text += f" — {obj}"

        if condition and not pd.isna(condition):
            text += f" ({condition})"

        if source:
            text += f" [{source}]"

        values.append(text)

    return values


def build_candidate_process_window(
    quantitative_evidence: pd.DataFrame,
    config: ProcessWindowConfig,
) -> pd.DataFrame:
    """Build evidence-aware candidate dimensions without unsupported ranges."""

    dimension_rules = [
        {
            "dimension": "Bi_thickness",
            "aliases": ["Bi_thickness"],
            "engineering_role": "stopping power + thermalization",
            "unresolved_status": "requires_controlled_thickness_series",
        },
        {
            "dimension": "grain_size",
            "aliases": [
                "grain_size",
                "average_grain_size",
                "average_grain_radius",
                "diffraction_grain_size",
                "SEM_grain_size",
            ],
            "engineering_role": "carrier thermalization + spectral tail",
            "unresolved_status": "acceptance_threshold_not_established",
        },
        {
            "dimension": "current_density",
            "aliases": ["current_density"],
            "engineering_role": "electroplating process control",
            "unresolved_status": "process_tolerance_not_established",
        },
        {
            "dimension": "bias_voltage",
            "aliases": ["bias_voltage"],
            "engineering_role": "electroplating process control",
            "unresolved_status": "process_tolerance_not_established",
        },
        {
            "dimension": "plating_rate",
            "aliases": ["plating_rate"],
            "engineering_role": "deposition kinetics + microstructure",
            "unresolved_status": "process_tolerance_not_established",
        },
    ]

    selected = set(config.leading_process_variables)
    rows: list[dict[str, Any]] = []

    for rule in dimension_rules:
        if rule["dimension"] not in selected:
            continue

        observed = _observed_values_for(
            quantitative_evidence,
            rule["aliases"],
        )

        rows.append(
            {
                "dimension": rule["dimension"],
                "engineering_role": rule["engineering_role"],
                "observed_evidence": "; ".join(observed),
                "candidate_range": "",
                "range_status": rule["unresolved_status"],
            }
        )

    return pd.DataFrame(rows)


def build_validation_matrix(
    config: ProcessWindowConfig,
) -> pd.DataFrame:
    """Return the default experiment plan required to establish a window."""

    templates = {
        "Bi_thickness": {
            "strategy": "controlled sweep",
            "held_constant": "electroplating chemistry + TES + membrane",
            "primary_response": "low_energy_tail_fraction",
            "secondary_responses": "quantum_efficiency, C, energy_resolution",
            "measurement": "x-ray spectrum + thermal characterization",
        },
        "current_density": {
            "strategy": "controlled sweep around reported operating point",
            "held_constant": "Bi_thickness + bath + geometry",
            "primary_response": "grain_size_distribution",
            "secondary_responses": "morphology, spectral response",
            "measurement": "SEM / diffraction + TES spectrum",
        },
        "bias_voltage": {
            "strategy": "controlled sweep around reported operating point",
            "held_constant": "Bi_thickness + bath + geometry",
            "primary_response": "grain_size_distribution",
            "secondary_responses": "morphology, spectral response",
            "measurement": "SEM / diffraction + TES spectrum",
        },
        "plating_rate": {
            "strategy": "controlled sweep",
            "held_constant": "Bi_thickness + bath + geometry",
            "primary_response": "grain_size_distribution",
            "secondary_responses": "roughness, spectral response",
            "measurement": "SEM / diffraction + TES spectrum",
        },
        "grain_size": {
            "strategy": "acceptance-threshold study",
            "held_constant": "nominal absorber thickness + detector design",
            "primary_response": "low_energy_tail_fraction",
            "secondary_responses": "energy_resolution, repeatability",
            "measurement": "SEM / diffraction + TES spectrum",
        },
    }

    rows: list[dict[str, Any]] = []

    for variable in config.leading_process_variables:
        template = templates.get(variable)
        if template is None:
            continue

        rows.append(
            {
                "input_variable": variable,
                **template,
            }
        )

    rows.append(
        {
            "input_variable": "batch",
            "strategy": "replicated production batches",
            "held_constant": "nominal process recipe",
            "primary_response": "repeatability",
            "secondary_responses": "yield, grain size, tail fraction",
            "measurement": "multi-wafer statistical characterization",
        }
    )

    return pd.DataFrame(rows)


def build_status(
    *,
    config: ProcessWindowConfig,
    operating_points: pd.DataFrame,
    candidate_process_window: pd.DataFrame,
) -> dict[str, Any]:
    """Describe current engineering maturity of the process window."""

    unresolved = 0
    if not candidate_process_window.empty:
        unresolved = int(
            (
                candidate_process_window["candidate_range"]
                .fillna("")
                .astype(str)
                .str.strip()
                == ""
            ).sum()
        )

    numeric_established = bool(
        len(candidate_process_window) > 0 and unresolved == 0
    )

    return {
        "status": (
            "numeric_process_window_established"
            if numeric_established
            else "measurement_plan_ready"
        ),
        "numeric_process_window_established": numeric_established,
        "source_supported_operating_points": int(len(operating_points)),
        "leading_process_variables": list(config.leading_process_variables),
        "leading_detector_responses": list(
            config.leading_response_variables
        ),
        "unresolved_process_dimensions": unresolved,
        "next_engineering_step": (
            "Validate replicated process-to-response measurements and "
            "populate numerical candidate ranges."
            if not numeric_established
            else "Validate candidate ranges across independent batches."
        ),
    }


def build_process_window(
    *,
    engineering_objects: Mapping[str, Mapping[str, Any]],
    source_records: Mapping[str, Mapping[str, Any]],
    config: ProcessWindowConfig = DEFAULT_ELECTROPLATED_BI_CONFIG,
) -> ProcessWindowResult:
    """Build one evidence-grounded process-window package."""

    process_object = _require_mapping(
        engineering_objects,
        config.process_object_id,
        label="Engineering Object",
    )

    process_variables = build_process_variable_table(process_object)

    quantitative_evidence = collect_quantitative_evidence(
        source_records,
        config.process_value_aliases,
    )

    operating_points = collect_operating_points(process_object)

    coupled_ids = (
        config.process_object_id,
        *config.response_object_ids,
    )
    coupled_variables = build_coupled_variable_table(
        engineering_objects,
        coupled_ids,
    )

    candidate_process_window = build_candidate_process_window(
        quantitative_evidence,
        config,
    )

    validation_matrix = build_validation_matrix(config)

    status = build_status(
        config=config,
        operating_points=operating_points,
        candidate_process_window=candidate_process_window,
    )

    return ProcessWindowResult(
        process_variables=process_variables,
        quantitative_evidence=quantitative_evidence,
        operating_points=operating_points,
        coupled_variables=coupled_variables,
        candidate_process_window=candidate_process_window,
        validation_matrix=validation_matrix,
        status=status,
    )


def result_as_dict(
    result: ProcessWindowResult,
) -> dict[str, Any]:
    """Return JSON-serializable process-window metadata and tables."""

    return {
        "status": result.status,
        "process_variables": result.process_variables.to_dict("records"),
        "quantitative_evidence": result.quantitative_evidence.to_dict("records"),
        "operating_points": result.operating_points.to_dict("records"),
        "coupled_variables": result.coupled_variables.to_dict("records"),
        "candidate_process_window": (
            result.candidate_process_window.to_dict("records")
        ),
        "validation_matrix": result.validation_matrix.to_dict("records"),
    }
