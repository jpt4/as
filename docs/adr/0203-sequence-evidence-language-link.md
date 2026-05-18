# ADR-0203: Sequence Evidence Language Link

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0201 added a checked network-sequence object language, and ADR-0202 made
aggregate project status fail closed over that language. The sequence evidence
bundle still predates the language layer: it cites sequence claims, proof
certificates, the claim validator, the executable witness, chain bundles, and
source-status records, but not `language/network_sequence_claim_language.json`.

An evidence bundle should expose every layer it claims to make auditable. If
the checked sequence language drifts, the network-sequence evidence bundle
should fail rather than relying on project status to catch the problem
elsewhere.

## Decision

Add the network-sequence claim language as an explicit evidence-bundle
artifact:

- add `sequence_language` to the checked bundle artifact list;
- load that path into `NetworkSequenceEvidenceBundle`;
- include it in schema path validation;
- validate it with the existing sequence object-language validator; and
- include a `sequence-language` validation result in bundle reports.

This does not add new runtime behavior, claims, proof rules, evidence bundles,
project-status fields, scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because loaded bundles have no
  `sequence_language_path`, the validation result set lacks
  `sequence-language`, and missing language paths are not rejected by bundle
  validation.
- The checked bundle records `language/network_sequence_claim_language.json`.
- Bundle text/JSON validation includes accepted `sequence-language`.
- Missing or invalid sequence language input rejects the evidence bundle.
- Registry validation remains green.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_evidence_bundle`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent sequence object-language/claim/evidence tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_evidence_bundle.py` and
`evidence/sequences/post_handoff_signal_bundle.json`, with documentation in
`docs/network-sequence-evidence-bundles.md`.

The red focused run failed as intended because loaded bundles had no
`sequence_language_path`, the validation result set lacked
`sequence-language`, missing language paths were not rejected by bundle
validation, and text reports lacked `OK sequence-language:`.

The green focused run passed 11 tests after the bundle loader, schema check,
and validation report reused the existing network-sequence object-language
validator. Adjacent evidence-bundle/object-language/claim tests passed 33
tests, live bundle JSON reported 8 accepted results including
`sequence-language`, registry JSON accepted 1 bundle, and the full default
suite passed 863 tests.
