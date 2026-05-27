# ADR-0320: Fixed-Point Substitution Graph Correctness Proof Target

Date: 2026-05-27

## Status

Accepted.

## Context

The fixed-point frontier selector still exposes
`substitution-graph-correctness-proof` as one of two selected root proof
obligations. ADR-0304 gives that root finite certificate support, ADR-0314
marks it certificate-ready but proof-open, ADR-0318 confirms that it remains
part of the currently actionable selected-root readiness coverage, and
ADR-0319 added the analogous blocked proof target for the other selected root.

The project still lacks a fixed-point-level checked proof-target surface for
`substitution-graph-correctness-proof`: one place that names the accepted
support surfaces, states that the root is not yet closed, records the exact
proof-closure artifacts that would be needed before any future promotion from
`proof-case-open`, and keeps the proof boundary explicit.

## Decision

Add
`autarkic_systems.fixed_point_substitution_graph_correctness_proof_target`, a
text/JSON validator over
`claims/fixed_point_substitution_graph_correctness_proof_target.json`.

The target surface derives from:

- `claims/fixed_point_substitution_graph_correctness_certificate.json`;
- `claims/fixed_point_substitution_graph_correctness_proof_readiness.json`;
  and
- `claims/fixed_point_selected_root_proof_readiness_coverage.json`.

It records the current case id and case kind, the accepted certificate and
readiness surfaces, the selected-root coverage acceptance, and an explicit
blocked proof-target status with required missing proof artifacts.

Do not change fixed-point construction semantics, proof-case status,
frontier-selector behavior, project-status behavior, or any dependency
manifest in this slice.

## Success Criteria

- Red tests fail before implementation because the substitution graph
  correctness proof-target module does not exist.
- The checked-in manifest validates against the current substitution graph
  correctness certificate, substitution graph correctness proof-readiness
  report, and selected-root proof-readiness coverage report.
- JSON output records case kind `substitution-graph-correctness-proof`, proof
  target status `blocked-proof-closure-targeted`, one accepted certificate,
  seven certificate steps, readiness status
  `blocked-certificate-ready-proof-open`, five correctness cases, five finite
  dependencies, and selected-root coverage acceptance.
- JSON output records the three required missing proof artifacts and confirms
  that proof closure remains blocked.
- Text output renders the proof target without proof promotion.
- Stale proof artifact metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that substitution graph correctness, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, fixed-point
  construction, or self-consistency has been proved.

## Failure Criteria

- The target accepts when the certificate, readiness, or selected-root coverage
  dependency rejects.
- The target accepts stale case, status, certificate-step, correctness-case,
  finite-dependency, or missing-artifact metadata.
- The slice promotes the substitution graph correctness proof case, changes
  mathematical semantics, changes project-status semantics, or changes
  unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_target`.
- Green:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_target`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_target tests.test_fixed_point_substitution_graph_correctness_certificate tests.test_fixed_point_substitution_graph_correctness_proof_readiness tests.test_fixed_point_selected_root_proof_readiness_coverage`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_substitution_graph_correctness_proof_target --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Completed on branch `adr-0320-substitution-graph-correctness-proof-target`.

The red run behaved as required:
`python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_target`
failed with `ImportError` because
`autarkic_systems.fixed_point_substitution_graph_correctness_proof_target` did
not yet exist.

Implementation added the proof-target manifest, validator, report
documentation, suite-manifest entry, README navigation entry, and tests. The
first focused implementation run exposed one integration error: the proof
target read correctness-case and finite-dependency counts from the certificate
report instead of the derived certificate object. The validator now reads those
counts from the accepted certificate and rejects stale manifest counts
fail-closed.

Final verification:

- `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_target`
  passed 8 tests in 168.598s.
- `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_target tests.test_fixed_point_substitution_graph_correctness_certificate tests.test_fixed_point_substitution_graph_correctness_proof_readiness tests.test_fixed_point_selected_root_proof_readiness_coverage`
  passed 28 tests in 184.139s.
- `python -m autarkic_systems.fixed_point_substitution_graph_correctness_proof_target --format json`
  accepted the checked-in target with target id
  `as-fixed-point-substitution-graph-correctness-proof-target-v1`, case id
  `AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS`, case kind
  `substitution-graph-correctness-proof`, proof target status
  `blocked-proof-closure-targeted`, readiness status
  `blocked-certificate-ready-proof-open`, one accepted certificate, seven
  certificate steps, five correctness cases, five finite dependencies, three
  missing proof artifacts, `proof_closure_ready=false`,
  `observed_certificate_accepted=true`,
  `observed_readiness_accepted=true`,
  `observed_selected_root_coverage_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- `python -m autarkic_systems.test_suite_selection --list-suites --format json`
  listed 173 discovered modules: 130 fast, 43 extended-fixed-point, and 173
  all-suite modules.
- `python -m compileall autarkic_systems tests` passed.
- `git diff --check` passed.
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 189.560s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 488 tests in 3281.686s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 43`.

This is a blocked proof-closure target only. It does not prove substitution
graph correctness, bridge equality, the fixed-point equation, introduce an
arithmetized proof predicate, prove fixed-point construction, or claim
self-consistency.
