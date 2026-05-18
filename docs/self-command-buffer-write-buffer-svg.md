# Self Command-Buffer Write-Buffer SVG

ADR-0162 adds
`schematics/self_command_buffer_write_buffer_trace.svg`, generated from
`schematics/self_command_buffer_write_buffer_trace.json` by
`autarkic_systems.schematic_svg.render_schematic_svg`.

The committed SVG is renderer-locked: validation rejects drift between the
structured trace and the visible artifact. It shows the completed
`self/write-buf-one` decode, preserved control rail, cleared input source, and
buffer reset to `[1]`.
