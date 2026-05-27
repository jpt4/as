# ADR-0319: Fixed-Point Diagonal Instance Closure Proof Target

Date: 2026-05-27

## Status

Accepted.

## Context

The fixed-point frontier selector still exposes `diagonal-instance-closure` as
one of two selected root proof obligations. ADR-0303 gives that root finite
certificate support, ADR-0312 marks it certificate-ready but proof-open, and
ADR-0318 confirms that it remains part of the currently actionable selected
root readiness coverage.

The project still lacks a checked proof-target surface for the root itself:
one place that names the accepted support surfaces, states that the root is
not yet closed, and records the exact proof-closure artifacts that would be
needed before any future promotion from `proof-case-open`.

## Decision

Add `autarkic_systems.fixed_point_diagonal_instance_closure_proof_target`, a
text/JSON validator over
`claims/fixed_point_diagonal_instance_closure_proof_target.json`.

The target surface derives from:

- `claims/fixed_point_diagonal_instance_closure_certificate.json`;
- `claims/fixed_point_diagonal_instance_closure_proof_readiness.json`; and
- `claims/fixed_point_selected_root_proof_readiness_coverage.json`.

It records the current case id and case kind, the accepted certificate and
readiness surfaces, the selected-root coverage acceptance, and an explicit
blocked proof-target status with required missing proof artifacts.

Do not change fixed-point construction semantics, proof-case status,
frontier-selector behavior, project-status behavior, or any dependency
manifest in this slice.

## Success Criteria

- Red tests fail before implementation because the diagonal-instance closure
  proof-target module does not exist.
- The checked-in manifest validates against the current diagonal-instance
  closure certificate, diagonal-instance closure proof-readiness report, and
  selected-root proof-readiness coverage report.
- JSON output records case kind `diagonal-instance-closure`, proof target
  status `blocked-proof-closure-targeted`, one accepted certificate, seven
  certificate steps, readiness status `blocked-certificate-ready-proof-open`,
  and selected-root coverage acceptance.
- JSON output records the three required missing proof artifacts and confirms
  that proof closure remains blocked.
- Text output renders the proof target without proof promotion.
- Stale proof artifact metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that diagonal-instance closure, substitution graph
  correctness, substitution representability, bridge equality, the fixed-point
  equation, an arithmetized proof predicate, fixed-point construction, or
  self-consistency has been proved.

## Failure Criteria

- The target accepts when the certificate, readiness, or selected-root coverage
  dependency rejects.
- The target accepts stale case, status, certificate-step, or missing-artifact
  metadata.
- The slice promotes the diagonal-instance closure proof case, changes
  mathematical semantics, changes project-status semantics, or changes
  unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_target`.
- Green:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_target`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_target tests.test_fixed_point_diagonal_instance_closure_certificate tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_selected_root_proof_readiness_coverage`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_target --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Completed on branch `adr-0319-diagonal-instance-closure-proof-target`.

The red run behaved as required:
`python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_target`
failed with `ImportError` because
`autarkic_systems.fixed_point_diagonal_instance_closure_proof_target` did not
yet exist.

Implementation added the proof-target manifest, validator, report
documentation, suite-manifest entry, README navigation entry, and tests. The
first focused implementation run exposed an artifact-subject mapping bug:
stale `expected_missing_proof_artifact*` inputs were rejected, but under the
manifest/proof-boundary subjects instead of the intended artifact subject. The
mapping now routes both live target artifact entries and checked manifest
expected artifact entries through
`fixed-point-diagonal-instance-closure-proof-target-artifacts`.

Final verification:

- `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_target`
  passed 7 tests in 143.841s.
- `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_target tests.test_fixed_point_diagonal_instance_closure_certificate tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_selected_root_proof_readiness_coverage`
  passed 27 tests in 159.473s.
- `python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_target --format json`
  accepted the checked-in target with target id
  `as-fixed-point-diagonal-instance-closure-proof-target-v1`, case id
  `AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE`, case kind
  `diagonal-instance-closure`, proof target status
  `blocked-proof-closure-targeted`, readiness status
  `blocked-certificate-ready-proof-open`, one accepted certificate, seven
  certificate steps, three missing proof artifacts, `proof_closure_ready=false`,
  `observed_certificate_accepted=true`,
  `observed_readiness_accepted=true`,
  `observed_selected_root_coverage_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- `python -m autarkic_systems.test_suite_selection --list-suites --format json`
  listed 172 discovered modules: 130 fast, 42 extended-fixed-point, and 172
  all-suite modules.
- `python -m compileall autarkic_systems tests` passed.
- `git diff --check` passed.
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 197.077s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 480 tests in 3392.408s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 42`.

This is a blocked proof-closure target only. It does not prove
diagonal-instance closure, substitution graph correctness, substitution
representability, bridge equality, the fixed-point equation, an arithmetized
proof predicate, fixed-point construction, or self-consistency.
