# ADR-0321: Fixed-Point Selected Root Proof Target Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0318 records that both currently selected fixed-point construction root
obligations have certificate-ready but proof-open readiness handoffs. ADR-0319
and ADR-0320 then added individual blocked proof-closure targets for those two
selected roots:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

The project now needs one aggregate surface showing that the selected-root
proof-target layer is complete: both selected roots have accepted proof-target
gates, both gates remain blocked, and the proof boundary is still preserved.
Without that aggregate, downstream bridge-equality and construction-level
handoffs cannot cite one checked proof-target coverage object.

## Decision

Add `autarkic_systems.fixed_point_selected_root_proof_target_coverage`, a
text/JSON validator over
`claims/fixed_point_selected_root_proof_target_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_selected_root_proof_readiness_coverage.json`;
- `claims/fixed_point_diagonal_instance_closure_proof_target.json`; and
- `claims/fixed_point_substitution_graph_correctness_proof_target.json`.

It records the selected root set, the two accepted proof-target gates, the
total missing proof artifacts across those gates, zero proof-closure-ready
roots, and the proof-promotion non-claims.

Do not promote any root obligation, change fixed-point construction semantics,
change frontier-selector behavior, change project-status behavior, or change
any dependency manifest in this slice.

## Success Criteria

- Red tests fail before implementation because the selected-root proof-target
  coverage module does not exist.
- The checked-in manifest validates against the current selected-root
  proof-readiness coverage report and both selected-root proof-target reports.
- JSON output records two selected roots, two accepted proof targets, two
  blocked proof targets, zero proof-closure-ready roots, six total missing
  proof artifacts, and selected-root readiness coverage acceptance.
- Text output renders proof-target coverage without proof promotion.
- Stale selected-root, target-count, blocked-target, closure-ready, and
  missing-artifact metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that diagonal-instance closure, substitution graph
  correctness, substitution representability, bridge equality, the fixed-point
  equation, an arithmetized proof predicate, fixed-point construction, or
  self-consistency has been proved.

## Failure Criteria

- The coverage accepts when selected-root readiness coverage or either
  proof-target dependency rejects.
- The coverage accepts stale selected-root, target-count, blocked-target,
  closure-ready, or missing-artifact metadata.
- The slice promotes either selected root proof case, changes mathematical
  semantics, changes project-status semantics, or changes unrelated
  suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_selected_root_proof_target_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_selected_root_proof_target_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_selected_root_proof_target_coverage tests.test_fixed_point_selected_root_proof_readiness_coverage tests.test_fixed_point_diagonal_instance_closure_proof_target tests.test_fixed_point_substitution_graph_correctness_proof_target`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_selected_root_proof_target_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch `adr-0321-selected-root-proof-target-coverage`.

- The red run failed as intended before implementation:
  `python -m unittest tests.test_fixed_point_selected_root_proof_target_coverage`
  raised `ImportError` because
  `autarkic_systems.fixed_point_selected_root_proof_target_coverage` did not
  exist.
- Added
  `claims/fixed_point_selected_root_proof_target_coverage.json`,
  `autarkic_systems.fixed_point_selected_root_proof_target_coverage`, and
  `docs/fixed-point-selected-root-proof-target-coverage.md`. The validator
  derives aggregate selected-root proof-target coverage from the accepted
  selected-root proof-readiness coverage and the two accepted blocked
  proof-target manifests for diagonal-instance closure and substitution graph
  correctness.
- The focused coverage suite passed 8 tests in 147.369s.
- The focused selected-root/proof-target seam passed 30 tests in 146.357s.
- Live JSON validation passed with `accepted=true`, coverage id
  `as-fixed-point-selected-root-proof-target-coverage-v1`,
  `observed_selected_root_readiness_coverage_accepted=true`,
  `observed_proof_boundary_preserved=true`, selected case kinds
  `diagonal-instance-closure` and
  `substitution-graph-correctness-proof`, `selected_case_count=2`,
  `proof_target_count=2`, `blocked_proof_target_count=2`,
  `proof_closure_ready_count=0`, `missing_case_kinds=[]`,
  `missing_proof_artifact_count=6`, and `failed_subjects=[]`.
- Suite selection listed 174 discovered modules: 130 fast, 44
  extended-fixed-point, and 174 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 175.648s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 496 tests in 3231.890s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 44`.
- This is aggregate blocked proof-target coverage only. It does not prove
  diagonal-instance closure, substitution graph correctness, substitution
  representability, bridge equality, the fixed-point equation, introduce an
  arithmetized proof predicate, prove fixed-point construction, or claim
  self-consistency.
