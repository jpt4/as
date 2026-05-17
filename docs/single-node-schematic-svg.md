# Single-Node Schematic SVG

Status: first rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured single-node schematic trace. It
is not a separate design source. The authoritative artifact remains
`schematics/single_node_triangular_rlem_trace.json`, and the checked-in SVG must
match `autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in
`schematics/single_node_triangular_rlem_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- the right-memory routing flow;
- the trace ID and transition function;
- the four interpretive layer IDs from ADR-0016.

The SVG does not claim physical circulator verification. The physical layer is
rendered only as a named interpretive boundary, preserving ADR-0015's rule that
circulator physics remains a candidate implementation hypothesis.

## Verification

Run:

```sh
python -m unittest tests.test_single_node_schematic_svg
```

The test parses the SVG as XML, checks its port and layer data attributes,
confirms the routed signal flow is visible, and verifies that the committed SVG
exactly matches renderer output for the current JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through
`render_single_node_schematic_svg()` and keep the test output green. Do not edit
the SVG by hand unless the renderer is updated in the same ADR.
