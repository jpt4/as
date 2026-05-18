# ADR-0170: Recipient Write-Buffer Command Evidence Bundle

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0169 implements recipient-side `write-buf-zero` and `write-buf-one`
command-message append execution and leaves the write-buffer source-status
record with a pending evidence-bundle promotion. Project status now reports
that write-buffer runtime behavior is implemented, but the transition
evidence registry still has no integrated bundle for the recipient
command-message surface.

The self-mailbox and self-target command-buffer write-buffer surfaces already
have evidence bundles. The recipient command-message surface should receive
the same runtime/claim/proof/trace/SVG/source-status bridge so the implemented
behavior is inspectable as a first-class transition evidence artifact.

## Decision

Add a recipient write-buffer command-message evidence bundle covering the
positive `fixed upstream write-buf-zero command appended` claim example and
the full positive-example set for
`UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED`.

The bundle will add:

- a schematic-linked trace for upstream recipient `write-buf-zero` append
  execution;
- a renderer-locked SVG for that trace;
- a registered transition evidence bundle;
- source-status updates marking the recipient write-buffer evidence-bundle
  promotion implemented; and
- project/source-status frontier updates so the remaining active safe-next
  slice is standard-signal source review.

## Success Criteria

- Red tests fail before implementation because the recipient write-buffer
  trace constant, trace file, SVG constant, SVG file, evidence bundle,
  registry entry, and source-status completion metadata are absent.
- The new trace replays through `step_fixed_cell`, matches the claim example,
  validates against the PRC hardware witness map, and rejects drift in append
  state or routed flow.
- The committed SVG is exactly renderer-derived and exposes the recipient
  write-buffer command-message state transition.
- The evidence bundle validates claim, proof certificate, trace, SVG, source
  status, and boundary layers, including both positive recipient write-buffer
  command-message examples as covered examples.
- The transition evidence registry accepts 11 bundles with no unregistered
  bundle files.
- Project/source status no longer advertises
  `add-recipient-write-buffer-command-message-evidence-bundle` as an active
  safe-next slice after that bundle lands.

## Test Plan

- Red: add focused trace, SVG, evidence-bundle, registry, and status tests
  before implementation.
- Green: add the trace/SVG constants and validator branch, commit the trace,
  generated SVG, bundle, registry entry, and source-status/doc updates.
- Regression: run focused ADR-0170 tests, evidence/project/source status
  CLIs, JSON parsing, `compileall`, `git diff --check`, and full unittest
  discovery.

## After Action Report

Implemented on 2026-05-18.

The red phase added trace, SVG, evidence-bundle, registry, and status tests
before implementation. The focused red run executed 149 tests and failed for
the expected reasons: the recipient write-buffer trace and SVG constants were
absent, the trace and bundle files did not exist, the registry still contained
10 transition bundles, and source-status records still advertised the pending
write-buffer evidence-bundle promotion.

The implementation added the recipient write-buffer schematic trace and
renderer-locked SVG, registered
`recipient-write-buffer-command-message-evidence-bundle`, added validator
support for the new trace artifact, and updated source/project status so the
completed write-buffer promotion no longer appears in the active safe-next
frontier. The new bundle covers both positive recipient write-buffer
command-message examples while tracing the upstream `write-buf-zero` case.

Verification passed after implementation: the focused ADR-0170/status suite
ran 183 tests, transition evidence accepted 11 bundles, chain evidence
accepted 2 bundles, project-status JSON accepted schema 15 with 16 transition
claims and 40 examples, source-status JSON accepted schema 2 with
`standard-signal` as the only blocked command and the only active safe-next
frontier, all JSON files parsed, `compileall` passed, `git diff --check`
passed, and full unittest discovery ran 763 tests successfully.
