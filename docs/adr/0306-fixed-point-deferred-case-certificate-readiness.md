# ADR-0306: Fixed-Point Deferred Case Certificate Readiness

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0302 selects the currently actionable fixed-point construction root
obligations and defers three downstream proof cases:

- `substitution-representability-proof`;
- `bridge-equality-proof`; and
- `fixed-point-equation-lifting`.

ADR-0305 confirms that both selected root obligations have accepted finite
certificate support. That support is useful handoff evidence for downstream
planning, but it must not be treated as proof closure. The next useful
operator surface is a compact readiness report for deferred cases that shows
which predecessor roots already have finite certificate coverage and which
predecessors still block promotion because the proof cases remain open.

## Decision

Add `autarkic_systems.fixed_point_deferred_case_certificate_readiness`, a
text/JSON validator over
`claims/fixed_point_deferred_case_certificate_readiness.json`.

The readiness surface derives from:

- `claims/fixed_point_construction_obligation_graph.json`;
- `claims/fixed_point_frontier_selector.json`; and
- `claims/fixed_point_selected_root_certificate_coverage.json`.

It records exactly three deferred readiness entries. For each deferred case it
must report:

- its predecessor proof cases from the obligation graph;
- which predecessor cases are covered by selected-root finite certificate
  coverage;
- which predecessor cases remain open and therefore still block promotion; and
- a readiness status that preserves downstream deferral.

Do not change fixed-point construction semantics, close any proof case, alter
frontier selection, or change project-status/handoff behavior in this slice.

## Success Criteria

- Red tests fail before implementation because the readiness module does not
  exist.
- The checked-in readiness manifest validates against the current graph,
  selector, and selected-root certificate coverage.
- JSON output exposes three deferred readiness entries.
- JSON output reports two certificate-covered predecessors for
  `substitution-representability-proof`, three predecessor proof cases for
  `bridge-equality-proof`, and one predecessor proof case for
  `fixed-point-equation-lifting`.
- Text output renders the deferred readiness boundary and non-claims.
- Stale deferred-case metadata is rejected fail-closed.
- No output claims that substitution representability, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The readiness accepts when the selector no longer defers the expected
  downstream cases.
- The readiness accepts when selected-root certificate coverage rejects.
- The graph predecessor set changes but the readiness still accepts stale
  expectations.
- The slice promotes downstream cases, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_readiness`.
- Green:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_readiness`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_readiness tests.test_fixed_point_selected_root_certificate_coverage tests.test_fixed_point_frontier_selector tests.test_fixed_point_construction_obligation_graph`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_deferred_case_certificate_readiness --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Completed on branch `adr-0306-deferred-case-certificate-readiness`.

- The red run failed as intended:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_readiness`
  reported `ImportError` because
  `autarkic_systems.fixed_point_deferred_case_certificate_readiness` did not
  yet exist.
- Added `claims/fixed_point_deferred_case_certificate_readiness.json`,
  `autarkic_systems.fixed_point_deferred_case_certificate_readiness`, and
  `docs/fixed-point-deferred-case-certificate-readiness.md`.
- The first implementation attempt caught that the manifest's JSON-object
  count fields are intentionally dictionary-shaped and therefore not hashable
  under `lru_cache`; the readiness validator now validates live manifests
  directly.
- The focused readiness suite passed 6 tests in 107.464s.
- The focused readiness/coverage/selector/graph seam passed 24 tests in
  112.882s.
- Live JSON validation returned `accepted=true`, `readiness_count=3`,
  deferred cases `substitution-representability-proof`,
  `bridge-equality-proof`, and `fixed-point-equation-lifting`, predecessor
  counts 2, 3, and 1, selected-root certificate-covered predecessor counts 2,
  2, and 0, `observed_selected_root_coverage_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Suite selection listed 159 discovered modules: 130 fast, 29
  extended-fixed-point, and 159 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 153.178s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 390 tests in 2541.362s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 29`.
- This is deferred-case readiness only. It does not prove substitution
  representability, prove bridge equality, prove the fixed-point equation,
  introduce an arithmetized proof predicate, or claim self-consistency.
