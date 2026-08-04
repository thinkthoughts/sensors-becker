# Engineering Graph

`engineering_graph.yaml` is generated from every
`engineering_navigator/*/specification.yaml` file.

Generate it from the `sensors-becker` repository root:

```bash
python3 tools/build_engineering_graph.py
```

Verify that it is current:

```bash
python3 tools/build_engineering_graph.py --check
```

The graph contains:

- engineering-driver nodes;
- `supports`, `continues_to`, and `navigates_to` relationships;
- Reading Point, session, artifact, and figure indexes;
- unresolved references to planned drivers that do not yet have specifications.

Edit driver `specification.yaml` files, then regenerate the graph.
