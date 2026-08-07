# Engineering Objects

Engineering Objects are repository-wide knowledge objects assembled from source-record evidence.

They are not source summaries. A source record says what one source contributes; an Engineering Object says what the repository currently knows about a stable engineering object or process.

Initial objects:

```text
absorber.yaml
electroplating.yaml
tes.yaml
membrane.yaml
detector_module.yaml
```

## Intended flow

```text
Source Records
    ↓
Engineering Objects
    ↓
Engineering Concepts
    ↓
Synthesis
    ↓
Engineering Specifications
    ↓
Quantitative Notebooks
```

Each object records:

- objective
- contributing source records
- variables
- current evidence
- candidate specifications
- open specifications
- relationships to other engineering objects

These v1 files are hand-initialized from the current SOURCE_00, SOURCE_01, and SOURCE_02 evidence. The next repository feature should be an `object_builder.py` that assembles or refreshes them from source records and synthesis outputs.
