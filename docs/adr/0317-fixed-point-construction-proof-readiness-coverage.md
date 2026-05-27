# ADR-0317: Fixed-Point Construction Proof Readiness Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0273 and the current fixed-point construction frontier status keep the
aggregate `fixed-point-construction` blocker open across five construction
proof cases:

- `diagonal-instance-closure`;
- `substitution-representability-proof`;
- `substitution-graph-correctness-proof`;
- `bridge-equality-proof`; and
- `fixed-point-equation-lifting`.

ADRs 0312 through 0316 now give each case an accepted
certificate-ready/proof-open readiness handoff. The project still lacks one
checked aggregate surface that confirms the current five open construction
cases are exactly covered by those five readiness handoffs.

The missing handoff should say exactly: the fixed-point construction frontier
remains blocked, all five proof cases remain open, and every open case has an
accepted certificate-ready/proof-open readiness surface. It must not promote
fixed-point construction, the fixed-point equation, or self-consistency.

## Decision

Add `autarkic_systems.fixed_point_construction_proof_readiness_coverage`, a
text/JSON validator over
`claims/fixed_point_construction_proof_readiness_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_construction_frontier_status.json`;
- `claims/fixed_point_diagonal_instance_closure_proof_readiness.json`;
- `claims/fixed_point_substitution_representability_proof_readiness.json`;
- `claims/fixed_point_substitution_graph_correctness_proof_readiness.json`;
- `claims/fixed_point_bridge_equality_proof_closure_readiness.json`; and
- `claims/fixed_point_equation_lifting_proof_readiness.json`.

It records that the five open construction case kinds match exactly the five
accepted proof-readiness handoffs, that all five readiness handoffs are
certificate-ready but proof-open, and that the aggregate frontier remains
blocked by `fixed-point-construction`.

Do not change fixed-point construction semantics, proof-case status,
project-status behavior, or any dependency manifest in this slice.

## Success Criteria

- Red tests fail before implementation because the construction
  proof-readiness coverage module does not exist.
- The checked-in manifest validates against the current fixed-point
  construction frontier and all five proof-readiness reports.
- JSON output records aggregate frontier status `blocked` and frontier blocker
  `fixed-point-construction`.
- JSON output records exactly five open construction cases and exactly five
  readiness entries.
- JSON output records zero missing readiness handoffs.
- JSON output records five certificate-ready, proof-open readiness handoffs.
- Text output renders the coverage without proof promotion.
- Stale case metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that diagonal-instance closure, substitution
  representability, substitution graph correctness, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, fixed-point
  construction, or self-consistency has been proved.

## Failure Criteria

- The coverage accepts when the construction frontier or any readiness
  dependency rejects.
- The coverage accepts stale case, readiness-status, frontier-status, or count
  metadata.
- The slice promotes any proof case, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_construction_proof_readiness_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_construction_proof_readiness_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_construction_proof_readiness_coverage tests.test_fixed_point_construction_frontier_status tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_substitution_representability_proof_readiness tests.test_fixed_point_substitution_graph_correctness_proof_readiness tests.test_fixed_point_bridge_equality_proof_closure_readiness tests.test_fixed_point_equation_lifting_proof_readiness`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_construction_proof_readiness_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch `adr-0317-construction-proof-readiness-coverage`.

- Added
  `tests/test_fixed_point_construction_proof_readiness_coverage.py` before
  implementation. The red run failed as intended with `ImportError` because
  `autarkic_systems.fixed_point_construction_proof_readiness_coverage` did not
  exist.
- Added
  `claims/fixed_point_construction_proof_readiness_coverage.json`,
  `autarkic_systems.fixed_point_construction_proof_readiness_coverage`, and
  `docs/fixed-point-construction-proof-readiness-coverage.md`. The validator
  derives aggregate construction proof-readiness coverage from the fixed-point
  construction frontier plus the five certificate-ready/proof-open readiness
  handoffs.
- The focused construction proof-readiness coverage suite passed 7 tests in
  165.414s.
- The focused construction frontier/readiness seam passed 59 tests in
  256.144s.
- Live JSON validation passed with `accepted=true`, coverage id
  `as-fixed-point-construction-proof-readiness-coverage-v1`, frontier status
  `blocked`, frontier blocker `fixed-point-construction`, five open case kinds,
  five readiness entries, zero missing readiness entries, five
  certificate-ready handoffs, `observed_frontier_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Suite selection listed 170 discovered modules: 130 fast, 40
  extended-fixed-point, and 170 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 181.681s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 466 tests in 3037.841s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 40`.
- This is aggregate fixed-point construction proof-readiness coverage only. It
  does not prove diagonal-instance closure, prove substitution
  representability, prove substitution graph correctness, prove bridge
  equality, prove the fixed-point equation, introduce an arithmetized proof
  predicate, prove fixed-point construction, or claim self-consistency.
