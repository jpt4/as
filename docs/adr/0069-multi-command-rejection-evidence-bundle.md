# ADR-0069: Multi-Command Rejection Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0068 added the recipient non-init `standard-signal` rejection as the second
evidence bundle. The remaining visible recipient rejection ladder from
ADR-0059 through ADR-0061 covers a different boundary: two simultaneous
command-message tokens are rejected rather than prioritized or sequenced.

That multi-command rejection has an existing claim example, proof certificate,
schematic trace, SVG render, and source-status artifact. It should enter the
evidence registry as a third bundle so the registry covers:

- executable init-family recipient command-message consumption;
- single non-init command-message rejection; and
- simultaneous command-message rejection.

## Decision

Add `evidence/multi_command_recipient_rejection_bundle.json` and register it in
`evidence/manifest.json`.

The bundle will point to:

- `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`;
- the positive manifest example `fixed all-init command conflict rejected`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/multi_command_recipient_rejection_trace.json`;
- `schematics/multi_command_recipient_rejection_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep multi-command, non-init,
  `standard-signal`, and write-buffer boundaries explicit.

This ADR does not add command prioritization, sequencing, or new runtime
execution behavior.

## Success Criteria

- Red tests fail before implementation because the multi-command bundle is
  absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes and validates against the PRC
  hardware witness map.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains three bundles and the CLI validates all three.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers the active recipient command-message frontier
as three inspectable bundles: init-family execution, single-token non-init
rejection, and simultaneous-token rejection.

## Test Plan

- Red: `python -m unittest tests.test_multi_command_evidence_bundle` fails
  before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle and registry
  entry.
- Regression: run evidence registry/CLI tests, adjacent multi-command tests,
  and the full default suite before commit.

## After Action Report

Implemented in `evidence/multi_command_recipient_rejection_bundle.json` and
registered in `evidence/manifest.json`.

The focused red run failed because
`evidence/multi_command_recipient_rejection_bundle.json` was absent. The green
implementation adds the bundle for the positive `fixed all-init command
conflict rejected` example under
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`.

The evidence registry and CLI now validate three bundles: recipient init
execution, recipient single-token non-init rejection, and recipient
simultaneous-token rejection.

Runtime behavior remains unchanged. AS still rejects multiple simultaneous
recipient command-message tokens and does not infer priority or sequencing.
