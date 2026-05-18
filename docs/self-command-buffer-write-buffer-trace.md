# Self Command-Buffer Write-Buffer Trace

ADR-0162 adds
`schematics/self_command_buffer_write_buffer_trace.json`, a schematic-linked
trace for completed self-target command-buffer write-buffer execution.

The trace records a stem cell whose input `[0, 1, 0]` matches control
`[0, 1, 0]`, completing buffer `00111`. The command decoder reads value `7`
as `self/write-buf-one`. Replaying the trace through `step_stem_cell` clears
the command-buffer source, preserves the control rail, resets the buffer to
the literal append bit `[1]`, and returns
`stem-command-buffer-self-write-buffer-appended`.

The trace is aligned to the positive transition-claim example
`self command buffer write buffer one appended` under
`UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED`.
