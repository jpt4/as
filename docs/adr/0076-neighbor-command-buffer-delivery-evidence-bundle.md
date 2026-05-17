# ADR-0076: Neighbor Command-Buffer Delivery Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0044 implemented completed neighbor-target command-buffer delivery,
ADR-0045 promoted it into the named claim and proof-certificate surface,
ADR-0046 added the schematic-linked trace, and ADR-0047 added the rendered SVG
view.

The evidence registry now covers recipient command-message behavior, direct
self-mailbox behavior, and self-target command-buffer behavior. Neighbor
command-buffer delivery remains outside the integrated registry even though it
is the delivery surface that recipient-side command-message consumption builds
on.

Registering this path next makes the decoded-command evidence chain cover the
point where a stem cell completes `neighbor-b/proc-l-init`, places
`proc-l-init` on output channel 1, and stops before any recipient execution.

## Decision

Add `evidence/neighbor_command_buffer_delivery_bundle.json` and register it in
`evidence/manifest.json`.

The bundle will point to:

- `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED`;
- the positive manifest example `neighbor b proc left command delivered`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/neighbor_command_buffer_delivery_trace.json`;
- `schematics/neighbor_command_buffer_delivery_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep recipient consumption, recipient non-init,
  `standard-signal`, write-buffer, and init-family boundaries explicit.

This ADR does not add Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the neighbor delivery bundle is
  absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes, validates against the PRC
  hardware witness map, and exactly matches the named claim example.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains eight bundles and the CLI validates all
  eight.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry covers the neighbor-target decoded-command delivery
surface as an integrated path. Recipient-side init-family command-message
consumption remains a separate bundle, and recipient non-init,
`standard-signal` command-token, and write-buffer command-token semantics
remain source-blocked.

## Test Plan

- Red:
  `python -m unittest tests.test_neighbor_command_buffer_delivery_evidence_bundle`
  fails before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle and registry
  entry.
- Regression: run evidence registry/CLI tests, adjacent neighbor delivery and
  recipient boundary tests, and the full default suite before commit.

## After Action Report

Implemented in `evidence/neighbor_command_buffer_delivery_bundle.json` and
registered in `evidence/manifest.json`.

The focused red run failed because
`evidence/neighbor_command_buffer_delivery_bundle.json` was absent. The green
implementation adds the bundle for the positive
`neighbor b proc left command delivered` example under
`UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED`.

The neighbor delivery trace already matched the named claim example exactly,
so no trace or SVG regeneration was needed. Bundle validation now proves one
completed `neighbor-b/proc-l-init` command-buffer delivery across claim,
proof, trace, render, hardware witness map, recipient source-status, and
blocked-command source-status boundaries.

The evidence registry and CLI now validate eight bundles: recipient init
execution, recipient single-token non-init rejection, recipient
simultaneous-token rejection, direct self-mailbox init execution, direct
self-mailbox unsupported preservation, completed self-target command-buffer
init dispatch, completed self-target non-init command-buffer append
preservation, and completed neighbor-target command-buffer delivery.

Runtime behavior remains unchanged. AS still keeps recipient command-message
consumption, recipient non-init command messages, `standard-signal`
command-token execution, and write-buffer command-token execution behind their
separate source-status boundaries.

Verification passed:

- focused red:
  `python -m unittest tests.test_neighbor_command_buffer_delivery_evidence_bundle`
  failed before the bundle was added;
- focused green:
  `python -m unittest tests.test_neighbor_command_buffer_delivery_evidence_bundle`
  passed 5 tests;
- focused bundle/registry/CLI/source-status stack passed 35 tests;
- adjacent neighbor delivery and evidence stack passed 82 tests;
- actual CLI text and JSON modes passed for eight bundles;
- JSON parsing passed for the registry, new bundle, touched source status, and
  neighbor delivery trace;
- `py_compile` passed for the touched tests;
- `git diff --check` passed; and
- `python -m unittest discover` passed 450 tests.
