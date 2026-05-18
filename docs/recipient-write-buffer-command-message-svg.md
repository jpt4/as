# Recipient Write-Buffer Command-Message SVG

Status: renderer-locked SVG, added 2026-05-18.

ADR-0170 adds
`schematics/recipient_write_buffer_command_message_trace.svg`, rendered from
`schematics/recipient_write_buffer_command_message_trace.json` by
`autarkic_systems.schematic_svg.render_schematic_svg`.

The SVG records the same upstream `write-buf-zero` recipient append trace as
the JSON artifact, including before/after upstream, input, output, control,
and buffer state. The committed file must match the renderer output exactly.

## Boundary

The SVG is a visual rendering of the checked trace, not an independent
semantic authority. Renderer drift, missing metadata, or changed cell-state
text is rejected by tests.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_write_buffer_command_message_svg
```

The tests check SVG metadata, visible transition text, exact renderer parity,
and drift rejection.
