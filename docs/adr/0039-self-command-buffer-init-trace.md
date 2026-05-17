# ADR-0039: Self Command Buffer Init Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0037 added a narrow self-target init command-buffer dispatch path, and
ADR-0038 promoted that path into the named transition-claim and
proof-certificate surface.

The schematic evidence layer should now expose the same behavior as a
structured trace. Without that trace, the command-buffer behavior is executable
and claim-backed, but not yet visible in the P7 hardware/schematic witness
sequence that has carried prior Universal Cell slices.

## Decision

Add a schematic-linked trace for one completed self-target init command buffer:

- add `schematics/self_command_buffer_init_trace.json`;
- add a schematic trace artifact id for the command-buffer self-init slice;
- validate completed-buffer decoding separately from ordinary buffer
  accumulation and direct self-mailbox execution;
- add tests for artifact identity, schema vocabulary, recorded command-buffer
  flow, execution replay, witness-map validation, and drift rejection.

The trace will use the five-bit buffer `00101`, decoded as self-target
`proc-l-init`, because that command changes both role and memory while also
proving that the command buffer and control state are cleared after dispatch.

## Success Criteria

- Red tests fail before implementation because the command-buffer trace
  artifact id is absent.
- The trace maps every current `Cell` field.
- Replaying the trace through `step_stem_cell` reaches
  `stem-command-buffer-self-processed`.
- The recorded after-cell matches current execution exactly.
- Validation rejects wrong target role/memory, uncleared control/buffer state,
  or drifted command-buffer flow.

## Consequences

- P7 gains visible, executable evidence for the ADR-0037/ADR-0038 slice.
- The trace still does not claim neighbor routing, self-target non-init
  commands, larger GELC examples, or physical simulation.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_command_buffer_init_trace`
failed because `SELF_COMMAND_BUFFER_INIT_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`.

The green implementation added the command-buffer init trace artifact,
registered the artifact id, and routed
`stem-command-buffer-self-processed` traces through a dedicated completed
command-buffer alignment check instead of the ordinary stem-buffer
accumulation check.

Final verification is recorded in `LOG.md`.
