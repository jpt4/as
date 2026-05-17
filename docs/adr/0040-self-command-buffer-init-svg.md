# ADR-0040: Self Command Buffer Init SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0039 added a structured schematic-linked trace for one completed
self-target `proc-l-init` command buffer. The JSON trace is executable and
drift-checked, but it is not yet visible as a rendered schematic artifact.

The existing SVG renderer already has special summaries for self-mailbox
execution, unsupported mailbox preservation, automail reconfiguration, and
ordinary buffer accumulation. Completed command-buffer dispatch needs its own
summary path because it changes role like reconfiguration while the important
evidence is the decoded buffer, consumed command state, and cleared
control/buffer.

## Decision

Add a generated SVG for the self command-buffer init trace:

- export `SELF_COMMAND_BUFFER_INIT_SVG_ARTIFACT`;
- render command-buffer summary fields before generic reconfiguration and
  buffer summaries;
- add `schematics/self_command_buffer_init_trace.svg`;
- add tests proving parseability, metadata, port/layer annotations,
  command-buffer details, exact renderer-output matching, and drift rejection.

This SVG is a view of ADR-0039's JSON trace. It does not add new Universal Cell
semantics.

## Success Criteria

- Red tests fail before implementation because
  `SELF_COMMAND_BUFFER_INIT_SVG_ARTIFACT` is absent.
- The committed SVG exactly matches renderer output for
  `schematics/self_command_buffer_init_trace.json`.
- Existing schematic SVG tests still pass.
- The SVG exposes artifact ID, trace ID, ports, interpretive layers, transition
  status, command-buffer before/after state, cleared input, and recorded decode
  flow.
- Validation rejects a drifted SVG.

## Consequences

- P7 gains a visible render for the self-target command-buffer init dispatch
  trace.
- The renderer now distinguishes completed-buffer dispatch from generic
  role-changing reconfiguration.
- Neighbor routing, self-target non-init commands, larger GELC, and physical
  simulation remain out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_command_buffer_init_svg`
failed because `SELF_COMMAND_BUFFER_INIT_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`.

The green implementation added the SVG artifact path, a command-buffer-specific
summary branch in `render_schematic_svg`, and a checked-in SVG generated from
`schematics/self_command_buffer_init_trace.json`.

Final verification is recorded in `LOG.md`.
