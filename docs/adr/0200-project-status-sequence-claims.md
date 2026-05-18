# ADR-0200: Project Status Sequence Claims

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0199 made aggregate project status validate the network-sequence evidence
registry. That evidence validator already checks the sequence claim and proof
certificate internally, but the main project-status claim/proof summary still
names only base transition claims and transition-chain claims.

That leaves two operator-facing gaps: the compact claim line does not account
for the accepted sequence claim, and the proof-rule audit omits the three
predicate-result steps in the network-sequence certificate manifest.

## Decision

Add the network-sequence claim/proof surface to
`autarkic_systems.project_status`:

- validate `claims/network_sequence_claims.json`;
- validate `claims/network_sequence_proof_certificates.json`;
- expose `sequence_claims` in JSON;
- include sequence claims in aggregate acceptance;
- render sequence claims in default text and compact summary modes;
- include sequence proof certificates in the proof-rule audit; and
- add CLI overrides for sequence claim and certificate manifests.

This does not add new sequence behavior, evidence artifacts, or proof rules.

## Success Criteria

- Red tests fail before implementation because project status still reports
  schema version `17`, has no `sequence_claims`, omits sequence claims from
  text and summary output, omits sequence certificate steps from the
  proof-rule audit, and rejects sequence claim/certificate CLI overrides.
- JSON project status includes accepted sequence claims with one claim and one
  certificate.
- Text project status renders the accepted network-sequence claim surface.
- Summary mode includes the sequence claim count and the proof-rule audit
  reports 52 predicate-result steps.
- Missing sequence claim or certificate manifests make project status rejected
  with structured failed subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run handoff tests, project-status text/summary/JSON, refreshed
  handoff, `python -m compileall -q autarkic_systems tests`,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented.

The red project-status run executed 81 tests and failed because aggregate
status still reported schema version `17`, had no `sequence_claims`, omitted
network-sequence claims from text and summary output, kept proof-rule audit at
49 predicate-result steps, rejected `--sequence-claims` /
`--sequence-certificates`, and did not accept sequence claim/certificate
builder overrides.

The implementation reuses the existing network-sequence claim validator,
exposes `sequence_claims` in JSON, includes that surface in aggregate
acceptance, renders the accepted one-claim/one-certificate sequence surface in
text and summary output, and counts the three sequence proof-certificate steps
in `proof_rule_audit`.

Focused verification passed 81 project-status tests and 6 handoff tests. Live
summary output reported `1 sequence claim/1 certificate` and proof rules
`predicate-result=52, manifest-example=0`; JSON output reported
`schema_version: 18` and accepted sequence claims. `compileall`,
`git diff --check`, refreshed handoff, and the full default suite passed. The
full suite ran 848 tests.
