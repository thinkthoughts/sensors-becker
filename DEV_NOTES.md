Engineering Artifact Naming (DEV NOTES)

> **Status note (added):** This document records an earlier repository
> architecture (the RO/ES/NB/SR/ER artifact-family plan below). The
> repository's current development chain — Reading Order → Engineering
> Statements → Reading Point Specifications → Notebook Compiler →
> Notebook Bundles — is described in `RO_A_READING_ORDER.md`, which
> reflects what the repository actually does today. This document is
> preserved as historical/provenance context, not as the live
> architecture. Where the two disagree, `RO_A_READING_ORDER.md` governs.

Purpose

Capture the current engineering artifact architecture while repository
development continues.

Artifact naming develops through continued engineering work. This
document remains intentionally flexible.

======================================================================
ENGINEERING ARTIFACT LIFECYCLE
======================================================================

Read

↓

Specify

↓

Develop

↓

Record

↓

Publish

======================================================================
ARTIFACT FAMILIES
======================================================================

RO  Reading Order

Purpose

Understand the repository.

Identity

Alphabetical reading sequence.

Examples

RO_A_READING_ORDER.md

RO_B_ENGINEERING_OBJECT_MAP.md

RO_C_ENGINEERING_PATHS.md

RO_D_REPOSITORY_CONTEXT.md

RO_E_ENGINEERING_SYSTEM_MAP.md

RO_F_MEASURED_ENGINEERING_STATES.md

RO_G_ENGINEERING_CONSTRAINTS.md

RO_H_ENGINEERING_REFINEMENTS.md

-----------------------------------------------------------------------

ES  Engineering Statements

Purpose

Specify reusable engineering intent.

Identity

Stable Engineering Statement identifiers.

Examples

ES_0000_ENGINEERING_STATEMENTS.md

ES_0001_SENSOR_DEVELOPMENT.yaml

ES_0002_ENGINEERING_OBJECT.yaml

ES_0003_ENGINEERING_PATHS.yaml

ES_0004_LEADING_SPECIFICATIONS.yaml

ES_0005_ENGINEERING_SESSION.yaml

...

-----------------------------------------------------------------------

NB  Engineering Notebooks

Purpose

Develop engineering through executable computational artifacts.

Identity

Notebook milestone

+

Engineering grammar stage

+

Engineering notebook title

Filename convention

NB_<number>_<letter>_<engineering_title>.ipynb

Foundation notebooks

NB_00_Z_ENGINEERING_CONTEXT.ipynb

NB_01_A_ENGINEERING_OBJECT.ipynb

NB_02_B_CONNECTED_LANES.ipynb

NB_03_C_ENGINEERING_VARIABLES.ipynb

NB_04_D_MEASURED_ENGINEERING_STATES.ipynb

Repository development notebooks

NB_07_E_ENGINEERING_SYSTEM.ipynb

NB_11_F_ENGINEERING_CONSTRAINTS.ipynb

NB_13_G_ENGINEERING_REFINEMENTS.ipynb

NB_17_H_ENGINEERING_SESSION.ipynb

NB_19_I_ENGINEERING_REPORT.ipynb

...

Engineering grammar stage identifies conceptual progression.

Notebook milestone identifies a stable engineering notebook.

-----------------------------------------------------------------------

SR  Session Reports

Purpose

Record engineering sessions.

Identity

Engineering session date.

Examples

SR_2026_07_INITIAL_ENGINEERING.md

SR_2026_07_DANIEL_BECKER_OUTREACH.md

SR_2026_08_SENSOR_REVIEW.md

...

-----------------------------------------------------------------------

ER  Engineering Reports

Purpose

Publish engineering outputs.

Identity

Stable engineering report identifiers.

Examples

ER_0001_SENSOR_DEVELOPMENT.md

ER_0002_ENGINEERING_SYSTEM.md

ER_0003_ENGINEERING_CONSTRAINTS.md

...

======================================================================
ARTIFACT RELATIONSHIPS
======================================================================

RO

↓

ES

↓

NB

↓

SR

↓

ER

Reading Order supports repository comprehension.

Engineering Statements specify engineering intent.

Engineering Notebooks develop engineering.

Session Reports record engineering development.

Engineering Reports communicate engineering outputs.

======================================================================
CURRENT OBSERVATIONS
======================================================================

Reading Order uses letters because readers follow a sequence.

Engineering Statements use stable identifiers because statements are
referenced independently.

Engineering Notebooks use both notebook milestones and engineering
grammar stages because they describe both engineering execution and
conceptual progression.

Session Reports use dates because engineering sessions occur through
time.

Engineering Reports use stable report identifiers because published
engineering outputs remain referenceable.

Additional artifact families may be specified through continued
repository engineering.

//

I used statement_text rather than a second statement key, since YAML would otherwise treat the later key as a replacement for the metadata block. This distinction should carry into the reusable ES schema:

statement:
  id:
  title:
  repository:
  status:

statement_text: >
  The actual engineering statement.

  //

  Dan Hawkley ChatGPT account (2026.07.25): Initial Sensors-Becker Scaffold
