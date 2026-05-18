# ADR-0213: Transition Registry Bundle Failed Subjects

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0211 and ADR-0212 made network-sequence and transition-chain registry JSON
report inner failed subjects for loadable rejected bundles. The base
transition evidence registry still only exposes registry-level subjects such
as `registry-bundle-validation`.

That is structured enough to tell automation that some registered transition
evidence bundle rejected, but too coarse to tell whether the drift was in the
claim example, proof certificate, schematic trace, schematic SVG,
source-statuses, or semantic boundary without parsing a detail string or
rerunning per-bundle validation.

## Decision

Extend `registry_validation_report_payload` with `bundle_failed_subjects`, an
ordered list of rejected validation subjects from each loadable registered
transition evidence bundle:

- accepted registries report `bundle_failed_subjects: []`;
- rejected existing bundles report `{bundle_id, failed_subjects}` entries; and
- missing registered bundle files keep the existing registry-level
  missing-path behavior and do not add bundle-level subjects.

This does not change registry acceptance semantics, text formatting, project
status schema, demo registry schema, runtime behavior, claims, proof rules,
source-status boundaries, trace/SVG rendering, scheduler, topology, timing, or
command semantics.

## Success Criteria

- Red tests fail before implementation because transition registry JSON lacks
  `bundle_failed_subjects`.
- Accepted transition registry JSON reports `bundle_failed_subjects: []`.
- A registry pointing at a drifted existing transition bundle reports its
  bundle ID and inner failed subjects.
- CLI JSON emits the same field.
- Existing missing-bundle registry behavior remains unchanged.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_registry`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent evidence/project-status tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/evidence_bundle.py`, with focused coverage
in `tests/test_evidence_bundle_registry.py` and operator notes in
`docs/evidence-bundle-registry.md`.

The red focused run failed as intended because accepted direct and CLI
transition registry JSON lacked `bundle_failed_subjects`, and a registry
pointing at a drifted existing transition bundle could not expose
`claim-example` or `schematic-trace` without parsing
`registry-bundle-validation`.

The implementation adds `bundle_failed_subjects` to
`registry_validation_report_payload`, populated from loadable registered
bundle validation results. Missing registered bundle paths continue to report
the existing registry-level `registry-bundle-paths` and
`registry-bundle-validation` subjects while leaving `bundle_failed_subjects`
empty.

Focused transition evidence-bundle registry tests passed 22 tests. Adjacent
evidence/project-status tests passed 115 tests. Live transition registry JSON
reported `accepted: true`, `bundle_count: 11`, and
`bundle_failed_subjects: []`; live project-status summary remained accepted.
`compileall`, `git diff --check`, and the full default suite passed; the full
suite ran 902 tests.
