# Self-Mailbox Write-Buffer Trace

ADR-0162 adds
`schematics/self_mailbox_write_buffer_trace.json`, a schematic-linked trace for
the direct `self_mailbox` `write-buf-one` execution path introduced by
ADR-0161.

The trace records a stem cell with left memory, control rail `[1, 0, 0]`,
buffer `[0]`, and `self_mailbox: write-buf-one`. Replaying the trace through
`step_stem_cell` appends literal `1`, clears `self_mailbox`, preserves the
control rail, and returns `self-mailbox-write-buffer-appended`.

The trace is aligned to the positive transition-claim example
`self mailbox write buffer one appended` under
`UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED`.
