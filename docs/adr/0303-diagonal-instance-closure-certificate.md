# ADR-0303: Diagonal Instance Closure Certificate

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0302 selected two open root obligations for the current fixed-point
construction frontier:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

The first root already has finite closure evidence and a finite candidate
surface, but those support facts are still split between the closure,
candidate-surface, and selector reports. The next slice should expose a small
certificate support object for the selected diagonal-instance root without
claiming that the proof case has been completed.

## Decision

Add `autarkic_systems.fixed_point_diagonal_instance_closure_certificate`, a
text/JSON validator over
`claims/fixed_point_diagonal_instance_closure_certificate.json`.

The certificate derives one finite support object from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/fixed_point_diagonal_instance_closure.json`; and
- `claims/fixed_point_diagonal_instance_candidate_surface.json`.

The certificate records seven checked steps:

- `select-open-root-obligation`;
- `accept-closure-report`;
- `accept-candidate-surface`;
- `check-closed-diagonal-instance`;
- `check-codebook-roundtrip`;
- `match-candidate-to-closure`; and
- `preserve-open-proof-boundary`.

Do not change fixed-point construction semantics, close the
`diagonal-instance-closure` proof case, alter the aggregate frontier selector,
or change project-status/handoff behavior in this slice.

## Success Criteria

- Red tests fail before implementation because the certificate module does not
  exist.
- The checked-in certificate validates against the current selector, closure,
  and candidate-surface reports.
- JSON output exposes one accepted finite certificate with seven accepted
  steps.
- Text output renders the selected-root certificate and non-claims.
- Stale expected step metadata is rejected fail-closed.
- No output claims that the diagonal-instance proof case, fixed-point equation,
  proof predicate, or self-consistency theorem has been proved.

## Failure Criteria

- The certificate accepts when the selector no longer selects
  `diagonal-instance-closure` as an open root obligation.
- The certificate accepts when the closure or candidate-surface report rejects.
- The candidate surface no longer matches the closure evidence but the
  certificate still accepts.
- The slice changes mathematical semantics, project-status semantics, handoff
  behavior, or unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_certificate`.
- Green:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_certificate`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_certificate tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_diagonal_instance_candidate_surface tests.test_fixed_point_frontier_selector`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_diagonal_instance_closure_certificate --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented.

The red run was:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure_certificate
```

It failed as intended before implementation with:

```text
ImportError: cannot import name 'fixed_point_diagonal_instance_closure_certificate'
```

The implementation adds
`autarkic_systems.fixed_point_diagonal_instance_closure_certificate`,
`claims/fixed_point_diagonal_instance_closure_certificate.json`, and
`docs/fixed-point-diagonal-instance-closure-certificate.md`. The validator
derives one finite certificate from the accepted frontier selector,
diagonal-instance closure report, and candidate-surface report.

The first green attempt caught a report-shape mismatch: future-work guardrails
live on the candidate manifest rather than the derived candidate object. The
certificate now reads that manifest-level boundary.

Focused certificate verification passed:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure_certificate
```

Observed result:

```text
Ran 6 tests in 102.073s
OK
```

The focused certificate/closure/candidate/selector seam passed:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure_certificate tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_diagonal_instance_candidate_surface tests.test_fixed_point_frontier_selector
```

Observed result:

```text
Ran 35 tests in 170.429s
OK
```

The live JSON validator accepted one seven-step finite certificate:

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_closure_certificate --format json
```

Observed result:

```text
accepted=true
certificate_count=1
certificate_step_count=7
observed_candidate_code_length=296
observed_selector_accepts_root=true
observed_closure_accepted=true
observed_candidate_surface_accepted=true
observed_candidate_matches_closure=true
observed_proof_boundary_preserved=true
failed_subjects=[]
```

The suite index listed 156 discovered modules, with 130 fast modules, 26
extended fixed-point modules, and 156 all-suite modules:

```sh
python -m autarkic_systems.test_suite_selection --list-suites --format json
```

The fast suite passed:

```sh
python -m autarkic_systems.test_suite_selection --suite fast
```

Observed result:

```text
Ran 1188 tests in 140.246s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 130
```

The extended fixed-point suite passed:

```sh
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point
```

Observed result:

```text
Ran 372 tests in 2441.532s
OK
manifest: as-test-suite-selection-v1 suite: extended-fixed-point module_count: 26
```

Hygiene checks passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
```

This slice remains finite certificate support only. It does not close the
`diagonal-instance-closure` proof case, prove substitution representability,
prove substitution graph correctness, prove bridge equality, prove the
fixed-point equation, introduce an arithmetized proof predicate, or claim
self-consistency.
