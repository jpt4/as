# ADR-0316: Fixed-Point Equation Lifting Proof Readiness

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0278 records the compact `fixed-point-equation-lifting` frontier status:
the equation-lifting construction case is still open, but the selected fixed
point target, checked equation bridge, formal codebook, and equation-lifting
alignment support surfaces accept.

ADR-0311 exposes `bridge-equality-proof` as certificate-ready but proof-open,
and ADR-0315 checks that bridge equality's three predecessor proof blockers
are exactly covered by accepted certificate-ready/proof-open readiness
handoffs. The obligation graph names `bridge-equality-proof` as the sole
predecessor of `fixed-point-equation-lifting`.

The remaining terminal handoff should say exactly: equation lifting is
certificate-ready as a proof-readiness handoff, because the equation-lifting
frontier accepts and the sole bridge-equality predecessor has accepted
proof-readiness coverage; nevertheless, equation lifting remains blocked and
proof-open. This must not promote a fixed-point equation proof.

## Decision

Add `autarkic_systems.fixed_point_equation_lifting_proof_readiness`, a
text/JSON validator over
`claims/fixed_point_equation_lifting_proof_readiness.json`.

The readiness surface derives from:

- `claims/fixed_point_equation_lifting_frontier_status.json`;
- `claims/fixed_point_bridge_equality_proof_closure_readiness.json`; and
- `claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json`.

It records the terminal `fixed-point-equation-lifting` case as
`blocked-certificate-ready-proof-open`, with exactly one predecessor
(`bridge-equality-proof`) and no missing predecessor readiness. It preserves
the frontier's finite support facts, including support surface count, direct
target code length, and bridge equation code length.

Do not change fixed-point construction semantics, bridge-equality semantics,
project-status behavior, or any proof-case status in this slice.

## Success Criteria

- Red tests fail before implementation because the equation-lifting
  proof-readiness module does not exist.
- The checked-in manifest validates against the current equation-lifting
  frontier, bridge-equality proof-closure readiness, and bridge predecessor
  readiness coverage reports.
- JSON output records `fixed-point-equation-lifting` readiness as
  `blocked-certificate-ready-proof-open`.
- JSON output records exactly one predecessor readiness entry:
  `bridge-equality-proof`.
- JSON output records zero missing predecessor readiness handoffs.
- JSON output records the equation-lifting support surface count as four,
  direct target code length as 4528, and bridge equation code length as 4815.
- Text output renders readiness without proof promotion.
- Stale support or predecessor metadata is rejected fail-closed.
- Missing dependency inputs produce structured rejections rather than
  exceptions.
- No output claims that bridge equality, the fixed-point equation, an
  arithmetized proof predicate, or self-consistency has been proved.

## Failure Criteria

- The readiness surface accepts when the equation-lifting frontier,
  bridge-equality readiness, or bridge predecessor coverage dependency rejects.
- The readiness surface accepts stale predecessor, support-count, code-length,
  readiness-status, or proof-boundary metadata.
- The slice promotes any proof case, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_equation_lifting_proof_readiness`.
- Green:
  `python -m unittest tests.test_fixed_point_equation_lifting_proof_readiness`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_equation_lifting_proof_readiness tests.test_fixed_point_equation_lifting_frontier_status tests.test_fixed_point_bridge_equality_proof_closure_readiness tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_equation_lifting_proof_readiness --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch `adr-0316-equation-lifting-proof-readiness`.

Red-green evidence:

- Red:
  `python -m unittest tests.test_fixed_point_equation_lifting_proof_readiness`
  failed before implementation with `ImportError` because
  `autarkic_systems.fixed_point_equation_lifting_proof_readiness` did not
  exist.
- Focused green:
  `python -m unittest tests.test_fixed_point_equation_lifting_proof_readiness`
  passed 8 tests in 174.437s.
- Focused seam:
  `python -m unittest tests.test_fixed_point_equation_lifting_proof_readiness tests.test_fixed_point_equation_lifting_frontier_status tests.test_fixed_point_bridge_equality_proof_closure_readiness tests.test_fixed_point_bridge_predecessor_proof_readiness_coverage`
  passed 36 tests in 193.047s.

The implementation added:

- `claims/fixed_point_equation_lifting_proof_readiness.json`;
- `autarkic_systems.fixed_point_equation_lifting_proof_readiness`;
- `docs/fixed-point-equation-lifting-proof-readiness.md`; and
- `tests/test_fixed_point_equation_lifting_proof_readiness.py`.

Live JSON validation passed with `accepted=true`, readiness id
`as-fixed-point-equation-lifting-proof-readiness-v1`, frontier status
`blocked`, frontier blocker `fixed-point-equation-lifting`, support surface
count 4, direct target code length 4528, bridge equation code length 4815,
one predecessor readiness entry `bridge-equality-proof`, zero missing
predecessor readiness entries, `observed_frontier_accepted=true`,
`observed_bridge_readiness_accepted=true`,
`observed_bridge_predecessor_coverage_accepted=true`,
`observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.

Suite selection listed 169 discovered modules: 130 fast, 39
extended-fixed-point, and 169 all-suite modules. The new test is classified
under `extended-fixed-point`.

Hygiene and regression gates passed:

- `python -m compileall autarkic_systems tests`;
- `git diff --check`;
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 197.337s with
  `manifest: as-test-suite-selection-v1 suite: fast module_count: 130`; and
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 459 tests in 3047.714s with
  `manifest: as-test-suite-selection-v1 suite: extended-fixed-point
  module_count: 39`.

This is terminal equation-lifting proof-readiness metadata only. It does not
prove bridge equality, prove the fixed-point equation, introduce an
arithmetized proof predicate, or claim self-consistency.
