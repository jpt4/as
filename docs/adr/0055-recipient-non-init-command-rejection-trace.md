# ADR-0055: Recipient Non-Init Command Rejection Trace

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0053 concluded that recipient-side non-init command-message execution is
not justified by the current source reconciliation. ADR-0054 promoted the safe
boundary into the named
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` transition claim and proof
certificate.

The next useful artifact is a schematic-linked executable trace that makes one
rejection case visible at the same layer as the existing recipient init trace.
The trace must not imply execution of `standard-signal`, `write-buf-zero`,
`write-buf-one`, or multi-command recipient inputs. It should instead record
the current AS fail-closed behavior: the recipient rejects the non-init command
message, clears the command source, preserves role and memory, and emits no
output.

## Decision

Add a recipient non-init command-message rejection schematic trace covering a
fixed recipient cell that pulls `standard-signal` from upstream channel 1.

The trace will:

- use artifact id
  `recipient-non-init-command-rejection-schematic-and-uc-transition-trace`;
- execute through `step_fixed_cell`;
- record `rejected-input` status;
- preserve role and memory;
- clear the upstream command source, input, and output channels;
- preserve automail, self-mailbox, control, and buffer state;
- validate against the PRC witness map and the ADR-0054 rejection predicate.

## Consequences

The project gains a concrete schematic-linked rejection artifact for the
non-init recipient frontier without taking on unresolved PRC execution
semantics. This also creates the correct source of truth for a later rendered
SVG slice.

The trace is intentionally one upstream `standard-signal` example. Direct
write-buffer rejection and stem multi-command conflict rejection remain covered
by ADR-0054 claim examples rather than by separate schematic artifacts in this
slice.

## Test Plan

- Red: `python -m unittest tests.test_recipient_non_init_command_rejection_trace`
  fails because the artifact identity and trace do not exist.
- Green: the same focused test passes after adding the artifact and validator
  alignment.
- Regression: run the adjacent recipient command-source tests and the full
  default suite before commit.

## After Action Report

Implemented in `autarkic_systems/schematic_trace.py`,
`schematics/recipient_non_init_command_rejection_trace.json`, and
`docs/recipient-non-init-command-rejection-trace.md`.

The focused red run failed because
`RECIPIENT_NON_INIT_COMMAND_REJECTION_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`. The green run passed
`tests.test_recipient_non_init_command_rejection_trace`, including execution
replay, ADR-0054 predicate coverage, witness validation, and drift rejection.
