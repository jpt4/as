# ADR-0032: Self Mailbox Init Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0030 added source-stable self-mailbox init-command execution, and ADR-0031
promoted that behavior into the named claim and proof-certificate surface.

The P7 schematic path should now expose the same behavior as a structured
trace. Without that trace, the behavior is executable and claim-backed but not
yet visible in the schematic evidence layer that has carried prior Universal
Cell slices.

## Decision

Add a schematic-linked trace for one self-mailbox init command:

- add `schematics/self_mailbox_init_trace.json`;
- add a schematic trace artifact id for self-mailbox init execution;
- validate self-mailbox init flow separately from automail reconfiguration and
  standard-signal buffer accumulation;
- add tests for artifact identity, schema vocabulary, recorded mailbox flow,
  execution replay, witness-map validation, and drift rejection.

The trace will use `proc-l-init` because it changes both role and memory while
also proving that control and buffer state are cleared by the mailbox command.

## Success Criteria

- Red tests fail before implementation because the self-mailbox trace artifact
  id is absent.
- The trace maps every current `Cell` field.
- Replaying the trace through `step_stem_cell` reaches
  `self-mailbox-processed`.
- The recorded after-cell matches current execution exactly.
- Validation rejects wrong target role/memory, uncleared mailbox state, or
  drifted mailbox flow.

## Consequences

- P7 gains visible, executable evidence for the ADR-0030/ADR-0031 slice.
- The trace still does not claim write-buffer, `standard-signal`, neighbor
  delivery, or full command-buffer execution.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_mailbox_init_trace` failed
because `SELF_MAILBOX_INIT_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`.

The green implementation added the self-mailbox init trace artifact, registered
the artifact id, and routed stem traces with empty automail and non-empty
`self_mailbox` through a dedicated self-mailbox init alignment check.

Final verification is recorded in `LOG.md`.
