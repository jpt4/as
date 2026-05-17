# ADR-0073: Self-Mailbox Unsupported Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0072 registered direct self-mailbox init execution as an integrated
evidence bundle. The sibling self-mailbox preservation boundary from ADR-0034
through ADR-0036 remains outside the evidence registry.

That boundary is important because it is the explicit reason AS does not
silently execute unresolved `write-buf-zero`, `write-buf-one`, or
`standard-signal` self-mailbox command tokens. It already has a named claim,
proof certificate, schematic trace, SVG render, and source-status boundary.

The registry should cover this negative frontier as a first-class evidence
bundle, not only the executable init-family path.

## Decision

Add `evidence/self_mailbox_unsupported_bundle.json` and register it in
`evidence/manifest.json`.

The bundle will point to:

- `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED`;
- the positive manifest example `write buffer one unsupported preserved`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_mailbox_unsupported_trace.json`;
- `schematics/self_mailbox_unsupported_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep self-mailbox non-init,
  `standard-signal`, write-buffer, and init-family boundaries explicit.

The checked-in unsupported self-mailbox trace and SVG will be aligned with the
named claim example so integrated validation proves one exact preservation
path.

This ADR does not add Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the unsupported bundle is
  absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes, validates against the PRC
  hardware witness map, and exactly matches the named claim example.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains five bundles and the CLI validates all five.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers both self-mailbox paths: supported
init-family execution and unsupported non-init preservation. This makes the
blocked command-token frontier inspectable as a positive artifact rather than
an absence of work.

## Test Plan

- Red: `python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle`
  fails before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle, registry entry,
  and trace/SVG alignment.
- Regression: run evidence registry/CLI tests, adjacent unsupported
  self-mailbox tests, and the full default suite before commit.

## After Action Report

Implemented in `evidence/self_mailbox_unsupported_bundle.json` and registered
in `evidence/manifest.json`.

The focused red run failed because
`evidence/self_mailbox_unsupported_bundle.json` was absent. The green
implementation adds the bundle for the positive
`write buffer one unsupported preserved` example under
`UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED`.

The integration exposed the same class of fixture drift as ADR-0072: the
existing unsupported self-mailbox trace and the claim example used different
incidental control/buffer values. The trace and generated SVG now match the
named preservation example exactly, so bundle validation proves one concrete
preservation path across claim, proof, trace, render, hardware witness map,
and source-status boundaries.

The evidence registry and CLI now validate five bundles: recipient init
execution, recipient single-token non-init rejection, recipient
simultaneous-token rejection, direct self-mailbox init execution, and direct
self-mailbox unsupported preservation.

Runtime behavior remains unchanged. AS still does not execute self-mailbox
non-init, recipient non-init, `standard-signal` command-token, or write-buffer
command-token semantics.
