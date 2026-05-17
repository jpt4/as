# ADR-0086: Chain Registry JSON Entries

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0084 added JSON output for chain evidence registry validation. The payload
records the registry ID, accepted status, bundle count, result count, and
validation results.

That is enough for pass/fail automation, but it is weaker than it should be
for operators and future agents: the payload does not list which bundle IDs,
paths, chain claim IDs, or expected statuses were actually validated. A caller
has to re-read the manifest to connect a green `bundle_count` to concrete
artifacts.

## Decision

Extend `chain_registry_validation_report_payload` with a `bundles` array.

Each entry will include:

- `bundle_id`;
- `path`;
- `chain_claim_id`; and
- `expected_status`.

This ADR does not change validation semantics, text output, or the manifest
schema.

## Success Criteria

- Red tests fail before implementation because the chain registry JSON payload
  lacks a `bundles` array.
- The in-process JSON payload lists the checked-in neighbor delivery chain
  bundle with path, claim ID, and expected status.
- Module execution in JSON registry mode emits the same bundle entry.
- Existing chain registry validation, chain evidence bundle validation, and
  full repository tests remain green.

## Consequences

Chain registry JSON becomes self-describing enough for automation to identify
the concrete chain evidence artifacts validated in a run.

## Test Plan

- Red: `python -m unittest tests.test_chain_evidence_bundle_registry` fails
  before payload entries are added.
- Green: the same focused test passes after adding payload entries.
- Regression: run adjacent chain CLI/registry/bundle tests, both registry JSON
  and single-bundle JSON modes, `py_compile`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

Implemented in `autarkic_systems/chain_evidence_bundle.py`, with focused
tests in `tests/test_chain_evidence_bundle_registry.py`.

The focused red run failed because `chain_registry_validation_report_payload`
did not include a `bundles` key. The green implementation adds a `bundles`
array to the registry JSON payload, with one record per registered chain
bundle: bundle ID, path, chain claim ID, and expected status.

Verification passed:

- focused red:
  `python -m unittest tests.test_chain_evidence_bundle_registry` failed before
  payload entries were added;
- focused green:
  `python -m unittest tests.test_chain_evidence_bundle_registry` passed 10
  tests;
- adjacent chain CLI/registry/bundle tests passed 20 tests;
- `python -m autarkic_systems.chain_evidence_bundle --registry
  evidence/chains/manifest.json --format json` reported `accepted: true`,
  `bundle_count: 1`, and the expected `bundles` entry;
- `python -m autarkic_systems.chain_evidence_bundle --format json` still
  reported `accepted: true` and `result_count: 9`;
- `py_compile` passed for the touched module and focused test;
- `git diff --check` passed; and
- `python -m unittest discover` passed 504 tests.
