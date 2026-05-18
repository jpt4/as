# Recipient Write-Buffer Command-Message Trace

Status: schematic-linked transition trace, added 2026-05-18.

ADR-0170 adds
`schematics/recipient_write_buffer_command_message_trace.json`, an AS-owned
single-node trace for the ADR-0169 recipient write-buffer command-message
surface.

The trace uses the positive
`UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED` example named
`fixed upstream write-buf-zero command appended`: a wire/right recipient pulls
an upstream `write-buf-zero` token, appends literal `0` to an existing
one-bit buffer, clears the upstream command source, and preserves role,
memory, output, automail, self-mailbox, and control state.

## Boundary

This trace covers a single non-full recipient write-buffer command-message
append. It does not cover init-family recipient consumption, standard-signal
rejection, multi-command conflict rejection, or the full-buffer boundary; those
remain covered by their existing traces, claims, and runtime tests.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_write_buffer_command_message_trace
```

The tests load the trace, replay it through `step_fixed_cell`, validate it
against the PRC hardware witness map, and reject drifted append state or
routed-flow text.
