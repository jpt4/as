# ADR-0311: Fixed-Point Bridge Equality Proof-Closure Readiness

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0310 records expanded available predecessor certificate coverage for the
deferred fixed-point construction proof cases. In that surface,
`bridge-equality-proof` has finite certificate support for all three
predecessor cases:

- `diagonal-instance-closure`;
- `substitution-representability-proof`; and
- `substitution-graph-correctness-proof`.

That is useful but easy to overread. Complete predecessor certificate support
does not prove bridge equality. The bridge-equality case remains open until the
underlying predecessor proof cases close and an actual bridge-equality proof is
added.

## Decision

Add
`autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness`,
a text/JSON validator over
`claims/fixed_point_bridge_equality_proof_closure_readiness.json`.

The readiness surface derives from:

- `claims/fixed_point_expanded_available_predecessor_certificate_coverage.json`;
- `claims/fixed_point_bridge_equality_frontier_status.json`; and
- `claims/fixed_point_bridge_equality_certificate.json`.

It records one readiness entry for `bridge-equality-proof`. The entry must show
that all three predecessor certificates are available while all three
predecessor proof blockers remain open. The readiness status is therefore
`blocked-certificate-ready-proof-open`, not proof closure.

Do not change fixed-point construction semantics, bridge-equality frontier
semantics, formal-confidence behavior, project-status behavior, or any
proof-case status in this slice.

## Success Criteria

- Red tests fail before implementation because the proof-closure readiness
  module does not exist.
- The checked-in manifest validates against the current expanded available
  predecessor coverage, bridge-equality frontier, and bridge-equality
  certificate reports.
- JSON output exposes exactly one readiness entry for `bridge-equality-proof`.
- JSON output reports three predecessor certificates available and zero missing
  predecessor certificates for `bridge-equality-proof`.
- JSON output reports three open proof blockers for `bridge-equality-proof`.
- JSON output records the bridge-equality frontier as blocked by
  `bridge-equality-proof`.
- JSON output records the bridge-equality certificate as accepted with six
  certificate steps.
- Text output renders certificate-ready/proof-open status without proof
  promotion.
- Stale expected open proof blocker metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that diagonal-instance closure, substitution
  representability, substitution graph correctness, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The readiness accepts when expanded predecessor coverage, bridge-equality
  frontier status, or bridge-equality certificate validation rejects.
- The readiness accepts stale missing-predecessor lists, stale blocker counts,
  stale predecessor lists, or stale certificate step counts.
- The slice promotes bridge equality, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_bridge_equality_proof_closure_readiness`.
- Green:
  `python -m unittest tests.test_fixed_point_bridge_equality_proof_closure_readiness`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_bridge_equality_proof_closure_readiness tests.test_fixed_point_expanded_available_predecessor_certificate_coverage tests.test_fixed_point_bridge_equality_frontier_status tests.test_fixed_point_bridge_equality_certificate`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0311-bridge-equality-proof-closure-readiness`.

The red run failed as intended with `ImportError` because
`autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness` did not
exist.

The implementation adds a manifest, validator, CLI report, tests, and public
documentation for the bridge-equality proof-closure readiness surface. It
derives a single readiness entry from expanded predecessor certificate
coverage, bridge-equality frontier status, and the bridge-equality certificate.

Validation receipts:

- The focused proof-closure readiness suite passed 7 tests in 137.397s.
- The focused readiness/expanded-coverage/bridge-frontier/bridge-certificate
  seam passed 35 tests in 199.205s.
- Live JSON validation passed with `accepted=true`, readiness case
  `bridge-equality-proof`, readiness status
  `blocked-certificate-ready-proof-open`, three available predecessor
  certificates, zero missing predecessor certificates, three open proof
  blockers, blocked bridge-equality frontier status, bridge frontier blocker
  `bridge-equality-proof`, six bridge certificate steps,
  `observed_expanded_coverage_accepted=true`,
  `observed_bridge_frontier_accepted=true`,
  `observed_bridge_certificate_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Suite selection listed 164 discovered modules: 130 fast, 34
  extended-fixed-point, and 164 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 152.440s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 423 tests in 2613.156s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 34`.

This is bridge-equality proof-closure readiness only. It does not prove
diagonal-instance closure, prove substitution representability, prove
substitution graph correctness, prove bridge equality, prove the fixed-point
equation, introduce an arithmetized proof predicate, or claim
self-consistency.
