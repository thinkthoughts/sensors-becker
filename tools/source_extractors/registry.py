"""Registered source extractors."""

from . import source_00, source_01, source_02, source_03, source_04

EXTRACTORS = {
    "SOURCE_00": source_00.extract,
    "SOURCE_01": source_01.extract,
    "SOURCE_02": source_02.extract,
    "SOURCE_03": source_03.extract,
    "SOURCE_04": source_04.extract,
}


def extract_source(source_id: str, scaffold: dict) -> dict:
    if source_id not in EXTRACTORS:
        available = ", ".join(sorted(EXTRACTORS))
        raise ValueError(
            f"No extractor registered for {source_id!r}. Available: {available}"
        )

    completed = EXTRACTORS[source_id](scaffold)

    if completed.get("source_id") != source_id:
        raise ValueError(
            f"Extractor returned {completed.get('source_id')!r}; "
            f"expected {source_id!r}"
        )

    return completed
