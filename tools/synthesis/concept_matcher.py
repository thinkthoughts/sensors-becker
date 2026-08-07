"""Concept matching and cross-source relationship synthesis."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd


def searchable_record_text(record: Mapping[str, Any]) -> str:
    """Return normalized searchable text from synthesis-relevant record fields."""
    chunks: list[str] = []

    for field in (
        "design_variables",
        "engineering_relationships",
        "engineering_constraints",
        "future_questions",
        "unreported_variables",
    ):
        chunks.append(str(record.get(field, "")))

    return " ".join(chunks).lower()


def build_engineering_axis_matrix(
    records: Mapping[str, Mapping[str, Any]],
    engineering_axes: list[dict[str, Any]],
) -> pd.DataFrame:
    """Build a source-by-engineering-axis support matrix."""

    rows: list[dict[str, Any]] = []

    for axis in engineering_axes:
        axis_id = axis["id"]
        aliases = set(axis.get("aliases", []))
        keywords = [str(k).lower() for k in axis.get("keywords", [])]

        row: dict[str, Any] = {"engineering_axis": axis_id}
        source_count = 0

        for source_id, record in records.items():
            variable_ids = {
                item.get("id")
                for item in record.get("design_variables", [])
                if isinstance(item, dict) and item.get("id")
            }

            alias_hits = sorted(variable_ids.intersection(aliases))
            text = searchable_record_text(record)
            keyword_hits = sorted(k for k in keywords if k in text)

            evidence = alias_hits or keyword_hits
            row[source_id] = ", ".join(alias_hits or keyword_hits) if evidence else "—"
            source_count += int(bool(evidence))

        row["source_count"] = source_count
        rows.append(row)

    if not rows:
        return pd.DataFrame(columns=["engineering_axis", "source_count"])

    return (
        pd.DataFrame(rows)
        .sort_values(["source_count", "engineering_axis"], ascending=[False, True])
        .reset_index(drop=True)
    )


def relationship_text(item: Mapping[str, Any]) -> str:
    """Normalize one source relationship for concept matching."""
    return (
        f"{item.get('relationship', '')} "
        f"{item.get('engineering_effect', '')}"
    ).lower()


def concept_matches(text: str, concept: Mapping[str, Any]) -> bool:
    """Return True where text satisfies every required keyword group."""
    groups = concept.get("required_keyword_groups", [])

    for group in groups:
        normalized = [str(keyword).lower() for keyword in group]
        if not any(keyword in text for keyword in normalized):
            return False

    return True


def collect_source_relationships(
    records: Mapping[str, Mapping[str, Any]],
    concepts: list[dict[str, Any]],
) -> pd.DataFrame:
    """Collect source relationships and attach matching concept IDs."""

    rows: list[dict[str, Any]] = []

    for source_id, record in records.items():
        for index, item in enumerate(record.get("engineering_relationships", [])):
            if not isinstance(item, dict):
                continue

            text = relationship_text(item)
            matched = [
                concept["id"]
                for concept in concepts
                if concept_matches(text, concept)
            ]

            rows.append(
                {
                    "source_id": source_id,
                    "relationship_index": index,
                    "relationship": item.get("relationship", ""),
                    "engineering_effect": item.get("engineering_effect", ""),
                    "source_pages": item.get("source_pages", []),
                    "concepts": matched,
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "source_id",
            "relationship_index",
            "relationship",
            "engineering_effect",
            "source_pages",
            "concepts",
        ],
    )


def match_relationship_concepts(
    source_relationships_df: pd.DataFrame,
    concepts: list[dict[str, Any]],
) -> pd.DataFrame:
    """Aggregate concept support across independent source records."""

    rows: list[dict[str, Any]] = []

    for concept in concepts:
        concept_id = concept["id"]

        if source_relationships_df.empty:
            supporting = source_relationships_df
        else:
            supporting = source_relationships_df[
                source_relationships_df["concepts"].apply(
                    lambda values: concept_id in values
                )
            ]

        sources = (
            sorted(supporting["source_id"].unique().tolist())
            if not supporting.empty
            else []
        )

        rows.append(
            {
                "concept": concept_id,
                "category": concept.get("category", ""),
                "source_count": len(sources),
                "sources": sources,
                "relationship_count": len(supporting),
                "status": (
                    "supported_across_sources"
                    if len(sources) >= 2
                    else "single_source_support"
                    if len(sources) == 1
                    else "unsupported"
                ),
            }
        )

    if not rows:
        return pd.DataFrame(
            columns=[
                "concept",
                "category",
                "source_count",
                "sources",
                "relationship_count",
                "status",
            ]
        )

    return (
        pd.DataFrame(rows)
        .sort_values(["source_count", "concept"], ascending=[False, True])
        .reset_index(drop=True)
    )
