# ADR-0309: Fixed-Point Substitution Representability Certificate

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0308 makes available predecessor certificate coverage visible for deferred
fixed-point construction cases. It shows that
`substitution-representability-proof` has available finite certificate support
for both of its predecessor proof cases:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

The substitution-representability construction case itself remains open. The
existing frontier status records five accepted finite support surfaces for
that case, including the substitution-representability witness, substitution
graph correctness cases, fixed-point equation bridge target, and substitution
witness bridge. The next useful surface is a finite certificate support object
for the substitution-representability case that composes those support facts
with ADR-0308 predecessor coverage without claiming proof closure.

## Decision

Add `autarkic_systems.fixed_point_substitution_representability_certificate`,
a text/JSON validator over
`claims/fixed_point_substitution_representability_certificate.json`.

The certificate surface derives from:

- `claims/fixed_point_substitution_representability_frontier_status.json`; and
- `claims/fixed_point_available_predecessor_certificate_coverage.json`.

It records one finite certificate support object for
`substitution-representability-proof`. The certificate must report:

- the construction case id and open construction status;
- accepted substitution-representability frontier status;
- accepted available predecessor certificate coverage;
- two certificate-covered predecessor proof cases;
- no missing predecessor certificate support;
- five accepted frontier support surfaces;
- the checked 296-token witness output code length; and
- an explicit open proof boundary.

Do not close `substitution-representability-proof`, change the fixed-point
construction case graph, alter frontier selection, or promote bridge equality
or fixed-point equation claims in this slice.

## Success Criteria

- Red tests fail before implementation because the substitution
  representability certificate module does not exist.
- The checked-in manifest validates against the current substitution
  representability frontier status and available predecessor certificate
  coverage reports.
- JSON output exposes one certificate support object with seven named steps.
- JSON output reports `substitution-representability-proof` as the selected
  case kind and `AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY`
  as the construction case id.
- JSON output reports two covered predecessor certificate subjects,
  `diagonal-instance-closure` and
  `substitution-graph-correctness-proof`, and no missing predecessor
  certificate support.
- JSON output reports five accepted frontier support surfaces and the
  296-token witness output code length.
- Text output renders certificate support and open proof blockers without
  proof promotion.
- Stale step metadata is rejected fail-closed.
- No output claims that substitution representability, substitution graph
  correctness, bridge equality, the fixed-point equation, an arithmetized
  proof predicate, or self-consistency has been proved.

## Failure Criteria

- The certificate accepts when the frontier status or available predecessor
  certificate coverage rejects.
- The certificate accepts stale expected step ids, predecessor coverage, or
  support counts.
- The slice promotes a proof case, changes mathematical semantics, changes
  project-status semantics, or changes unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_substitution_representability_certificate`.
- Green:
  `python -m unittest tests.test_fixed_point_substitution_representability_certificate`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_substitution_representability_certificate tests.test_fixed_point_substitution_representability_frontier_status tests.test_fixed_point_available_predecessor_certificate_coverage`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_substitution_representability_certificate --format json`.
- Suite gates:
  `python -m autarkic_systems.test_suite_selection --list-suites --format json`,
  `python -m autarkic_systems.test_suite_selection --suite fast`, and
  `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`.
- Hygiene:
  `python -m compileall autarkic_systems tests` and `git diff --check`.

## After Action Report

Implemented on branch `adr-0309-substitution-representability-certificate`.

The red test run preceded implementation:

```sh
python -m unittest tests.test_fixed_point_substitution_representability_certificate
```

It failed as intended with `ImportError` because
`autarkic_systems.fixed_point_substitution_representability_certificate` did
not exist.

Verification receipts:

- `python -m unittest tests.test_fixed_point_substitution_representability_certificate`
  passed 6 tests in 136.280s.
- `python -m unittest tests.test_fixed_point_substitution_representability_certificate tests.test_fixed_point_substitution_representability_frontier_status tests.test_fixed_point_available_predecessor_certificate_coverage`
  passed 24 tests in 144.087s.
- `python -m autarkic_systems.fixed_point_substitution_representability_certificate --format json`
  reported `accepted=true`, `certificate_count=1`,
  `certificate_step_count=7`,
  `construction_case_id=AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY`,
  `selected_case_kind=substitution-representability-proof`,
  covered predecessors `diagonal-instance-closure` and
  `substitution-graph-correctness-proof`,
  `missing_certificate_predecessor_count=0`,
  `observed_frontier_support_surface_count=5`,
  `observed_witness_output_code_length=296`,
  `observed_proof_boundary_preserved=true`, and `failed_subjects=[]`.
- `python -m autarkic_systems.test_suite_selection --list-suites --format json`
  listed 162 discovered modules: 130 fast, 32 extended-fixed-point, and 162
  all-suite modules.
- `python -m compileall autarkic_systems tests` passed.
- `git diff --check` passed.
- `python -m autarkic_systems.test_suite_selection --suite fast` passed 1188
  tests in 163.742s with `module_count: 130`.
- `python -m autarkic_systems.test_suite_selection --suite extended-fixed-point`
  passed 408 tests in 2595.984s with `module_count: 32`.

The resulting surface is finite certificate support only. It gives
`substitution-representability-proof` its own accepted certificate support
object, but it does not close the construction case, prove substitution
representability, prove substitution graph correctness, prove bridge equality,
prove the fixed-point equation, introduce an arithmetized proof predicate, or
claim self-consistency.
