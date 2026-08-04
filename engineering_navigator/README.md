# Engineering Navigator

The Engineering Navigator organizes engineering work around **engineering
drivers** rather than files.

Instead of beginning with notebooks, figures, or source documents, the
Navigator begins with the engineering problems that guide detector
development. Each engineering driver connects engineering objectives,
Reading Points, engineering sessions, generated artifacts, and future
engineering questions into a single navigation page.

The Engineering Navigator is intended to evolve as engineering progresses.
Reading Points document engineering sessions. Engineering drivers organize
those sessions into a coherent engineering program.

---

# Engineering Workflow

```
Engineering Driver

↓

Engineering Questions

↓

Engineering Sessions

↓

Reading Points

↓

Generated Figures

↓

Engineering Reports

↓

Next Engineering Questions
```

Every engineering session contributes evidence toward one or more
engineering drivers.

---

# Engineering Drivers

## Detector Performance

Performance targets, detector response, and measurable engineering
improvements.

Status: Planned

---

## Absorber Manufacturing

Repeatable absorber fabrication supporting scalable detector production.

Status: Active

Directory:

```
absorber_manufacturing/
```

---

## Detector Module

Integration of detector components into validated detector modules.

Status: Planned

---

## Instrument Scaling

Engineering transition from detector modules toward instrument-scale
systems.

Status: Planned

---

## Commercial Evaluation

Evaluation of detector technology within practical engineering programs.

Status: Planned

---

## Product Assembly

Engineering requirements for manufacturing complete detector systems.

Status: Planned

---

## Data Analysis

Engineering support for detector characterization, calibration, and
performance evaluation.

Status: Planned

---

## Deployment

Engineering considerations for field deployment and operational systems.

Status: Planned

---

# Engineering Driver Structure

Each engineering driver follows the same structure.

```
Engineering Objective

↓

Current Status

↓

Engineering Dependencies

↓

Engineering Outcomes

↓

Reading Points

↓

Engineering Sessions

↓

Generated Figures

↓

Engineering Reports

↓

Current Engineering Questions
```

This structure allows engineering knowledge to evolve without changing the
overall organization of the repository.

---

# Repository Relationships

```
Engineering Navigator

↓

Engineering Driver

↓

Reading Point

↓

Notebook

↓

Generated Figures

↓

Engineering Session Report
```

Reading Points provide engineering evidence.

Engineering drivers provide engineering navigation.

---

# Current Engineering Drivers

| Driver | Reading Points |
|---------|----------------|
| Detector Performance | RP_37 |
| Absorber Manufacturing | RP_43 |
| Commercial Evaluation | RP_47 |

Additional engineering drivers will be added as the engineering program
expands.

---

# Design Principles

- Organize engineering by problems rather than files.
- Connect engineering decisions to supporting evidence.
- Preserve traceability from engineering questions to generated artifacts.
- Update engineering status without restructuring repository organization.
- Extend engineering knowledge through successive engineering sessions.

---

# Repository Goal

The Engineering Navigator serves as the primary engineering interface for
the Sensors-Becker repository.

Its purpose is to support engineering exploration, engineering refinement,
and engineering decision-making by organizing repository knowledge around
the leading engineering specifications that drive detector development.

---

*Admissible generalizations trail leading specifications.*
