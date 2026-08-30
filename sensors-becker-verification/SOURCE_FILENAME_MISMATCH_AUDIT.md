# Repo-Wide Audit: `source_file` Filename Mismatch

Found while building V2 source-content verification for RP_37 (see `SENSORS_BECKER_SG_AUDIT.md` and the RP_37 notebook's V2 cell). Recorded separately per the explicit instruction not to fix this opportunistically as part of the RP_37 work.

## The mismatch

Every `source.source_file` field referencing Dan Becker's paper says `"Daniel Becker (1).pdf"`. The actual committed file, in `authors-becker/`, is `"Daniel Becker.pdf"` — no `(1)`. Any code that opens the file by the stated name will fail (this is exactly what RP_37's new V2 verification cell hit on its first run).

## Root cause, not just occurrence count

`templates/RP_TEMPLATE.yaml` line 80 has the wrong filename hardcoded:

```yaml
source_file: Daniel Becker (1).pdf
```

Every affected file inherited this value from the template at generation time, rather than each notebook independently discovering or verifying the actual committed filename. This is one error, propagated, not seventeen independent ones — which matters for how to fix it: correcting `RP_TEMPLATE.yaml` stops the error from propagating to future Reading Points, but does not retroactively fix the 16 files that already copied the wrong value from it.

## Full extent (17 occurrences, 12 files)

**The template itself:**
- `templates/RP_TEMPLATE.yaml`

**Generated/committed RP specifications, all three existing Reading Points:**
- `templates/specifications/RP_37_A.yaml`, `RP_37_B.yaml`, `RP_37_C.yaml`
- `templates/specifications/RP_43_A.yaml`, `RP_43_B.yaml`, `RP_43_C.yaml`
- `templates/specifications/RP_47_A.yaml`, `RP_47_B.yaml`, `RP_47_C.yaml`

**Extraction notebooks (hardcoded `SOURCE` dict), all three:**
- `notebooks/NB_00_RP_37_SOURCE_EXTRACTION.ipynb`
- `notebooks/NB_00_RP_43_SOURCE_EXTRACTION.ipynb`
- `notebooks/NB_00_RP_47_SOURCE_EXTRACTION.ipynb`

**Notebook-generated output artifacts (regenerated on every run, not independently authored):**
- `notebooks/outputs/source_extraction/becker_2025_arpa_e/becker_2025_source_extraction.{json,yaml}`
- `notebooks/outputs/source_extraction/becker_2025_arpa_e/RP_37_{A,B,C}.yaml`

The last group doesn't need separate fixing — they're regenerated from the notebook's own `SOURCE` dict every run, so fixing the notebook fixes these automatically on next execution. The template and the three notebooks are the actual independent places the value is authored; the nine `templates/specifications/RP_*.yaml` files are downstream copies that would need their own correction even after the template and notebooks are fixed, since nothing currently regenerates them automatically from a single source of truth.

## What this doesn't affect

`authors-hawkley/` contains no PDF yet (only placeholder files) — no Reading Point has been built from a Hawkley source, so there's nothing there to check.

## Not fixed here

Per instruction, this document records the finding; it does not apply the fix. A reasonable order, if this is picked up: (1) fix `RP_TEMPLATE.yaml` so no future Reading Point inherits the error, (2) fix the three notebooks' `SOURCE` dicts, (3) decide whether to hand-correct the nine existing `templates/specifications/RP_*.yaml` files or regenerate them by rerunning each notebook (the latter is cleaner if rerunning is safe, but would need checking that regeneration doesn't disturb anything else in those files first).
