"""Generate candidate and open specifications from synthesis evidence."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd


def generate_candidate_specifications(
    relationships_df: pd.DataFrame,
    rules: list[dict[str, Any]],
    *,
    spec_prefix: str = "SPEC_AM",
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    """Generate candidate specifications from cross-source concept support."""

    if relationships_df.empty:
        concept_index: dict[str, dict[str, Any]] = {}
    else:
        concept_index = relationships_df.set_index("concept").to_dict("index")

    candidates: list[dict[str, Any]] = []
    spec_number = 1

    for rule in rules:
        concept = rule["concept"]
        result = concept_index.get(concept, {})
        min_sources = int(rule.get("min_sources", 1))

        if int(result.get("source_count", 0)) < min_sources:
            continue

        candidates.append(
            {
                "spec_id": f"{spec_prefix}_{spec_number:02d}",
                "concept": concept,
                "specification": rule["specification"],
                "evidence": result.get("sources", []),
                "source_count": int(result.get("source_count", 0)),
                "state": "source_supported_candidate",
                "next_validation": rule.get("next_validation", ""),
            }
        )
        spec_number += 1

    return candidates, pd.DataFrame(candidates)


def collect_unreported_gaps(
    records: Mapping[str, Mapping[str, Any]],
) -> pd.DataFrame:
    """Flatten all unreported_variables into one source-tagged table."""

    rows: list[dict[str, str]] = []

    for source_id, record in records.items():
        for gap in record.get("unreported_variables", []):
            rows.append(
                {
                    "source_id": source_id,
                    "gap": str(gap),
                }
            )

    return pd.DataFrame(rows, columns=["source_id", "gap"])


def generate_open_specifications(
    gaps_df: pd.DataFrame,
    rules: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    """Generate unresolved engineering specifications from source-record gaps."""

    open_items: list[dict[str, Any]] = []

    for rule in rules:
        if gaps_df.empty:
            continue

        keywords = [str(k).lower() for k in rule.get("keywords", [])]

        mask = gaps_df["gap"].str.lower().apply(
            lambda text: any(keyword in text for keyword in keywords)
        )
        matches = gaps_df[mask]

        if matches.empty:
            continue

        sources = sorted(matches["source_id"].unique().tolist())

        open_items.append(
            {
                "concept": rule["concept"],
                "open_specification": rule["open_specification"],
                "why_open": "; ".join(
                    sorted(matches["gap"].unique().tolist())
                ),
                "gap_sources": sources,
                "source_count": len(sources),
                "next_measurement": rule.get("next_measurement", ""),
            }
        )

    if not open_items:
        return open_items, pd.DataFrame(
            columns=[
                "concept",
                "open_specification",
                "why_open",
                "gap_sources",
                "source_count",
                "next_measurement",
            ]
        )

    frame = (
        pd.DataFrame(open_items)
        .sort_values(
            ["source_count", "open_specification"],
            ascending=[False, True],
        )
        .reset_index(drop=True)
    )

    return open_items, frame
