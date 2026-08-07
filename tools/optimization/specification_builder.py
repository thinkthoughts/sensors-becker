"""Build candidate engineering specifications from process-window evidence.

This module consumes a ProcessWindowResult from process_window_builder.py and
turns its evidence state into structured candidate specifications.

It is intentionally conservative:
- observed values remain evidence, not tolerances;
- numerical ranges are emitted only when candidate_range is populated;
- unresolved dimensions become explicit open specifications;
- validation requirements remain attached to each candidate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .process_window_builder import ProcessWindowResult


@dataclass(frozen=True)
class SpecificationResult:
    """Structured engineering-specification result."""

    candidate_specifications: pd.DataFrame
    open_specifications: pd.DataFrame
    validation_requirements: pd.DataFrame
    status: dict[str, Any]


DEFAULT_SPECIFICATION_TEMPLATES = {
    "Bi_thickness": {
        "title": "Electroplated Bi thickness",
        "requirement": (
            "Control electroplated-bismuth thickness as a coupled "
            "stopping-power and thermalization variable."
        ),
        "validation_target": (
            "Confirm quantum efficiency, low-energy tail fraction, "
            "heat capacity, and energy resolution across the thickness range."
        ),
    },
    "grain_size": {
        "title": "Electroplated Bi grain size",
        "requirement": (
            "Track bismuth grain size or an equivalent morphology metric "
            "as an absorber acceptance variable."
        ),
        "validation_target": (
            "Establish a quantitative relationship between grain-size "
            "distribution and spectral-tail fraction."
        ),
    },
    "current_density": {
        "title": "Electroplating current density",
        "requirement": (
            "Control electroplating current density within a validated "
            "process window."
        ),
        "validation_target": (
            "Relate current-density variation to grain size, morphology, "
            "yield, and detector response."
        ),
    },
    "bias_voltage": {
        "title": "Electroplating bias voltage",
        "requirement": (
            "Control electroplating bias voltage within a validated "
            "process window."
        ),
        "validation_target": (
            "Relate bias-voltage variation to grain size, morphology, "
            "yield, and detector response."
        ),
    },
    "plating_rate": {
        "title": "Electroplating rate",
        "requirement": (
            "Control plating rate within a validated process window."
        ),
        "validation_target": (
            "Relate plating-rate variation to grain size, roughness, "
            "repeatability, and detector response."
        ),
    },
}


def _is_resolved_range(value: Any) -> bool:
    """Return True where a candidate numerical range is actually populated."""
    if value is None:
        return False
    text = str(value).strip()
    return bool(text)


def build_candidate_specifications(
    process_window: ProcessWindowResult,
    *,
    templates: dict[str, dict[str, str]] | None = None,
    spec_prefix: str = "SPEC_PW",
) -> pd.DataFrame:
    """Build resolved candidate specifications from populated process ranges."""

    templates = templates or DEFAULT_SPECIFICATION_TEMPLATES
    rows: list[dict[str, Any]] = []
    spec_number = 1

    for _, row in process_window.candidate_process_window.iterrows():
        dimension = row.get("dimension")
        candidate_range = row.get("candidate_range")

        if not _is_resolved_range(candidate_range):
            continue

        template = templates.get(dimension, {})
        rows.append(
            {
                "spec_id": f"{spec_prefix}_{spec_number:02d}",
                "dimension": dimension,
                "title": template.get("title", dimension),
                "requirement": template.get(
                    "requirement",
                    f"Control {dimension} within the validated process window.",
                ),
                "candidate_range": candidate_range,
                "observed_evidence": row.get("observed_evidence", ""),
                "state": "candidate_numeric_specification",
                "validation_target": template.get(
                    "validation_target",
                    "Validate across replicated devices and batches.",
                ),
            }
        )
        spec_number += 1

    return pd.DataFrame(
        rows,
        columns=[
            "spec_id",
            "dimension",
            "title",
            "requirement",
            "candidate_range",
            "observed_evidence",
            "state",
            "validation_target",
        ],
    )


def build_open_specifications(
    process_window: ProcessWindowResult,
    *,
    templates: dict[str, dict[str, str]] | None = None,
) -> pd.DataFrame:
    """Build explicit open specifications for unresolved process dimensions."""

    templates = templates or DEFAULT_SPECIFICATION_TEMPLATES
    rows: list[dict[str, Any]] = []

    for _, row in process_window.candidate_process_window.iterrows():
        dimension = row.get("dimension")
        candidate_range = row.get("candidate_range")

        if _is_resolved_range(candidate_range):
            continue

        template = templates.get(dimension, {})
        rows.append(
            {
                "dimension": dimension,
                "title": template.get("title", dimension),
                "requirement": template.get(
                    "requirement",
                    f"Control {dimension} within a validated process window.",
                ),
                "observed_evidence": row.get("observed_evidence", ""),
                "range_status": row.get("range_status", "unresolved"),
                "state": "open_numeric_specification",
                "next_validation": template.get(
                    "validation_target",
                    "Acquire replicated process-to-response evidence.",
                ),
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "dimension",
            "title",
            "requirement",
            "observed_evidence",
            "range_status",
            "state",
            "next_validation",
        ],
    )


def build_validation_requirements(
    process_window: ProcessWindowResult,
) -> pd.DataFrame:
    """Normalize the process-window validation matrix as specification evidence."""

    if process_window.validation_matrix.empty:
        return pd.DataFrame(
            columns=[
                "input_variable",
                "strategy",
                "held_constant",
                "primary_response",
                "secondary_responses",
                "measurement",
            ]
        )

    return process_window.validation_matrix.copy().reset_index(drop=True)


def build_specification_status(
    candidate_specifications: pd.DataFrame,
    open_specifications: pd.DataFrame,
    process_window: ProcessWindowResult,
) -> dict[str, Any]:
    """Summarize engineering-specification maturity."""

    candidate_count = len(candidate_specifications)
    open_count = len(open_specifications)

    return {
        "status": (
            "candidate_numeric_specifications_available"
            if candidate_count > 0
            else "numeric_specifications_open"
        ),
        "candidate_numeric_specification_count": candidate_count,
        "open_numeric_specification_count": open_count,
        "source_supported_operating_points": int(
            len(process_window.operating_points)
        ),
        "process_window_status": process_window.status.get("status"),
        "ready_for_numeric_specification": candidate_count > 0,
        "next_engineering_step": (
            "Validate candidate numerical specifications across independent batches."
            if candidate_count > 0
            else "Acquire replicated process-to-response measurements and populate candidate ranges."
        ),
    }


def build_specification(
    process_window: ProcessWindowResult,
    *,
    templates: dict[str, dict[str, str]] | None = None,
    spec_prefix: str = "SPEC_PW",
) -> SpecificationResult:
    """Build the complete specification package from one process-window result."""

    candidate_specifications = build_candidate_specifications(
        process_window,
        templates=templates,
        spec_prefix=spec_prefix,
    )

    open_specifications = build_open_specifications(
        process_window,
        templates=templates,
    )

    validation_requirements = build_validation_requirements(
        process_window
    )

    status = build_specification_status(
        candidate_specifications,
        open_specifications,
        process_window,
    )

    return SpecificationResult(
        candidate_specifications=candidate_specifications,
        open_specifications=open_specifications,
        validation_requirements=validation_requirements,
        status=status,
    )
