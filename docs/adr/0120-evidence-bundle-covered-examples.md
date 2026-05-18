# ADR-0120: Evidence Bundle Covered Examples

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0119 expanded the self-mailbox unsupported and self-target command-buffer
unsupported claim/proof surfaces so each blocked self-command token has an
explicit positive manifest example. The integrated evidence bundles for those
boundaries still name only one `positive_example`.

That single example remains useful because each bundle also points at one
schematic trace and one rendered SVG. But after ADR-0119, the bundle layer
should also be able to name the broader positive manifest coverage it depends
on. Otherwise the project can truthfully say the claim/proof surface is
complete while the integrated evidence bundle still looks representative-only.

## Decision

Add optional `covered_positive_examples` support to transition evidence
bundles. The existing `positive_example` remains the primary trace-aligned
example, while `covered_positive_examples` names every positive manifest
example the bundle depends on for boundary coverage.

The evidence bundle validator will require every covered example to:

- exist in the named claim;
- be a positive manifest example;
- have the bundle's expected status; and
- evaluate true under the claim predicate.

Bundles that omit `covered_positive_examples` continue to cover only their
primary `positive_example`. This ADR does not change Universal Cell runtime
behavior, claim predicates, proof certificates, schematic traces, or SVGs.

## Success Criteria

- Red tests fail before implementation because transition evidence bundles do
  not expose `covered_positive_examples`.
- The self-mailbox unsupported evidence bundle names all three positive
  unsupported self-mailbox examples.
- The command-buffer unsupported evidence bundle names all three positive
  unsupported self-target command-buffer examples.
- Drifted covered-example names are rejected by transition evidence bundle
  validation.
- Existing evidence bundle validation subjects remain stable.
- Project status text/JSON and the full test suite remain green.

## Consequences

Integrated evidence bundles can now distinguish one trace-aligned primary
example from the broader manifest/proof coverage they rely on. This keeps the
trace layer focused while making finite boundary coverage visible and
validated.

## Test Plan

- Red: run
  `python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle tests.test_command_buffer_unsupported_evidence_bundle`
  after adding tests that require `covered_positive_examples`.
- Green: update the evidence bundle loader, validator, and the two unsupported
  bundle artifacts.
- Regression: run adjacent evidence-bundle, evidence-registry, project-status,
  JSON/compile/hygiene checks, and the full default suite before commit.

## After Action Report

The red run of
`python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle tests.test_command_buffer_unsupported_evidence_bundle`
ran 12 tests and failed four errors because `TransitionEvidenceBundle` did
not yet expose `covered_positive_examples`.

The implementation added optional `covered_positive_examples` loading to
`autarkic_systems.evidence_bundle`, defaulting to the primary
`positive_example` when omitted. Bundle validation now checks every covered
example against the named claim and expected status while still using
`positive_example` as the trace/SVG alignment point. The unsupported
self-mailbox and command-buffer bundles now list all three ADR-0119 positive
examples.

Verification passed with:

- `python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle tests.test_command_buffer_unsupported_evidence_bundle` (12 tests)
- `python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle tests.test_command_buffer_unsupported_evidence_bundle tests.test_evidence_bundle_registry tests.test_project_status_report` (64 tests)
- `python -m json.tool evidence/self_mailbox_unsupported_bundle.json`
- `python -m json.tool evidence/command_buffer_unsupported_bundle.json`
- `python -m py_compile autarkic_systems/evidence_bundle.py tests/test_self_mailbox_unsupported_evidence_bundle.py tests/test_command_buffer_unsupported_evidence_bundle.py`
- `git diff --check`
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
- `python -m autarkic_systems.project_status`
- `python -m autarkic_systems.project_status --format json`
- `python -m unittest discover` (579 tests)
