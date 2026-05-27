# ADR-0305: Selected Root Certificate Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0302 selected two open root obligations for the current fixed-point
construction frontier:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

ADR-0303 and ADR-0304 added finite certificate support surfaces for those two
selected roots individually. The frontier still correctly remains blocked:
finite certificate support is not a proof of either selected root, and the
dependent construction cases remain deferred. The next useful handoff is a
compact coverage surface that verifies the selector's selected root set is
covered by accepted finite certificate support.

## Decision

Add `autarkic_systems.fixed_point_selected_root_certificate_coverage`, a
text/JSON validator over
`claims/fixed_point_selected_root_certificate_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/fixed_point_diagonal_instance_closure_certificate.json`; and
- `claims/fixed_point_substitution_graph_correctness_certificate.json`.

It records exactly two selected-root coverage entries, one for each selected
root obligation, and requires fourteen total checked certificate steps across
the two finite certificates.

Do not change fixed-point construction semantics, close either selected root
proof case, alter downstream deferral, or change project-status/handoff
behavior in this slice.

## Success Criteria

- Red tests fail before implementation because the coverage module does not
  exist.
- The checked-in coverage manifest validates against the current selector and
  both selected-root certificate reports.
- JSON output exposes two accepted coverage entries and fourteen total
  certificate steps.
- Text output renders the selected-root coverage boundary and non-claims.
- Stale selected-root metadata is rejected fail-closed.
- No output claims that diagonal-instance closure, graph correctness, bridge
  equality, the fixed-point equation, a proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The coverage accepts when either selected root is no longer selected by the
  frontier selector.
- The coverage accepts when either selected-root certificate rejects.
- The selected root set or total certificate-step count drifts but the coverage
  still accepts.
- The slice changes mathematical semantics, project-status semantics, handoff
  behavior, or unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_selected_root_certificate_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_selected_root_certificate_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_selected_root_certificate_coverage tests.test_fixed_point_diagonal_instance_closure_certificate tests.test_fixed_point_substitution_graph_correctness_certificate tests.test_fixed_point_frontier_selector`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_selected_root_certificate_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Completed on branch `adr-0305-selected-root-certificate-coverage`.

- The red run failed as intended:
  `python -m unittest tests.test_fixed_point_selected_root_certificate_coverage`
  reported `ImportError` because
  `autarkic_systems.fixed_point_selected_root_certificate_coverage` did not
  yet exist.
- Added `claims/fixed_point_selected_root_certificate_coverage.json`,
  `autarkic_systems.fixed_point_selected_root_certificate_coverage`, and
  `docs/fixed-point-selected-root-certificate-coverage.md`.
- The focused coverage suite passed 6 tests in 114.903s.
- The focused coverage/certificate/selector seam passed 24 tests in 134.375s.
- Live JSON validation returned `accepted=true`, `coverage_count=2`,
  `total_certificate_step_count=14`, selected roots
  `diagonal-instance-closure` and
  `substitution-graph-correctness-proof`, deferred downstream cases
  `substitution-representability-proof`, `bridge-equality-proof`, and
  `fixed-point-equation-lifting`, `failed_subjects=[]`, and preserved the
  proof boundary.
- Suite selection listed 158 discovered modules: 130 fast, 28
  extended-fixed-point, and 158 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- After tightening `next_as_action` wording to avoid proof-closure language,
  the focused coverage suite passed 6 tests in 109.348s and live JSON still
  accepted the manifest with the same coverage counts and proof boundary.
- The fast suite passed 1188 tests in 153.119s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 384 tests in 2551.047s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 28`.
- This is selected-root certificate coverage only. It does not close
  `diagonal-instance-closure`, close
  `substitution-graph-correctness-proof`, prove substitution
  representability, prove bridge equality, prove the fixed-point equation,
  introduce an arithmetized proof predicate, or claim self-consistency.
