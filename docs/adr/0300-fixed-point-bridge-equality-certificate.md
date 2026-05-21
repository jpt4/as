# ADR-0300: Fixed-Point Bridge Equality Certificate

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0269 added finite bridge-equality evaluation evidence for the current
fixed-point construction stack. That surface derives the left bridge term
`substitution_code(quote(seed), quote(seed))`, evaluates it at the meta level,
and checks that the output matches the right quoted diagonal-instance term.

ADR-0276 then summarized that alignment and evaluation evidence in the compact
bridge-equality frontier status, while correctly keeping the frontier blocked by
`bridge-equality-proof`.

The remaining gap is that the equality support is still split between
alignment/evaluation reports. Operators can see that the evaluation accepted,
but there is no small certificate surface that names the checked finite steps
needed by the bridge-equality construction case. The next slice should expose
that evidence without claiming a general bridge-equality proof, fixed-point
equation proof, proof predicate, or self-consistency theorem.

## Decision

Add `autarkic_systems.fixed_point_bridge_equality_certificate`, a text/JSON
validator for a checked finite bridge-equality certificate manifest.

The certificate will derive one accepted certificate for
`AS-FIXED-POINT-CONSTRUCTION-BRIDGE-EQUALITY` from the existing bridge-equality
evaluation, alignment, fixed-point equation bridge, and codebook surfaces. It
will expose the following checked step ids:

- `decode-left-formula`;
- `decode-self-argument`;
- `evaluate-substitution-code`;
- `match-witness-output`;
- `match-right-quote`; and
- `bridge-equation-formed`.

The bridge-equality frontier status will include the certificate as an accepted
support surface, but it will continue reporting `frontier_status=blocked` and
`frontier_blocked_by=bridge-equality-proof`.

The aggregate fixed-point construction frontier will include the certificate in
the finite support for the `bridge-equality-proof` case, but all five
construction cases remain `proof-case-open` and the aggregate frontier remains
blocked by `fixed-point-construction`.

Do not change fixed-point equation semantics, substitution graph correctness,
substitution representability status, construction-case status, Proflog
dependencies, formal-confidence blockers, handoff behavior, or suite-selection
behavior.

## Success Criteria

- Red tests fail before implementation because the certificate module and
  manifest do not exist.
- The certificate JSON reports one accepted certificate for
  `AS-FIXED-POINT-CONSTRUCTION-BRIDGE-EQUALITY`.
- Certificate steps include the six expected step ids and derive their
  acceptance from the current bridge-equality evaluation/alignment route.
- Text output renders a concise fixed-point bridge equality certificate report.
- The bridge-equality frontier includes certificate support but remains blocked
  by `bridge-equality-proof`.
- The aggregate fixed-point construction frontier includes the certificate under
  the bridge-equality finite support while remaining blocked by
  `fixed-point-construction`.
- Non-claims remain explicit: no bridge equality proof, no fixed-point equation
  proof, no arithmetized proof predicate, and no self-consistency theorem.

## Failure Criteria

- Any report says the bridge equality, fixed-point equation, or self-consistency
  theorem has been proved.
- The certificate hand-authors equality facts instead of deriving them from the
  accepted evaluation/alignment surfaces.
- The bridge-equality or aggregate construction frontier stops reporting a
  blocked status.
- Proflog becomes a dependency for this slice.
- `autarkic_systems.handoff`, suite-selection files, formal-confidence
  semantics, or project-status semantics are changed just to surface the
  certificate.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_bridge_equality_certificate tests.test_fixed_point_bridge_equality_frontier_status tests.test_fixed_point_construction_frontier_status`.
- Green:
  `python -m unittest tests.test_fixed_point_bridge_equality_certificate tests.test_fixed_point_bridge_equality_frontier_status tests.test_fixed_point_construction_frontier_status`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_bridge_equality_certificate tests.test_fixed_point_bridge_equality_evaluation tests.test_fixed_point_bridge_equality_alignment tests.test_fixed_point_bridge_equality_frontier_status tests.test_fixed_point_construction_frontier_status`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_bridge_equality_certificate --format json`,
  `python -m autarkic_systems.fixed_point_bridge_equality_frontier_status --format json`,
  and
  `python -m autarkic_systems.fixed_point_construction_frontier_status --format json`.
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
python -m unittest tests.test_fixed_point_bridge_equality_certificate tests.test_fixed_point_bridge_equality_frontier_status tests.test_fixed_point_construction_frontier_status
```

