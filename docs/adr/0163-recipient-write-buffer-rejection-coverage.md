# ADR-0163: Recipient Write-Buffer Rejection Coverage

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0161 implemented direct self-mailbox and completed self-target
command-buffer execution for `write-buf-zero` and `write-buf-one`. ADR-0162
then bundled those implemented self-target write-buffer surfaces as integrated
evidence.

Delivered recipient write-buffer command messages remain outside that
execution surface. They are intentionally rejected by the existing recipient
non-init command-message boundary. The predicate tests already exercise direct
write-buffer rejection behavior, and the neighbor-delivery rejection chain
already demonstrates an upstream `write-buf-one` handoff. The machine-readable
base claim, proof certificate, and recipient non-init evidence bundle still
only name the upstream `standard-signal` rejection as covered by the primary
bundle.

## Decision

Keep recipient write-buffer command-message execution blocked. Extend the
existing `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` claim and proof
certificate with explicit positive examples for upstream `write-buf-zero` and
`write-buf-one` rejection.

Update the existing recipient non-init evidence bundle so its
`covered_positive_examples` field names the standard-signal primary example and
both write-buffer rejection examples. This ADR does not add a new trace or SVG:
the bundle's primary trace remains the existing upstream `standard-signal`
rejection trace, while the covered examples make the claim/proof boundary
explicit for both delivered write-buffer command tokens.

## Success Criteria

- Red tests fail before implementation because the write-buffer rejection
  examples are absent from the claim, proof certificate, and bundle coverage.
- The claim manifest contains positive upstream `write-buf-zero` and
  `write-buf-one` recipient rejection examples that evaluate true.
- The proof certificate covers both new positive examples.
- The recipient non-init evidence bundle lists the standard-signal primary
  example plus both write-buffer examples as covered positive examples.
- Project status and evidence registry JSON expose the widened coverage.
- Runtime behavior and trace/SVG artifacts remain unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_recipient_non_init_command_rejection_claim tests.test_recipient_non_init_evidence_bundle tests.test_evidence_bundle_registry tests.test_project_status_report`
  fails before the claim/proof/bundle coverage is added.
- Green: the same focused suite passes after updating the artifacts.
- Regression: run the evidence registry CLI, project-status JSON,
  source-status JSON, JSON parsing for touched files, `compileall`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The focused red run failed before implementation because the upstream
`write-buf-zero` and `write-buf-one` rejection examples were absent from the
recipient non-init claim manifest, absent from the proof certificate, and
absent from recipient non-init evidence-bundle coverage.

The implementation adds those two positive examples to
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`, adds matching
`manifest-example` proof-certificate steps, and expands
`evidence/recipient_non_init_command_rejection_bundle.json` so the primary
upstream `standard-signal` trace also covers both upstream write-buffer
rejection examples at the claim/proof layer.

Runtime behavior, schematic traces, SVG artifacts, project-status schema `15`,
and source-status frontier schema `2` are unchanged. Project status now
reports 15 transition claims with 39 matched examples.

Verification passed:

- focused red suite failed before implementation as expected;
- focused green suite passed 107 tests;
- adjacent recipient/write-buffer/source-status focused suite passed 138
  tests;
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json`
  accepted 10 transition evidence bundles;
- evidence registry JSON, project-status JSON, and source-status JSON commands
  accepted the current artifacts;
- JSON parsing passed for the touched JSON artifacts;
- `python -m compileall -q autarkic_systems tests` passed;
- `git diff --check` passed; and
- `python -m unittest discover` ran 730 tests.
