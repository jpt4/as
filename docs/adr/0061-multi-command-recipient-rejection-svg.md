# ADR-0061: Multi-Command Recipient Rejection SVG

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0060 added a structured schematic trace for ADR-0059's
reject-and-clear policy over multiple simultaneous recipient command-message
inputs. The trace is executable and validates through the existing recipient
non-init rejection alignment checker, but the project convention is to follow a
stable schematic trace with a checked SVG view generated exactly from the JSON
trace.

This case is easy to misread as a missing transition because the rejection
preserves role, memory, output, self-mailbox, control, and buffer state. The
SVG must therefore make the simultaneous `wire-r-init` and `proc-l-init` input
conflict visible and show the cleared input/output boundary.

## Decision

Add a rendered SVG view for
`schematics/multi_command_recipient_rejection_trace.json`.

The renderer will expose:

- the direct `wire-r-init` plus `proc-l-init` command-message conflict;
- the `rejected-input` transition through `step_fixed_cell`;
- preserved recipient role and memory;
- cleared input and output channels;
- preserved upstream, self-mailbox, control, and buffer state;
- the trace's routed signal flow.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `MULTI_COMMAND_RECIPIENT_REJECTION_SVG_ARTIFACT` is absent from
  `autarkic_systems.schematic_svg`.
- The SVG is nonblank parseable XML with trace metadata.
- The SVG exposes trace ports and interpretive layer IDs.
- The visible text records the multi-command conflict and rejection details.
- The checked SVG exactly matches `render_schematic_svg()`.
- The SVG validator accepts the committed artifact and rejects drift.
- Source-status frontiers move beyond the multi-command SVG slice without
  widening command execution.

## Consequences

The multi-command recipient input policy becomes visible in the schematic
evidence layer. After this slice, AS should return to source-resolution work
for `standard-signal` and write-buffer command execution rather than adding
more rejection surface area.

## Test Plan

- Red: `python -m unittest tests.test_multi_command_recipient_rejection_svg`
  fails because the SVG artifact path is absent from
  `autarkic_systems.schematic_svg`.
- Green: the same focused test passes after adding the renderer route and
  checked SVG artifact.
- Regression: run adjacent multi-command/source-status tests and the full
  default suite before commit.

## After Action Report

Implemented in `autarkic_systems/schematic_svg.py`,
`schematics/multi_command_recipient_rejection_trace.svg`, and
`docs/multi-command-recipient-rejection-svg.md`.

The focused red run failed because
`MULTI_COMMAND_RECIPIENT_REJECTION_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`. After adding the artifact path and routing
the multi-command artifact through the existing recipient non-init rejection
summary branch, the test failed only because the checked SVG artifact was
missing. Generating the SVG from `render_schematic_svg()` made the focused SVG
suite pass.

Source-status frontiers now point away from the completed multi-command SVG
slice and back toward source resolution for `standard-signal` or write-buffer
command semantics.
