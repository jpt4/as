# Self Command Buffer Init SVG

Status: seventh rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured self command-buffer init trace.
It is not a separate design source. The authoritative artifact remains
`schematics/self_command_buffer_init_trace.json`, and the checked-in SVG must
match `autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in
`schematics/self_command_buffer_init_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- stem role and `step_stem_cell` transition function;
- the `stem-command-buffer-self-processed` transition status;
- the active control rail `[0, 1, 0]`;
- command buffer before `[0, 0, 1, 0]` and buffer after `[]`;
- cleared input after dispatch;
- the recorded decode-flow text for `self/proc-l-init`;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not claim neighbor routing, self-target non-init execution,
dynamic GELC reconfiguration, or physical circulator verification. It renders
the one completed `self/proc-l-init` command-buffer trace from ADR-0039.

ADR-0074 registers this SVG in
`evidence/self_command_buffer_init_bundle.json`, so the render is validated as
part of the same claim/proof/trace evidence path.

## Verification

Run:

```sh
python -m unittest tests.test_self_command_buffer_init_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the command-buffer dispatch details are visible, and
verifies that the committed SVG exactly matches renderer output for the current
JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the renderer
is updated in the same ADR.
