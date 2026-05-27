# ADR-0307: Fixed-Point Deferred Case Certificate Gap Analysis

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0306 records readiness for the three deferred fixed-point construction
cases. It shows that selected-root certificate coverage reaches some
predecessors, while the downstream proof cases still remain blocked because
predecessor proof cases are open.

The next useful operator surface is a compact gap analysis over that readiness
report. This should distinguish certificate-support gaps from proof-closure
blockers:

- `substitution-representability-proof` has certificate coverage for both
  predecessor roots, but both predecessor proof cases remain open;
- `bridge-equality-proof` has selected-root certificate coverage for two of
  three predecessors and lacks certificate coverage for
  `substitution-representability-proof`; and
- `fixed-point-equation-lifting` lacks predecessor certificate coverage because
  its only predecessor is `bridge-equality-proof`.

## Decision

Add `autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis`, a
text/JSON validator over
`claims/fixed_point_deferred_case_certificate_gap_analysis.json`.

The gap analysis derives from
`claims/fixed_point_deferred_case_certificate_readiness.json`. It records
exactly three gap entries, one for each deferred construction case. Each entry
must report:

- predecessor count;
- certificate-covered predecessor count;
- missing certificate predecessor case kinds;
- open proof blocker case kinds; and
- a gap status that does not promote the deferred case.

Do not change fixed-point construction semantics, close any proof case, alter
frontier selection, or change project-status/handoff behavior in this slice.

## Success Criteria

- Red tests fail before implementation because the gap-analysis module does
  not exist.
- The checked-in gap manifest validates against the current deferred-case
  readiness report.
- JSON output exposes three deferred gap entries.
- JSON output reports no certificate-support gaps for
  `substitution-representability-proof`.
- JSON output reports `substitution-representability-proof` as the only
  missing certificate predecessor for `bridge-equality-proof`.
- JSON output reports `bridge-equality-proof` as the only missing certificate
  predecessor for `fixed-point-equation-lifting`.
- Text output renders certificate gaps and proof blockers without proof
  promotion.
- Stale missing-certificate metadata is rejected fail-closed.
- No output claims that substitution representability, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The gap analysis accepts when deferred readiness rejects.
- The gap analysis accepts stale expected gap counts or missing predecessor
  lists.
- The slice promotes downstream cases, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_gap_analysis`.
- Green:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_gap_analysis`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_gap_analysis tests.test_fixed_point_deferred_case_certificate_readiness tests.test_fixed_point_selected_root_certificate_coverage`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Completed on branch `adr-0307-deferred-case-certificate-gap-analysis`.

- The red run failed as intended:
  `python -m unittest tests.test_fixed_point_deferred_case_certificate_gap_analysis`
  reported `ImportError` because
  `autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis` did not
  yet exist.
- Added `claims/fixed_point_deferred_case_certificate_gap_analysis.json`,
  `autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis`, and
  `docs/fixed-point-deferred-case-certificate-gap-analysis.md`.
- The focused gap-analysis suite passed 6 tests in 112.432s.
- The focused gap/readiness/coverage seam passed 18 tests in 113.083s.
- Live JSON validation returned `accepted=true`, `gap_entry_count=3`,
  certificate gap counts 0, 1, and 1 for
  `substitution-representability-proof`, `bridge-equality-proof`, and
  `fixed-point-equation-lifting`, missing certificate predecessors `none`,
  `substitution-representability-proof`, and `bridge-equality-proof`,
  `observed_readiness_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Suite selection listed 160 discovered modules: 130 fast, 30
  extended-fixed-point, and 160 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 159.890s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 396 tests in 2559.252s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 30`.
- This is certificate gap analysis only. It does not prove substitution
  representability, prove bridge equality, prove the fixed-point equation,
  introduce an arithmetized proof predicate, or claim self-consistency.
