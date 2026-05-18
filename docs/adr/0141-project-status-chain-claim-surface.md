# ADR-0141: Project Status Chain Claim Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0140 carries the base transition claim and proof-certificate validators
into `python -m autarkic_systems.project_status`. The same aggregate report
still exposes transition-chain claim/proof semantics only indirectly through
`chain_evidence` and `chain_language`.

That leaves an avoidable diagnostic gap. `autarkic_systems.chain_claims`
already validates the transition-chain language manifest, chain examples,
chain proof certificates, and chain surface as one operator-facing command.
Project status should summarize that existing validator alongside the base
claim/proof summaries.

## Decision

Add a `chain_claims` summary to project status JSON and text.

The summary will reuse `validate_transition_chain_claim_project` and
`chain_claim_validation_report_payload`, preserving the specialized chain
validator as the source of truth. The existing `--chain-language`,
`--chain-claims`, and `--chain-certificates` path overrides will feed both the
chain language summary and the new chain-claim summary.

The aggregate `accepted` field will require the chain-claim summary to be
accepted. Project status JSON will bump from `schema_version: 12` to
`schema_version: 13`.

## Success Criteria

- Red project-status tests fail before implementation because JSON still
  reports schema version `12`, omits `chain_claims`, and text omits the new
  chain-claim line.
- JSON reports the accepted chain-claim surface with language ID, paths,
  claim count, certificate count, failed subjects, result count, and summary
  results.
- Default text reports the accepted chain-claim surface with compact counts.
- A rejected chain proof-certificate fixture rejects aggregate project status
  and renders a compact failed-subject pointer in text.
- Full repository tests remain green.

## Consequences

The first diagnostic command now exposes both base and chain claim/proof
semantic validators, while leaving detailed clause output in the specialized
commands.

No new transition-chain claims, proof rules, evidence bundles, source-status
records, or runtime behavior are introduced.

## Test Plan

- Red: add project-status JSON/text tests for `chain_claims`, including a
  rejected chain certificate fixture.
- Green: reuse the existing chain-claim project validator and summarize its
  payload in project status.
- Regression: run focused project-status tests, project status text/JSON,
  direct chain-claim JSON CLI, `py_compile`, `git diff --check`, and the full
  default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` with focused tests in
`tests/test_project_status_report.py`.

The red test run executed 57 project-status tests and failed because project
status still reported `schema_version: 12`, omitted the `chain_claims` JSON
summary, omitted the compact transition-chain claim text line, and accepted an
incomplete chain proof-certificate fixture through the aggregate status.

The green implementation reuses `validate_transition_chain_claim_project` and
`chain_claim_validation_report_payload`, converts the existing chain-claim
payload into a `chain_claims` summary, includes chain-claim failed subjects,
and renders compact accepted/rejected text plus a `Chain claim failures:`
line.

Project status JSON now reports `schema_version: 13`, `accepted: true`, the
`as-transition-chain-claim-v1` chain claim language ID, 2 chain claims,
2 chain proof certificates, 4 validator result groups, and an empty
chain-claim failed-subject list on the checked-in manifests.

Verification passed: focused project-status tests ran 57 tests;
`python -m autarkic_systems.project_status` rendered the new chain-claim
summary lines; `python -m autarkic_systems.project_status --format json`
reported `schema_version: 13`; direct chain-claim JSON CLI was accepted;
`py_compile` and `git diff --check` passed; and
`python -m unittest discover` passed 636 tests.
