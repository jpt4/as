# ADR-0318: Fixed-Point Selected Root Proof Readiness Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0302 selects the two currently actionable fixed-point construction root
obligations:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

ADRs 0312 and 0314 give those two root obligations accepted
certificate-ready/proof-open readiness handoffs. ADR-0317 then checks that all
five open construction cases have readiness handoffs. The project still lacks
one checked surface that ties the selector's active root obligations directly
to the corresponding root readiness handoffs.

That handoff should be intentionally narrow: it should show that the selected
root obligations are exactly the two selected by the frontier selector, that
both selected roots have accepted certificate-ready/proof-open readiness
surfaces, and that downstream construction cases remain deferred.

## Decision

Add `autarkic_systems.fixed_point_selected_root_proof_readiness_coverage`, a
text/JSON validator over
`claims/fixed_point_selected_root_proof_readiness_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/fixed_point_diagonal_instance_closure_proof_readiness.json`; and
- `claims/fixed_point_substitution_graph_correctness_proof_readiness.json`.

It records that the selector remains accepted, the selected roots are exactly
`diagonal-instance-closure` and `substitution-graph-correctness-proof`, both
selected roots have accepted certificate-ready/proof-open readiness handoffs,
and the three dependent construction cases remain deferred.

Do not change fixed-point construction semantics, proof-case status,
frontier-selector behavior, project-status behavior, or any dependency
manifest in this slice.

## Success Criteria

- Red tests fail before implementation because the selected-root
  proof-readiness coverage module does not exist.
- The checked-in manifest validates against the current frontier selector and
  the two selected-root proof-readiness reports.
- JSON output records selector status accepted, two selected roots, and three
  deferred construction cases.
- JSON output records exactly two selected-root readiness entries and zero
  missing selected-root readiness handoffs.
- JSON output records two certificate-ready, proof-open selected-root
  readiness handoffs.
- Text output renders the selected-root coverage without proof promotion.
- Stale selected-root metadata is rejected fail-closed.
- Missing selected-root readiness inputs produce structured rejections rather
  than exceptions.
- No output claims that diagonal-instance closure, substitution graph
  correctness, substitution representability, bridge equality, the fixed-point
  equation, an arithmetized proof predicate, fixed-point construction, or
  self-consistency has been proved.

## Failure Criteria

- The coverage accepts when the selector or either selected-root readiness
  dependency rejects.
- The coverage accepts stale selected-root, deferred-case, readiness-status,
  or count metadata.
- The slice promotes any proof case, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_selected_root_proof_readiness_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_selected_root_proof_readiness_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_selected_root_proof_readiness_coverage tests.test_fixed_point_frontier_selector tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_substitution_graph_correctness_proof_readiness`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_selected_root_proof_readiness_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch `adr-0318-selected-root-proof-readiness-coverage`.

- Added
  `tests/test_fixed_point_selected_root_proof_readiness_coverage.py` before
  implementation. The red run failed as intended with `ImportError` because
  `autarkic_systems.fixed_point_selected_root_proof_readiness_coverage` did not
  exist.
- Added
  `claims/fixed_point_selected_root_proof_readiness_coverage.json`,
  `autarkic_systems.fixed_point_selected_root_proof_readiness_coverage`, and
  `docs/fixed-point-selected-root-proof-readiness-coverage.md`. The validator
  derives selected-root coverage from the fixed-point frontier selector plus
  the two selected-root readiness reports.
- The focused selected-root proof-readiness coverage suite passed 7 tests in
  145.854s.
- The focused selector/selected-root readiness seam passed 27 tests in
  159.342s.
- Live JSON validation passed with `accepted=true`, coverage id
  `as-fixed-point-selected-root-proof-readiness-coverage-v1`, two selected
  roots, three deferred cases, two readiness entries, zero missing readiness
  entries, two certificate-ready handoffs, `observed_selector_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Suite selection listed 171 discovered modules: 130 fast, 41
  extended-fixed-point, and 171 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 186.614s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 473 tests in 3015.617s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 41`.
- This is selected-root proof-readiness coverage only. It does not prove
  diagonal-instance closure, prove substitution graph correctness, prove
  substitution representability, prove bridge equality, prove the fixed-point
  equation, introduce an arithmetized proof predicate, prove fixed-point
  construction, or claim self-consistency.
