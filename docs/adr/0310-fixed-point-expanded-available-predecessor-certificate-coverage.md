# ADR-0310: Fixed-Point Expanded Available Predecessor Certificate Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0308 records available predecessor certificate coverage using selected-root
certificates plus the bridge-equality certificate. ADR-0309 then adds finite
certificate support for `substitution-representability-proof`.

The current ADR-0308 coverage remains useful as a historical view, but it still
reports `substitution-representability-proof` as missing certificate support
for the downstream `bridge-equality-proof` case. The next useful handoff is an
expanded available-certificate coverage surface that includes the
substitution-representability certificate while preserving that all underlying
proof cases remain open.

## Decision

Add
`autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage`,
a text/JSON validator over
`claims/fixed_point_expanded_available_predecessor_certificate_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_available_predecessor_certificate_coverage.json`; and
- `claims/fixed_point_substitution_representability_certificate.json`.

It records exactly three deferred coverage entries. The expanded coverage must
show that:

- `substitution-representability-proof` remains covered by the two root
  certificates and has no missing predecessor certificate support;
- `bridge-equality-proof` now has all three predecessor certificates available,
  including `substitution-representability-proof`, and has no missing
  predecessor certificate support; and
- `fixed-point-equation-lifting` remains covered by the bridge-equality
  certificate and has no missing predecessor certificate support.

Do not alter the historical ADR-0308 coverage, fixed-point construction
semantics, frontier selection, project-status behavior, or any proof-case
status in this slice.

## Success Criteria

- Red tests fail before implementation because the expanded coverage module
  does not exist.
- The checked-in manifest validates against the current ADR-0308 available
  coverage report and ADR-0309 substitution-representability certificate.
- JSON output exposes three deferred coverage entries.
- JSON output reports four available certificate subjects:
  `diagonal-instance-closure`, `substitution-graph-correctness-proof`,
  `substitution-representability-proof`, and `bridge-equality-proof`.
- JSON output reports twenty-seven total available certificate steps.
- JSON output reports no missing predecessor certificate support for
  `bridge-equality-proof`.
- JSON output still reports three open proof blockers for
  `bridge-equality-proof`.
- Text output renders expanded coverage and open proof blockers without proof
  promotion.
- Stale expected missing-predecessor metadata is rejected fail-closed.
- No output claims that substitution representability, substitution graph
  correctness, bridge equality, the fixed-point equation, an arithmetized
  proof predicate, or self-consistency has been proved.

## Failure Criteria

- The coverage accepts when ADR-0308 available coverage or ADR-0309
  substitution-representability certificate validation rejects.
- The coverage accepts stale missing predecessor lists, stale step counts, or
  stale available certificate subjects.
- The slice promotes downstream cases, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_expanded_available_predecessor_certificate_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_expanded_available_predecessor_certificate_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_expanded_available_predecessor_certificate_coverage tests.test_fixed_point_available_predecessor_certificate_coverage tests.test_fixed_point_substitution_representability_certificate`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0310-expanded-available-predecessor-coverage`.

The red run failed as intended with `ImportError` because
`autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage`
did not exist.

Additional dependency-failure tests were added after review. Before the
hardening patch, the missing base-coverage dependency case raised `KeyError`,
and the missing substitution-certificate dependency case incorrectly preserved
the proof boundary. Both now report structured rejections.

The implementation adds a derived manifest, validator, CLI report, tests, and
public documentation for expanded available predecessor certificate coverage.
It leaves ADR-0308 as a historical view while adding ADR-0309's
substitution-representability certificate to the available certificate subject
set.

Validation receipts:

- The focused expanded-coverage suite passed 8 tests in 134.350s.
- The focused expanded-coverage/available-coverage/substitution-certificate
  seam passed 20 tests in 136.610s.
- Live JSON validation passed with `accepted=true`,
  `coverage_entry_count=3`, available certificate subjects
  `diagonal-instance-closure`, `substitution-graph-correctness-proof`,
  `substitution-representability-proof`, and `bridge-equality-proof`,
  `total_available_certificate_step_count=27`,
  `observed_base_coverage_accepted=true`,
  `observed_substitution_certificate_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Live JSON reports no missing predecessor certificate support for
  `bridge-equality-proof`, while preserving its three open proof blockers:
  `diagonal-instance-closure`, `substitution-representability-proof`, and
  `substitution-graph-correctness-proof`.
- Suite selection listed 163 discovered modules: 130 fast, 33
  extended-fixed-point, and 163 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 151.437s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 416 tests in 2622.617s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 33`.

This is expanded available predecessor certificate coverage only. It does not
prove substitution representability, prove substitution graph correctness,
prove bridge equality, prove the fixed-point equation, introduce an
arithmetized proof predicate, or claim self-consistency.
