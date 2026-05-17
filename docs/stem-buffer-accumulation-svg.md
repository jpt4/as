# Stem Buffer Accumulation SVG

Status: fourth rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured stem buffer accumulation trace.
It is not a separate design source. The authoritative artifact remains
`schematics/stem_buffer_accumulation_trace.json`, and the checked-in SVG must
match `autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in
`schematics/stem_buffer_accumulation_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- stem role and `step_stem_cell` transition function;
- the active control rail `[0, 1, 0]`;
- buffer before `[0]` and buffer after `[0, 1]`;
- cleared input after the append;
- the recorded buffer-flow text;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not claim full command decoding, target routing, dynamic GELC
reconfiguration, or physical circulator verification. It renders the one
matching-input append trace from ADR-0024.

## Verification

Run:

```sh
python -m unittest tests.test_stem_buffer_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the stem buffer accumulation details are visible, and
verifies that the committed SVG exactly matches renderer output for the current
JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the renderer
is updated in the same ADR.
