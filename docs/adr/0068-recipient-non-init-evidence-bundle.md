# ADR-0068: Recipient Non-Init Rejection Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0065 through ADR-0067 made one recipient init transition inspectable through
an evidence bundle, registry, and CLI. The adjacent recipient non-init rejection
boundary already has the same ingredients:

- a named claim and proof certificate;
- a schematic trace;
- a checked SVG render; and
- source-status records keeping `standard-signal`, write-buffer, and
  multi-command behavior constrained.

The registry should not remain a one-entry happy path. Adding the rejection
boundary as a second bundle proves the registry can track both an executable
init transition and a blocked-command rejection boundary.

## Decision

Add `evidence/recipient_non_init_command_rejection_bundle.json` and register it
in `evidence/manifest.json`.

The bundle will point to:

- `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`;
- the positive manifest example `fixed upstream standard-signal command
  rejected`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/recipient_non_init_command_rejection_trace.json`;
- `schematics/recipient_non_init_command_rejection_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep the rejected command boundary explicit.

This ADR does not add `standard-signal` or write-buffer command execution.

## Success Criteria

- Red tests fail before implementation because the non-init rejection bundle is
  absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes and validates against the PRC
  hardware witness map.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains both recipient init and recipient non-init
  rejection bundles and the CLI validates both.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers both sides of the recipient command-message
frontier: a source-backed init-family transition and an explicit non-init
rejection boundary.

## Test Plan

- Red: `python -m unittest tests.test_recipient_non_init_evidence_bundle`
  fails before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle and registry
  entry.
- Regression: run evidence registry/CLI tests, adjacent recipient rejection
  tests, and the full default suite before commit.

## After Action Report

Implemented in `evidence/recipient_non_init_command_rejection_bundle.json` and
registered in `evidence/manifest.json`.

The focused red run failed because
`evidence/recipient_non_init_command_rejection_bundle.json` was absent. The
green implementation adds the bundle for the positive `fixed upstream
standard-signal command rejected` example under
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`.

The same cross-layer bundle validator now checks both the ADR-0065 recipient
init transition and this recipient non-init rejection boundary. The registry
CLI reports two accepted bundles.

Runtime behavior remains unchanged. `standard-signal`, write-buffer, and
multi-command recipient semantics remain blocked or rejected according to the
existing source-status records.
