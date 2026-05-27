# ADR-0314: Fixed-Point Substitution Graph Correctness Proof Readiness

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0311 records `substitution-graph-correctness-proof` as one of the three
still-open predecessor proof blockers for `bridge-equality-proof`. ADR-0304
already gives the root case finite certificate support, and ADR-0274 records
the wider substitution graph correctness frontier as blocked. ADR-0312 and
ADR-0313 now expose proof-readiness handoffs for the other two selected root
blockers. The graph-correctness root should receive the same explicit
certificate-ready/proof-open handoff.

The missing handoff should say exactly: finite certificate support is
accepted, the fixed-point graph-correctness construction case is
certificate-ready, and the proof case remains open. It must not promote
certificate support into proof closure or discharge the broader substitution
graph correctness frontier.

## Decision

Add
`autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness`,
a text/JSON validator over
`claims/fixed_point_substitution_graph_correctness_proof_readiness.json`.

The readiness surface derives from:

- `claims/substitution_graph_correctness_frontier_status.json`; and
- `claims/fixed_point_substitution_graph_correctness_certificate.json`.

It records one readiness entry for
`substitution-graph-correctness-proof`. The entry must show that the
fixed-point construction case has accepted finite certificate support, has
five checked graph-correctness cases and five finite dependencies, and remains
blocked by the open `substitution-graph-correctness-proof` proof case. The
readiness status is `blocked-certificate-ready-proof-open`, not proof closure.

Do not change fixed-point construction semantics, substitution graph
semantics, bridge-equality behavior, project-status behavior, or any proof-case
status in this slice.

## Success Criteria

- Red tests fail before implementation because the substitution graph
  correctness proof-readiness module does not exist.
- The checked-in manifest validates against the current substitution graph
  correctness frontier and fixed-point graph-correctness certificate reports.
- JSON output exposes exactly one readiness entry for
  `substitution-graph-correctness-proof`.
- JSON output records the broader substitution graph correctness frontier as
  blocked by `substitution-graph-correctness`.
- JSON output records the construction case as `proof-case-open`.
- JSON output records the certificate as accepted with seven certificate
  steps, five correctness cases, and five finite dependencies.
- Text output renders certificate-ready/proof-open status without proof
  promotion.
- Stale certificate step count metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that substitution graph correctness, bridge equality, the
  fixed-point equation, an arithmetized proof predicate, or self-consistency
  has been proved.

## Failure Criteria

- The readiness accepts when substitution graph correctness frontier status or
  fixed-point graph-correctness certificate validation rejects.
- The readiness accepts stale status, blocker, case-kind, case-status,
  correctness-case-count, finite-dependency-count, or certificate-step
  metadata.
- The slice promotes substitution graph correctness, changes mathematical
  semantics, changes project-status semantics, or changes unrelated
  suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_readiness`.
- Green:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_readiness`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_readiness tests.test_substitution_graph_correctness_frontier_status tests.test_fixed_point_substitution_graph_correctness_certificate`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch
`adr-0314-substitution-graph-correctness-proof-readiness`.

The red run of
`python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_readiness`
failed as intended with an `ImportError` because
`autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness`
did not exist.

The implementation added the proof-readiness manifest, validator, CLI, tests,
suite registration, README entry, and human-facing note. The readiness surface
derives the accepted substitution graph correctness frontier and fixed-point
graph-correctness finite certificate reports, then records that the selected
fixed-point construction case is certificate-ready while the proof case
remains open.

Verification receipts:

- `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_readiness`
  passed 7 tests in 117.770s.
- `python -m unittest tests.test_fixed_point_substitution_graph_correctness_proof_readiness tests.test_substitution_graph_correctness_frontier_status tests.test_fixed_point_substitution_graph_correctness_certificate`
  passed 31 tests in 192.671s.
- `python -m autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness --format json`
  returned `accepted=true`, `certificate_count=1`,
  `certificate_step_count=7`, `correctness_case_count=5`,
  `finite_dependency_count=5`, frontier status `blocked`, frontier blocker
  `substitution-graph-correctness`, `observed_frontier_accepted=true`,
  `observed_certificate_accepted=true`,
  `observed_proof_boundary_preserved=true`, readiness case
  `AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS`, readiness
  status `blocked-certificate-ready-proof-open`, open proof blocker
  `substitution-graph-correctness-proof`, and `failed_subjects=[]`.
- `python -m autarkic_systems.test_suite_selection --list-suites --format json`
  listed 167 discovered modules: 130 fast, 37 extended-fixed-point, and 167
  all-suite modules.
- `python -m compileall autarkic_systems tests` passed.
- `python -m py_compile autarkic_systems/fixed_point_substitution_graph_correctness_proof_readiness.py tests/test_fixed_point_substitution_graph_correctness_proof_readiness.py`
  passed.
- `git diff --check` passed.
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 148.942s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`.
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 444 tests in 2715.508s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 37`.

This is substitution-graph-correctness proof-readiness metadata only. It does
not prove substitution graph correctness, prove bridge equality, prove the
fixed-point equation, introduce an arithmetized proof predicate, or claim
self-consistency.
