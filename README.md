# Sensors Becker

Reproducible engineering specifications for cryogenic sensor development.

This repository develops an engineering navigator around public work by Daniel Becker and collaborators, with an emphasis on transition-edge sensors (TESs), absorber fabrication, microwave SQUID multiplexing, and SMuRF readout.

The central workflow is:

```text
technical source
    ↓
structured evidence
    ↓
engineering object
    ↓
specified constraints
    ↓
admissible engineering states
    ↓
checkable next questions
```

The repository also tests where the **General Divisor Theorem (GDT)** can legitimately specify discrete admissible engineering states.

The theorem is treated as a mathematical specification, not as an analogy: where its hypotheses are not supplied by the engineering evidence, the repository records that boundary rather than manufacturing an application.

## General Divisor Theorem

For an integer state subject to a residue condition

$$
n \equiv a \pmod{m}
$$

together with a coprimality condition

$$
\gcd(n,N)=1,
$$

define

$$
d=\operatorname{rad}(\gcd(m,N)),
\qquad
R=\frac{\operatorname{rad}(N)}{d}.
$$

The GDT gives an exact admissibility dichotomy and, in the admissible case, an exact period, count per period, density, and correction factor.

The mathematical source and Lean verification are maintained separately:

- Mathematical basis: https://goodmath.app/
- Paper: https://goodmath.app/divisor.pdf
- Lean formalization: https://github.com/thinkthoughts/general-divisor-theorem

`sensors-becker` asks a narrower engineering question:

> Where do real sensor-design constraints supply the mathematical objects required for a direct GDT application?

A discrete index by itself is not enough. A direct application requires physically justified meanings for the integer state, modulus, residue rule, and factor-exclusion rule.

## Current Engineering Domains

### Absorber Manufacturing

The absorber-manufacturing branch structures evidence concerning:

- bismuth electroplating
- deposition conditions
- absorber microstructure
- thermal conductivity
- thermalization
- spectral response
- process-to-response relationships

Reported process points are preserved as source evidence rather than promoted automatically into recommended fabrication specifications.

The resulting engineering objects can therefore distinguish:

```text
reported process point
        ≠
validated process window
        ≠
engineering specification
```

### Multiplexed Readout

The multiplexed-readout branch follows the same workflow for microwave SQUID multiplexing and SMuRF/PySMuRF readout.

The current evidence includes both published readout architecture and implementation-facing channel-assignment rules.

SOURCE_05 supplies discrete structures including resonator groups, digital analysis sub-bands, harmonic indices, channel states, frequency windows, and physical readout exclusions.

SOURCE_06 follows the PySMuRF assignment layer, where resonator frequencies are mapped to integer subband and channel indices and close resonator pairs are excluded by a frequency-separation rule.

This produces real admissible engineering states such as:

- assigned readout channels
- frequency-separated resonator pairs
- in-band resonators
- tracking-qualified channels

## Current GDT Result

The readout system contains genuine discrete engineering structure.

That alone does not establish a GDT application.

The current SOURCE_05 + SOURCE_06 audit tests candidate mappings involving:

- analysis subband index
- channel number within a subband
- resonator grouping
- tracked harmonic order

None currently supplies both

$$
n \equiv a \pmod{m}
$$

as a physically specified residue-class rule and

$$
\gcd(n,N)=1
$$

as a physically specified factor-exclusion rule.

Therefore:

```text
discrete engineering states
        ✓

specified admissibility constraints
        ✓

direct GDT application
        not yet established
```

This negative result is intentional.

The navigator preserves the actual frequency-distance, band-window, assignment, and tracking constraints instead of replacing them with an unsupported arithmetic encoding.

## Why This Matters

The objective is not to attach a mathematical theorem to every engineering problem.

It is to make the path from evidence to engineering decisions explicit:

```text
leading constraints
        ↓
engineering objects
        ↓
measurable states
        ↓
admissible states
        ↓
candidate specifications
        ↓
validation
```

Where a theorem applies, its hypotheses should be identifiable in the engineering system.

Where those hypotheses are absent, that should also be identifiable.

This makes theorem applicability itself a reproducible engineering result.

## Evidence Pipeline

Source records begin as scaffolds and are completed by reusable, source-specific extractors.

```text
source document / software documentation
        ↓
SOURCE scaffold
        ↓
registered extractor
        ↓
canonical source YAML
        ↓
validation
        ↓
Engineering Object
```

Current evidence records extend through `SOURCE_06`.

The repository includes evidence from both conventional technical literature and implementation-facing software documentation.

## Engineering Objects

Engineering Objects collect source-supported relationships around a specific engineering subsystem.

Current examples include absorber-manufacturing objects and:

```text
engineering_navigator/
    engineering_objects/
        multiplexed_readout.yaml
```

Engineering Objects are generated from canonical source records and validated before use by downstream notebooks.

They provide a layer between individual papers or software documentation and higher-level engineering claims.

## Notebook Sequence

The current notebook workflow includes:

```text
source extraction
        ↓
absorber-manufacturing synthesis
        ↓
candidate process window
        ↓
process-to-response validation plan
        ↓
GDT applicability audit
        ↓
multiplexed-readout source extraction
        ↓
SMuRF / PySMuRF GDT applicability audit
```

Recent notebooks include:

- SOURCE_05 SMuRF extraction
- `NB_06_GDT_MULTIPLEXED_READOUT`
- `NB_07_SOURCE_06_EXTRACTION`
- `NB_08_GDT_SMURF_CHANNEL_ASSIGNMENT`

NB_08 combines published SMuRF evidence with PySMuRF implementation evidence and produces machine-readable records of both admissible engineering states and missing GDT hypotheses.

## Repository Structure

The active engineering pipeline is organized primarily under:

```text
engineering_navigator/
    absorber_manufacturing/
        source_records/

    multiplexed_readout/
        source_records/
        gdt_audit/

    engineering_objects/

tools/
    source_extractors/
    engineering_objects/

notebooks/
```

Additional Reading Point, report, and visualization infrastructure remains in the repository as supporting material.

## Next Questions

For multiplexed readout, the next useful evidence is lower-level documentation where it specifies exact:

- firmware index-allocation rules
- resonator frequency-plan rules
- mask-layout rules
- clocking and synchronization constraints
- aliasing exclusions

The specific mathematical question is whether any such rule naturally specifies both a repeating residue-class condition and a factor-based exclusion.

If it does, that provides a candidate direct GDT engineering application.

If it does not, the resulting exclusion is itself useful specification.

## Repository Goal

Develop reproducible engineering objects that connect technical evidence, physical constraints, admissible states, mathematical specifications, and validation without introducing unsupported precision or unsupported theorem applications.

---

**Admissible generalizations trail leading specifications.**
