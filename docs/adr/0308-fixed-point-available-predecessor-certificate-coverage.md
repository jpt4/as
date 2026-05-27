# ADR-0308: Fixed-Point Available Predecessor Certificate Coverage

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0307 records certificate-support gaps over deferred fixed-point
construction cases using selected-root certificate coverage. That gap analysis
correctly shows a missing certificate predecessor for
`fixed-point-equation-lifting`: `bridge-equality-proof`.

The project already has accepted finite certificate support for the
`bridge-equality-proof` construction case. The next useful operator surface is
a wider available-certificate coverage report that includes:

- selected-root certificate coverage for `diagonal-instance-closure`;
- selected-root certificate coverage for
  `substitution-graph-correctness-proof`; and
- bridge-equality finite certificate support for `bridge-equality-proof`.

This surface should update certificate-support visibility without promoting
any proof case. In particular, `fixed-point-equation-lifting` can have
available certificate coverage for its predecessor while still remaining
blocked by the open `bridge-equality-proof` case.

## Decision

Add `autarkic_systems.fixed_point_available_predecessor_certificate_coverage`,
a text/JSON validator over
`claims/fixed_point_available_predecessor_certificate_coverage.json`.

The coverage surface derives from:

- `claims/fixed_point_deferred_case_certificate_readiness.json`;
- `claims/fixed_point_selected_root_certificate_coverage.json`; and
- `claims/fixed_point_bridge_equality_certificate.json`.

It records exactly three deferred coverage entries. Each entry must report:

- predecessor count;
- certificate-covered predecessor count using all available certificates;
- missing certificate predecessor case kinds; and
- open proof blocker case kinds.

Do not change fixed-point construction semantics, close any proof case, alter
frontier selection, or change project-status/handoff behavior in this slice.

## Success Criteria

- Red tests fail before implementation because the available-coverage module
  does not exist.
- The checked-in manifest validates against the current readiness,
  selected-root coverage, and bridge-equality certificate reports.
- JSON output exposes three deferred coverage entries.
- JSON output reports all two predecessors certificate-covered for
  `substitution-representability-proof`.
- JSON output reports one missing certificate predecessor,
  `substitution-representability-proof`, for `bridge-equality-proof`.
- JSON output reports no missing certificate predecessors for
  `fixed-point-equation-lifting` because `bridge-equality-proof` has accepted
  finite certificate support.
- JSON output reports twenty total available certificate steps across the
  available predecessor certificates.
- Text output renders available certificate coverage and open proof blockers
  without proof promotion.
- Stale missing-certificate metadata is rejected fail-closed.
- No output claims that substitution representability, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The coverage accepts when readiness, selected-root coverage, or the
  bridge-equality certificate rejects.
- The coverage accepts stale expected missing predecessor lists.
- The slice promotes downstream cases, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_available_predecessor_certificate_coverage`.
- Green:
  `python -m unittest tests.test_fixed_point_available_predecessor_certificate_coverage`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_available_predecessor_certificate_coverage tests.test_fixed_point_deferred_case_certificate_gap_analysis tests.test_fixed_point_deferred_case_certificate_readiness tests.test_fixed_point_bridge_equality_certificate`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_available_predecessor_certificate_coverage --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0308-available-predecessor-certificate-coverage`.

The red test run preceded implementation:

```sh
python -m unittest tests.test_fixed_point_available_predecessor_certificate_coverage
```

It failed as intended with `ImportError` because
`autarkic_systems.fixed_point_available_predecessor_certificate_coverage` did
not exist.

The first implementation attempt then exposed an integration error: the new
validator tried to read an `open_proof_blocker_count` attribute from deferred
readiness entries. That caught a real API-boundary mismatch, and the
implementation was corrected to derive proof-boundary preservation from
`blocking_open_predecessor_case_kinds`.

Verification receipts:

- `python -m unittest tests.test_fixed_point_available_predecessor_certificate_coverage`
  passed 6 tests in 134.410s.
- `python -m unittest tests.test_fixed_point_available_predecessor_certificate_coverage tests.test_fixed_point_deferred_case_certificate_gap_analysis tests.test_fixed_point_deferred_case_certificate_readiness tests.test_fixed_point_bridge_equality_certificate`
  passed 25 tests in 197.337s.
- `python -m autarkic_systems.fixed_point_available_predecessor_certificate_coverage --format json`
  reported `accepted=true`, `coverage_entry_count=3`,
  available subjects `diagonal-instance-closure`,
  `substitution-graph-correctness-proof`, and `bridge-equality-proof`,
  `total_available_certificate_step_count=20`,
  `observed_bridge_equality_certificate_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- `python -m autarkic_systems.test_suite_selection --list-suites --format json`
  listed 161 discovered modules: 130 fast, 31 extended-fixed-point, and 161
  all-suite modules.
- `python -m compileall autarkic_systems tests` passed.
- `git diff --check` passed.
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 161.234s with `module_count: 130`.
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 402 tests in 2575.972s with `module_count: 31`.

The resulting surface preserves the intended boundary. It records available
finite predecessor certificate coverage, including the existing
bridge-equality certificate for `fixed-point-equation-lifting`, but it does
not prove substitution representability, bridge equality, the fixed-point
equation, an arithmetized proof predicate, or self-consistency.
