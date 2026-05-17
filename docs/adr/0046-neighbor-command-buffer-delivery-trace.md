# ADR-0046: Neighbor Command Buffer Delivery Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0044 implements neighbor-target command-buffer delivery, and ADR-0045
promotes that delivery behavior into the named claim surface. The next evidence
layer should make one delivery path visible as a schematic-linked executable
trace before rendering it as SVG.

The trace should remain delivery-only. It must show a decoded command token
leaving on the correct output channel, but it must not imply recipient-side
command-message consumption.

## Decision

Add a schematic-linked trace for one neighbor command-buffer delivery:

- add `schematics/neighbor_command_buffer_delivery_trace.json`;
- add a schematic trace artifact id for neighbor command-buffer delivery;
- validate neighbor delivery separately from self init dispatch, unsupported
  append-boundary traces, and ordinary stem buffer accumulation;
- add tests for artifact identity, schema vocabulary, recorded decode flow,
  execution replay, witness-map validation, and drift rejection.

The trace will use the five-bit buffer `10101`, decoded as
`neighbor-b/proc-l-init`, because it exercises the middle output channel and a
non-stem init-family command token without executing that token on a neighbor.

## Success Criteria

- Red tests fail before implementation because the neighbor delivery trace
  artifact id is absent.
- The trace maps every current `Cell` field.
- Replaying the trace through `step_stem_cell` reaches
  `stem-command-buffer-neighbor-delivered`.
- The recorded after-cell matches current execution exactly.
- Validation rejects wrong output channels, uncleared command state, or drifted
  decode flow.

## Consequences

- P7 gains executable schematic-linked evidence for ADR-0044/ADR-0045 neighbor
  command-buffer delivery.
- Recipient-side command-message consumption, rendered SVG output, self-target
  non-init execution, larger GELC examples, and physical simulation remain out
  of scope.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_neighbor_command_buffer_delivery_trace` failed
because `NEIGHBOR_COMMAND_BUFFER_DELIVERY_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`.

The green implementation added the neighbor delivery trace artifact, registered
the artifact id, and routed that artifact through a dedicated completed
neighbor command-buffer delivery alignment check instead of the ordinary
stem-buffer accumulation path.

Final verification is recorded in `LOG.md`.
