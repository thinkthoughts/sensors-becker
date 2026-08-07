"""Select the next engineering notebook from unresolved specifications."""

from __future__ import annotations

from typing import Any

import pandas as pd


def select_next_notebook(
    open_specs_df: pd.DataFrame,
    rules: list[dict[str, Any]],
    source_files: list[str],
    *,
    fallback_id: str = "NB_02_ABSORBER_MANUFACTURING_REFINEMENT",
    fallback_question: str = (
        "Which unresolved absorber-manufacturing specification should be evaluated next?"
    ),
) -> dict[str, Any]:
    """Return the first notebook rule whose open concept is present."""

    open_concepts = (
        set(open_specs_df["concept"])
        if not open_specs_df.empty and "concept" in open_specs_df
        else set()
    )

    for rule in rules:
        if rule["open_concept"] not in open_concepts:
            continue

        prefixes = tuple(rule.get("input_prefixes", []))
        selected_inputs = [
            filename
            for filename in source_files
            if not prefixes or filename.startswith(prefixes)
        ]

        return {
            "id": rule["id"],
            "engineering_question": rule["engineering_question"],
            "inputs": selected_inputs,
            "outputs": rule.get("outputs", []),
        }

    return {
        "id": fallback_id,
        "engineering_question": fallback_question,
        "inputs": source_files,
        "outputs": [
            "ranked unresolved specifications",
            "next measurement plan",
        ],
    }
