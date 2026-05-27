# ADR-0315: Fixed-Point Bridge Predecessor Proof Readiness Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0311 exposes `bridge-equality-proof` as certificate-ready but proof-open
and records three still-open predecessor proof blockers:

- `diagonal-instance-closure`;
- `substitution-representability-proof`; and
- `substitution-graph-correctness-proof`.

ADRs 0312, 0313, and 0314 now give each predecessor its own
certificate-ready/proof-open readiness handoff. The bridge-equality readiness
surface still lists the three blockers, but no checked aggregate confirms that
the bridge blocker list is covered exactly by those three individual
proof-readiness surfaces.

The missing handoff should say exactly: bridge equality remains blocked, all
three predecessor proof blockers have accepted certificate-ready/proof-open
handoffs, and no proof case is promoted.

## Decision

Add
`autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage`,
a text/JSON validator over
`claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_bridge_equality_proof_closure_readiness.json`;
- `claims/fixed_point_diagonal_instance_closure_proof_readiness.json`;
- `claims/fixed_point_substitution_representability_proof_readiness.json`; and
- `claims/fixed_point_substitution_graph_correctness_proof_readiness.json`.

It records that the bridge-equality open proof blockers match exactly the
three accepted predecessor readiness case kinds, and that each predecessor is
certificate-ready but proof-open. It must preserve
`bridge-equality-proof` as blocked and must not close any predecessor proof.

Do not change bridge-equality semantics, fixed-point construction semantics,
project-status behavior, or any proof-case status in this slice.

## Success Criteria

- Red tests fail before implementation because the bridge predecessor
  proof-readiness coverage module does not exist.
- The checked-in manifest validates against the current bridge readiness and
  all three predecessor readiness reports.
- JSON output records `bridge-equality-proof` readiness as
  `blocked-certificate-ready-proof-open`.
- JSON output records exactly three predecessor readiness entries, one for
  each bridge open proof blocker.
- JSON output records zero missing predecessor readiness handoffs.
- JSON output records that all predecessor readiness entries are
  certificate-ready and proof-open.
- Text output renders the coverage without proof promotion.
- Stale predecessor metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that diagonal-instance closure, substitution
  representability, substitution graph correctness, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The coverage accepts when bridge-equality readiness or any predecessor
  readiness dependency rejects.
- The coverage accepts stale predecessor, blocker, readiness-status, or count
  metadata.
- The slice promotes any proof case, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage tests.test_fixed_point_bridge_equality_proof_closure_readiness tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_substitution_representability_proof_readiness tests.test_fixed_point_substitution_graph_correctness_proof_readiness`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0315-bridge-predecessor-proof-readiness-coverage`.

Red-green evidence:

- Red:
  `python -m unittest tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`
  failed before implementation with `ImportError` because
  `autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage`
  did not exist.
- Focused green:
  `python -m unittest tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`
  passed 7 tests in 150.235s.
- Focused seam:
  `python -m unittest tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage tests.test_fixed_point_bridge_equality_proof_closure_readiness tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_substitution_representability_proof_readiness tests.test_fixed_point_substitution_graph_correctness_proof_readiness`
  passed 35 tests in 168.451s.

The implementation added:

- `claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json`;
- `autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage`;
- `docs/fixed-point-bridge-predecessor-proof-readiness-coverage.md`; and
- `tests/test_fixed_point_bridge_predecessor_proof_readiness_coverage.py`.

Live JSON validation passed with `accepted=true`, coverage id
`as-fixed-point-bridge-predecessor-proof-readiness-coverage-v1`, bridge case
kind `bridge-equality-proof`, bridge readiness status
`blocked-certificate-ready-proof-open`, bridge open proof blocker case kinds
`diagonal-instance-closure`, `substitution-representability-proof`, and
`substitution-graph-correctness-proof`, three predecessor readiness entries,
zero missing predecessor readiness entries, three certificate-ready
predecessors, `observed_bridge_readiness_accepted=true`,
`observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.

Suite selection listed 168 discovered modules: 130 fast, 38
extended-fixed-point, and 168 all-suite modules. The new test is classified
under `extended-fixed-point`.

Hygiene and regression gates passed:

- `python -m compileall autarkic_systems tests`;
- `git diff --check`;
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 175.676s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`; and
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 451 tests in 2813.360s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 38`.

This is aggregate bridge predecessor proof-readiness coverage only. It does
not prove diagonal-instance closure, prove substitution representability,
prove substitution graph correctness, prove bridge equality, prove the
fixed-point equation, introduce an arithmetized proof predicate, or claim
self-consistency.
