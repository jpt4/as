# ADR-0312: Fixed-Point Diagonal Instance Closure Proof Readiness

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0311 identifies `diagonal-instance-closure` as one of the three still-open
predecessor proof blockers for `bridge-equality-proof`. The root case already
has a compact frontier status and a seven-step finite certificate support
surface, but there is not yet a focused readiness surface that says exactly:
the finite support is accepted, the selected root case is certificate-ready,
and the proof case remains open.

## Decision

Add
`autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness`, a
text/JSON validator over
`claims/fixed_point_diagonal_instance_closure_proof_readiness.json`.

The readiness surface derives from:

- `claims/fixed_point_diagonal_instance_closure_frontier_status.json`; and
- `claims/fixed_point_diagonal_instance_closure_certificate.json`.

It records one readiness entry for `diagonal-instance-closure`. The entry must
show that the closure root has accepted finite certificate support and remains
blocked by the open `diagonal-instance-closure` proof case. The readiness
status is `blocked-certificate-ready-proof-open`, not proof closure.

Do not change fixed-point construction semantics, diagonal-instance closure
frontier semantics, formal-confidence behavior, project-status behavior, or
any proof-case status in this slice.

## Success Criteria

- Red tests fail before implementation because the diagonal-instance closure
  proof-readiness module does not exist.
- The checked-in manifest validates against the current diagonal-instance
  closure frontier and certificate reports.
- JSON output exposes exactly one readiness entry for
  `diagonal-instance-closure`.
- JSON output records the frontier as blocked by `diagonal-instance-closure`.
- JSON output records the construction case as `proof-case-open`.
- JSON output records the diagonal-instance closure certificate as accepted
  with seven certificate steps.
- JSON output records the diagonal instance code length as 296.
- Text output renders certificate-ready/proof-open status without proof
  promotion.
- Stale certificate step count metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that diagonal-instance closure, substitution
  representability, substitution graph correctness, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The readiness accepts when diagonal-instance closure frontier status or
  certificate validation rejects.
- The readiness accepts stale status, blocker, case-kind, case-status, code
  length, or certificate step metadata.
- The slice promotes diagonal-instance closure, changes mathematical
  semantics, changes project-status semantics, or changes unrelated
  suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_readiness`.
- Green:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_readiness`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_readiness tests.test_fixed_point_diagonal_instance_closure_frontier_status tests.test_fixed_point_diagonal_instance_closure_certificate`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch `adr-0312-diagonal-instance-closure-proof-readiness`.

The red run failed as intended before implementation:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure_proof_readiness
```

It failed with `ImportError` because
`autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness` did
not exist.

The implementation added the readiness manifest, validator module, public
documentation, README entry, and extended-suite registration. The validator
derives a single readiness entry from the accepted diagonal-instance closure
frontier and certificate reports, checks the 296-token diagonal instance,
checks one seven-step certificate, preserves the `proof-case-open` construction
case status, and rejects stale certificate-step metadata or missing
dependencies with structured failure subjects.

Verification receipts:

- Focused green run passed 7 tests in 115.359s.
- Focused readiness/frontier/certificate seam passed 27 tests in 175.307s.
- Live JSON validation passed with `accepted=true`, `frontier_status=blocked`,
  `frontier_blocker=diagonal-instance-closure`, `support_surface_count=5`,
  `certificate_count=1`, `certificate_step_count=7`,
  `diagonal_instance_code_length=296`,
  `observed_frontier_accepted=true`,
  `observed_certificate_accepted=true`,
  `observed_proof_boundary_preserved=true`, readiness case
  `AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE`, readiness status
  `blocked-certificate-ready-proof-open`, and `failed_subjects=[]`.
- Suite selection listed 165 discovered modules: 130 fast, 35
  extended-fixed-point, and 165 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 149.219s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 430 tests in 2661.142s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 35`.

This is proof-readiness metadata only. It does not prove diagonal-instance
closure, prove substitution representability, prove substitution graph
correctness, prove bridge equality, prove the fixed-point equation, introduce
an arithmetized proof predicate, or claim self-consistency.
