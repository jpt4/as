# Multi-Command Recipient Rejection SVG

Status: implemented by ADR-0061 on 2026-05-17.

The rendered SVG lives in
`schematics/multi_command_recipient_rejection_trace.svg` and is generated from
`schematics/multi_command_recipient_rejection_trace.json`.

## Boundary

The SVG shows the ADR-0060 trace as a visible proof surface. It keeps the
simultaneous `wire-r-init` and `proc-l-init` input conflict visible, records
`rejected-input`, and shows role/memory preservation plus cleared
input/output and preserved upstream, self-mailbox, control, and buffer state.

This is not a runtime semantics expansion. AS still does not prioritize,
sequence, or execute multiple simultaneous recipient command-message tokens.
The next command-execution work should return to source resolution for
`standard-signal` and write-buffer command semantics.

## Validation

Run:

```sh
python -m unittest tests.test_multi_command_recipient_rejection_svg
```

The tests check parseability, trace metadata, port and layer annotations,
visible rejection details, exact renderer-output matching, validator
acceptance, and drift rejection.
