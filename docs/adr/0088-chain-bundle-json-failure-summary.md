# ADR-0088: Chain Bundle JSON Failure Summary

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0087 added `failed_subjects` to chain evidence registry JSON output. The
single-bundle chain evidence JSON payload still lacks the same summary, so a
caller validating one bundle has to scan every result record to find the
rejected subjects.

The bundle and registry JSON contracts should be parallel where possible:
both report accepted status, result records, and a compact list of rejected
subjects for automation.

## Decision

Extend `chain_evidence_bundle_report_payload` with `failed_subjects`, an
ordered list of validation subjects whose result was rejected.

This ADR does not change validation semantics, text output, or the bundle
schema.

## Success Criteria

- Red tests fail before implementation because the chain bundle JSON payload
  lacks `failed_subjects`.
- Successful bundle JSON reports `failed_subjects: []`.
- Drifted bundle JSON reports `accepted: false` and includes the rejected
  subjects in `failed_subjects`.
- Module execution in JSON bundle mode returns exit code `1` for a drifted
  bundle and emits the same `failed_subjects`.
- Existing chain bundle validation, chain registry validation, and full
  repository tests remain green.

## Consequences

Single-bundle chain evidence validation is now as automation-friendly as chain
registry validation.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle`
  fails before `failed_subjects` is added.
- Green: the same focused test passes after adding the field.
- Regression: run adjacent chain CLI/registry/bundle tests, both bundle JSON
  and registry JSON modes, `py_compile`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

Implemented `failed_subjects` in `chain_evidence_bundle_report_payload`
without changing validation semantics, text output, or the bundle schema.

The red focused run, before implementation, failed in
`tests.test_neighbor_delivery_chain_evidence_bundle` because the bundle JSON
payload lacked `failed_subjects`. After implementation:

- `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle`
  passed 10 tests.
- `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle tests.test_chain_evidence_bundle_registry tests.test_chain_evidence_cli_target_selection`
  passed 24 tests.
- `python -m autarkic_systems.chain_evidence_bundle --format json` reported
  `accepted: true`, `result_count: 9`, and `failed_subjects: []`.
- `python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json`
  reported `accepted: true`, `bundle_count: 1`, and `failed_subjects: []`.
- `python -m py_compile autarkic_systems/chain_evidence_bundle.py tests/test_neighbor_delivery_chain_evidence_bundle.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 508 tests.

The single-bundle JSON contract now matches the registry failure-summary
surface for the same concept: callers can read `failed_subjects` directly
instead of scanning every validation result.
