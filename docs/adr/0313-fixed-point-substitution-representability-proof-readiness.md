# ADR-0313: Fixed-Point Substitution Representability Proof Readiness

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0311 records `substitution-representability-proof` as one of the three
still-open predecessor proof blockers for `bridge-equality-proof`. The case
already has a compact frontier status and ADR-0309 finite certificate support,
but it does not yet have the same explicit proof-readiness handoff now present
for the `diagonal-instance-closure` root.

The missing handoff should say exactly: finite certificate support is accepted,
the substitution-representability construction case is certificate-ready, and
the proof case remains open. It must not promote certificate support into
proof closure.

## Decision

Add
`autarkic_systems.fixed_point_substitution_representability_proof_readiness`,
a text/JSON validator over
`claims/fixed_point_substitution_representability_proof_readiness.json`.

The readiness surface derives from:

- `claims/fixed_point_substitution_representability_frontier_status.json`; and
- `claims/fixed_point_substitution_representability_certificate.json`.

It records one readiness entry for `substitution-representability-proof`. The
entry must show that the case has accepted finite certificate support, has
covered predecessor certificate support for `diagonal-instance-closure` and
`substitution-graph-correctness-proof`, and remains blocked by the open
`substitution-representability-proof` proof case. The readiness status is
`blocked-certificate-ready-proof-open`, not proof closure.

Do not change fixed-point construction semantics, substitution
representability semantics, bridge-equality behavior, project-status behavior,
or any proof-case status in this slice.

## Success Criteria

- Red tests fail before implementation because the substitution
  representability proof-readiness module does not exist.
- The checked-in manifest validates against the current substitution
  representability frontier and certificate reports.
- JSON output exposes exactly one readiness entry for
  `substitution-representability-proof`.
- JSON output records the frontier as blocked by
  `substitution-representability-proof`.
- JSON output records the construction case as `proof-case-open`.
- JSON output records the certificate as accepted with seven certificate
  steps, two covered predecessor cases, and zero missing predecessor
  certificates.
- JSON output records five support surfaces and witness output code length
  296.
- Text output renders certificate-ready/proof-open status without proof
  promotion.
- Stale certificate step count metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that substitution representability, substitution graph
  correctness, bridge equality, the fixed-point equation, an arithmetized proof
  predicate, or self-consistency has been proved.

## Failure Criteria

- The readiness accepts when substitution representability frontier status or
  certificate validation rejects.
- The readiness accepts stale status, blocker, case-kind, case-status, covered
  predecessor, support-surface, witness-length, or certificate-step metadata.
- The slice promotes substitution representability, changes mathematical
  semantics, changes project-status semantics, or changes unrelated
  suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_readiness`.
- Green:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_readiness`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_readiness tests.test_fixed_point_substitution_representability_frontier_status tests.test_fixed_point_substitution_representability_certificate`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_substitution_representability_proof_readiness --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0313-substitution-representability-proof-readiness`.

The red run of
`python -m unittest tests.test_fixed_point_substitution_representability_proof_readiness`
failed as intended with an `ImportError` because
`autarkic_systems.fixed_point_substitution_representability_proof_readiness`
did not exist.

The implementation added the proof-readiness manifest, validator, CLI, tests,
suite registration, README entry, and human-facing note. The readiness surface
derives the currently accepted substitution-representability frontier and
finite certificate reports, then records that the construction case is
certificate-ready while the proof case remains open.

Verification receipts:

- `python -m unittest tests.test_fixed_point_substitution_representability_proof_readiness`
  passed 7 tests in 142.701s.
- `python -m unittest tests.test_fixed_point_substitution_representability_proof_readiness tests.test_fixed_point_substitution_representability_frontier_status tests.test_fixed_point_substitution_representability_certificate`
  passed 25 tests in 139.139s.
- `python -m autarkic_systems.fixed_point_substitution_representability_proof_readiness --format json`
  returned `accepted=true`, `certificate_count=1`,
  `certificate_step_count=7`, covered predecessor case kinds
  `diagonal-instance-closure` and
  `substitution-graph-correctness-proof`,
  `missing_certificate_predecessor_count=0`, frontier status `blocked`,
  frontier blocker `substitution-representability-proof`,
  `support_surface_count=5`, `witness_output_code_length=296`,
  `observed_frontier_accepted=true`, `observed_certificate_accepted=true`,
  `observed_proof_boundary_preserved=true`, readiness case
  `AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY`, readiness
  status `blocked-certificate-ready-proof-open`, and `failed_subjects=[]`.
- `python -m autarkic_systems.test_suite_selection --list-suites --format json`
  listed 166 discovered modules: 130 fast, 36 extended-fixed-point, and 166
  all-suite modules.
- `python -m compileall autarkic_systems tests` passed.
- `git diff --check` passed.
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 151.266s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 437 tests in 2725.241s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 36`.

This is substitution-representability proof-readiness metadata only. It does
not prove substitution representability, prove substitution graph correctness,
prove bridge equality, prove the fixed-point equation, introduce an
arithmetized proof predicate, or claim self-consistency.
