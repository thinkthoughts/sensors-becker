# RP_37 Changelog

## v1.0 — 2026-08-03

### Repository

- Finalized the first complete RP_37 Reading Point sequence.
- Established RP_37 as a cumulative A/B/C engineering workflow.
- Tagged repository state as `rp-37-v1.0`.

### Reading Point Workflow

- Added source-derived engineering extraction.
- Generated cumulative RP_37_A, RP_37_B, and RP_37_C specifications.
- Standardized YAML generation from NB_00_SOURCE_EXTRACTION.
- Eliminated manual editing of generated Reading Point YAML.

### Engineering Dialogue

#### RP_37_A

Updated dialogue from abstract engineering concepts to measured detector performance.

```
140 cps · 150 eV · ~1.5 ms
        ↓
200 cps · <100 eV · 750 μs
```

#### RP_37_B

Updated dialogue from engineering concepts to detector refinements.

```
200 cps · <100 eV · 750 μs
        ↓
Lower Tc · Increase Si Coupling
```

#### RP_37_C

Updated dialogue from engineering concepts to engineering sessions.

```
Lower Tc · Increase Si Coupling
        ↓
Fabricate · Characterize · Validate
```

### Figure Refinements

- Shortened figure titles.
- Standardized supporting-context wording.
- Improved consistency across the A/B/C sequence.

### Source Extraction

NB_00_SOURCE_EXTRACTION now directly generates:

- RP_37_A.yaml
- RP_37_B.yaml
- RP_37_C.yaml

without an intermediate notebook.

### Status

RP_37 v1.0 frozen.

---

*Admissible generalizations trail leading specifications.*
