# Processor Memory Toggle SVG

Status: second rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured processor memory-toggle trace.
It is not a separate design source. The authoritative artifact remains
`schematics/processor_memory_toggle_trace.json`, and the checked-in SVG must
match `autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in
`schematics/processor_memory_toggle_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- processor role and left-memory routing;
- before memory `left` and after memory `right`;
- the trace ID and `step_fixed_cell` transition function;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not introduce new processor semantics. It renders the executable
trace from ADR-0018 and remains subordinate to the JSON artifact.

## Verification

Run:

```sh
python -m unittest tests.test_processor_memory_toggle_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the processor memory-toggle details and routed signal flow
are visible, and verifies that the committed SVG exactly matches renderer
output for the current JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the renderer
is updated in the same ADR.
