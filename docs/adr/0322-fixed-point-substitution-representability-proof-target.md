# ADR-0322: Fixed-Point Substitution Representability Proof Target

Date: 2026-05-28

## Status

Accepted.

## Context

ADR-0313 records `substitution-representability-proof` as
certificate-ready but proof-open. ADR-0319 and ADR-0320 then added explicit
blocked proof-closure targets for two neighboring fixed-point construction
proof blockers:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

The bridge-predecessor layer still has one predecessor readiness handoff
without a matching proof-target gate: substitution representability. Without
that target, a later bridge-predecessor proof-target coverage surface cannot
honestly say that every predecessor blocker has an explicit blocked
proof-closure target.

## Decision

Add
`autarkic_systems.fixed_point_substitution_representability_proof_target`, a
text/JSON validator over
`claims/fixed_point_substitution_representability_proof_target.json`.

The target derives from:

- `claims/fixed_point_substitution_representability_certificate.json`;
- `claims/fixed_point_substitution_representability_proof_readiness.json`;
  and
- `claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json`.

It records the accepted certificate support, the certificate-ready/proof-open
readiness handoff, the bridge predecessor coverage handoff, the missing proof
artifacts required before proof closure, and the proof-promotion non-claims.

Do not promote substitution representability, change bridge-equality
semantics, change fixed-point construction semantics, change project-status
behavior, or change any dependency manifest in this slice.

## Success Criteria

- Red tests fail before implementation because the substitution
  representability proof-target module does not exist.
- The checked-in manifest validates against the current substitution
  representability certificate, substitution representability proof-readiness,
  and bridge predecessor proof-readiness coverage reports.
- JSON output records `substitution-representability-proof` with proof target
  status `blocked-proof-closure-targeted`.
- JSON output records readiness status `blocked-certificate-ready-proof-open`,
  one accepted certificate, seven certificate steps, two covered predecessor
  cases, zero missing predecessor certificates, five support surfaces, and
  witness output code length 296.
- JSON output records three missing proof artifacts and
  `proof_closure_ready=false`.
- Text output renders the blocked proof target without proof promotion.
- Stale covered-predecessor, support-surface, witness-length, and
  missing-artifact metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that substitution representability, substitution graph
  correctness, diagonal-instance closure, bridge equality, the fixed-point
  equation, an arithmetized proof predicate, fixed-point construction, or
  self-consistency has been proved.

## Failure Criteria

- The target accepts when certificate, readiness, or bridge predecessor
  coverage dependency validation rejects.
- The target accepts stale covered-predecessor, support-surface,
  witness-length, readiness-status, certificate-step, or missing-artifact
  metadata.
- The slice promotes substitution representability, changes mathematical
  semantics, changes project-status semantics, or changes unrelated
  suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_target`.
- Green:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_target`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_target tests.test_fixed_point_substitution_representability_certificate tests.test_fixed_point_substitution_representability_proof_readiness tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_substitution_representability_proof_target --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0322-substitution-representability-proof-target`.

- The red run failed as intended before implementation:
  `python -m unittest tests.test_fixed_point_substitution_representability_proof_target`
  raised `ImportError` because
  `autarkic_systems.fixed_point_substitution_representability_proof_target`
  did not exist.
- Added
  `claims/fixed_point_substitution_representability_proof_target.json`,
  `autarkic_systems.fixed_point_substitution_representability_proof_target`,
  and `docs/fixed-point-substitution-representability-proof-target.md`. The
  validator derives the blocked proof target from the accepted substitution
  representability certificate, substitution representability proof-readiness
  handoff, and bridge predecessor proof-readiness coverage.
- The focused proof-target suite passed 9 tests in 179.239s.
- The focused certificate/readiness/bridge-predecessor seam passed 29 tests in
  215.481s.
- Live JSON validation passed with `accepted=true`, target id
  `as-fixed-point-substitution-representability-proof-target-v1`, case id
  `AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY`, case kind
  `substitution-representability-proof`, proof target status
  `blocked-proof-closure-targeted`, readiness status
  `blocked-certificate-ready-proof-open`, one accepted certificate, seven
  certificate steps, covered predecessor case kinds
  `diagonal-instance-closure` and
  `substitution-graph-correctness-proof`, zero missing predecessor
  certificates, five support surfaces, witness output code length 296, three
  missing proof artifacts, `proof_closure_ready=false`,
  `observed_certificate_accepted=true`, `observed_readiness_accepted=true`,
  `observed_bridge_predecessor_coverage_accepted=true`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- Suite selection listed 175 discovered modules: 130 fast, 45
  extended-fixed-point, and 175 all-suite modules.
- Hygiene passed with `python -m compileall autarkic_systems tests` and
  `git diff --check`.
- The fast suite passed 1188 tests in 207.010s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- The extended fixed-point suite passed 505 tests in 3550.323s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 45`.
- This is a blocked proof-closure target only. It does not prove substitution
  representability, diagonal-instance closure, substitution graph
  correctness, bridge equality, the fixed-point equation, introduce an
  arithmetized proof predicate, prove fixed-point construction, or claim
  self-consistency.
