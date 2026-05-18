# ADR-0121: Registry Covered Example JSON

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0120 lets transition evidence bundles name `covered_positive_examples` and
validates every covered example against the claim predicate and expected
status. That coverage is visible if an operator opens the individual bundle
JSON, but the registry JSON and project-status JSON still list only bundle ID,
path, claim ID, and expected status.

The first-run machine-readable surfaces should not hide the coverage that the
validator just checked. Otherwise automation can see that a bundle passed but
not which positive examples made that pass meaningful.

## Decision

Add transition bundle coverage metadata to registry JSON bundle entries:

- `positive_example`, the primary trace-aligned example; and
- `covered_positive_examples`, the validated positive example list.

`autarkic_systems.evidence_bundle.registry_validation_report_payload` will
load each bundle entry when possible and add those fields. If a bundle cannot
be loaded, the fields are still present as `""` and `[]` so failure reports
remain structured.

Project status consumes transition registry payloads, so this ADR also bumps
project status JSON to `schema_version: 7`. Chain evidence bundle entries are
unchanged because transition-chain bundles have their own schema and do not yet
use `covered_positive_examples`.

## Success Criteria

- Red tests fail before implementation because transition evidence registry
  JSON bundle entries do not include `positive_example` or
  `covered_positive_examples`.
- Red tests fail before implementation because project status JSON remains
  `schema_version: 6` and lacks the covered-example metadata in transition
  bundle entries.
- Accepted transition evidence registry JSON reports each bundle's primary
  positive example and covered positive examples.
- Registry JSON keeps structured bundle entries even when a bundle cannot be
  loaded.
- Project status JSON reports `schema_version: 7` and carries the transition
  bundle coverage metadata.
- Project status text remains unchanged.
- Full repository tests remain green.

## Consequences

Automation can now inspect the concrete positive evidence coverage behind a
green registry or project-status result without opening every bundle file.
This makes ADR-0120's validated coverage part of the first diagnostic JSON
surface.

## Test Plan

- Red: run
  `python -m unittest tests.test_evidence_bundle_registry tests.test_project_status_report`
  after adding assertions for covered-example metadata.
- Green: update the transition registry JSON payload and project-status schema
  version.
- Regression: run focused registry/status tests, evidence-bundle adjacent
  tests, project status text/JSON, registry JSON, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

The red run of
`python -m unittest tests.test_evidence_bundle_registry tests.test_project_status_report`
ran 52 tests and failed because registry JSON bundle entries did not include
`positive_example` or `covered_positive_examples`, and project status still
reported `schema_version: 6`.

The implementation added bundle coverage fields to
`registry_validation_report_payload`, using structured fallback values when a
bundle cannot be loaded. Project status now reports `schema_version: 7` and
carries the richer transition evidence bundle entries through its existing
registry-summary path. Project status text output remained unchanged.

Verification passed with:

- `python -m unittest tests.test_evidence_bundle_registry tests.test_project_status_report` (52 tests)
- `python -m unittest tests.test_evidence_bundle_registry tests.test_project_status_report tests.test_self_mailbox_unsupported_evidence_bundle tests.test_command_buffer_unsupported_evidence_bundle` (64 tests)
- `python -m py_compile autarkic_systems/evidence_bundle.py autarkic_systems/project_status.py tests/test_evidence_bundle_registry.py tests/test_project_status_report.py`
- `git diff --check`
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
- `python -m autarkic_systems.project_status --format json`
- `python -m autarkic_systems.project_status`
- `python -m unittest discover` (579 tests)
