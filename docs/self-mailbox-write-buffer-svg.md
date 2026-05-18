# Self-Mailbox Write-Buffer SVG

ADR-0162 adds
`schematics/self_mailbox_write_buffer_trace.svg`, generated from
`schematics/self_mailbox_write_buffer_trace.json` by
`autarkic_systems.schematic_svg.render_schematic_svg`.

The committed SVG is renderer-locked: validation rejects drift between the
structured trace and the visible artifact. It shows the direct
`write-buf-one` self-mailbox source, the preserved control rail, and the buffer
change from `[0]` to `[0, 1]`.