It failed as intended before implementation with:

```text
ImportError: cannot import name 'fixed_point_bridge_equality_certificate'
ImportError: cannot import name 'REQUIRED_CASE_DEPENDENCY_SUBJECTS'
AttributeError: 'FixedPointConstructionFrontierStatusManifest' object has no attribute 'bridge_equality_certificate_path'
```

The implementation adds `autarkic_systems.fixed_point_bridge_equality_certificate`
and `claims/fixed_point_bridge_equality_certificate.json`. The validator derives
one certificate support object from the accepted fixed-point equation bridge,
bridge-equality alignment, bridge-equality evaluation, and codebook surfaces.

Focused certificate verification passed:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_certificate
```

Observed result:

```text
Ran 7 tests in 185.175s
OK
```

The bridge-equality frontier status passed:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_frontier_status
```

Observed result:

```text
Ran 13 tests in 0.712s
OK
```

The aggregate fixed-point construction frontier status passed:

```sh
python -m unittest tests.test_fixed_point_construction_frontier_status
```

Observed result:

```text
Ran 16 tests in 78.713s
OK
```

The wider focused seam passed:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_certificate tests.test_fixed_point_bridge_equality_evaluation tests.test_fixed_point_bridge_equality_alignment tests.test_fixed_point_bridge_equality_frontier_status tests.test_fixed_point_construction_frontier_status
```

Observed result:

```text
Ran 60 tests in 963.565s
OK
```

Live JSON checks passed:

```sh
python -m autarkic_systems.fixed_point_bridge_equality_certificate --format json
python -m autarkic_systems.fixed_point_bridge_equality_frontier_status --format json
python -m autarkic_systems.fixed_point_construction_frontier_status --format json
```

The certificate JSON reported `accepted=true`, one certificate, six certificate
steps, bridge equation length 4815, evaluation output length 296, and all six
steps accepted. The bridge frontier JSON reported `accepted=true`, support
count 6, and blocker `bridge-equality-proof`. The aggregate construction
frontier JSON reported `accepted=true`, support count 8, five open construction
cases, five accepted compact case-status rollups, and blocker
`fixed-point-construction`.

The suite index now reports 153 discovered modules: `fast=130`,
`extended-fixed-point=23`, and `all=153`.

Hygiene passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
```

The fast selector passed:

```sh
python -m autarkic_systems.test_suite_selection --suite fast
```

Observed result:

```text
Ran 1188 tests in 274.534s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 130
```

The first extended selector run caught a stale project-status test contract:
`formal_confidence.validation_summary` was present in the live payload but
absent from `FORMAL_CONFIDENCE_PAYLOAD_KEYS`.

```text
Ran 354 tests in 4847.508s
FAILED (failures=3)
manifest: as-test-suite-selection-v1 suite: extended-fixed-point module_count: 23
```

The exact failing project-status assertions passed after adding that key to the
expected contract:

```sh
python -m unittest tests.test_project_status_report.ProjectStatusReportTests.test_status_payload_summarizes_evidence_registries_and_frontier tests.test_project_status_report.ProjectStatusReportTests.test_status_payload_exposes_derived_formal_confidence_validation_summary tests.test_project_status_report.ProjectStatusReportTests.test_json_cli_reports_project_status
```

Observed result:

```text
Ran 3 tests in 173.263s
OK
```

The extended selector then passed:

```sh
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point
```

Observed result:

```text
Ran 354 tests in 4900.538s
OK
manifest: as-test-suite-selection-v1 suite: extended-fixed-point module_count: 23
```

This is a finite certificate support surface only. It does not prove bridge
equality, prove the fixed-point equation, introduce an arithmetized proof
predicate, discharge the fixed-point construction blocker, change
formal-confidence status, or claim self-consistency.
