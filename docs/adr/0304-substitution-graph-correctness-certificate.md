# ADR-0304: Substitution Graph Correctness Certificate

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0302 selected two open root obligations for the current fixed-point
construction frontier:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

ADR-0303 added finite certificate support for the first selected root. The
second selected root already has accepted finite support surfaces: a
substitution graph correctness target, a five-case correctness rollup, and the
fixed-point substitution graph correctness bridge tying those surfaces back to
the construction case. The next slice should expose those facts as one compact
certificate support object without claiming graph correctness has been proved.

## Decision

Add `autarkic_systems.fixed_point_substitution_graph_correctness_certificate`,
a text/JSON validator over
`claims/fixed_point_substitution_graph_correctness_certificate.json`.

The certificate derives one finite support object from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/substitution_graph_correctness_targets.json`;
- `claims/substitution_graph_correctness_cases.json`; and
- `claims/fixed_point_substitution_graph_correctness_bridge.json`.

The certificate records seven checked steps:

- `select-open-root-obligation`;
- `accept-correctness-target`;
- `accept-correctness-case-rollup`;
- `accept-bridge-report`;
- `check-correctness-case-count`;
- `check-finite-dependency-coverage`; and
- `preserve-open-proof-boundary`.

Do not change fixed-point construction semantics, close the
`substitution-graph-correctness-proof` proof case, alter the aggregate frontier
selector, or change project-status/handoff behavior in this slice.

## Success Criteria

- Red tests fail before implementation because the certificate module does not
  exist.
- The checked-in certificate validates against the current selector,
  substitution graph correctness target, correctness case rollup, and
  fixed-point graph-correctness bridge.
- JSON output exposes one accepted finite certificate with seven accepted
  steps.
- Text output renders the selected-root certificate and non-claims.
- Stale expected step metadata is rejected fail-closed.
- No output claims that graph correctness, bridge equality, the fixed-point
  equation, a proof predicate, or self-consistency has been proved.

## Failure Criteria

- The certificate accepts when the selector no longer selects
  `substitution-graph-correctness-proof` as an open root obligation.
- The certificate accepts when the correctness target, correctness case rollup,
  or bridge report rejects.
- The correctness case count or finite dependency coverage drifts but the
  certificate still accepts.
- The slice changes mathematical semantics, project-status semantics, handoff
  behavior, or unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_certificate`.
- Green:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_certificate`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_substitution_graph_correctness_certificate tests.test_fixed_point_substitution_graph_correctness_bridge tests.test_fixed_point_frontier_selector tests.test_substitution_graph_correctness_cases tests.test_substitution_graph_correctness_target`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_substitution_graph_correctness_certificate --format json`.
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
python -m unittest tests.test_fixed_point_substitution_graph_correctness_certificate
```

It failed as intended before implementation with:

```text
ImportError: cannot import name 'fixed_point_substitution_graph_correctness_certificate'
```

The implementation adds
`autarkic_systems.fixed_point_substitution_graph_correctness_certificate`,
`claims/fixed_point_substitution_graph_correctness_certificate.json`, and
`docs/fixed-point-substitution-graph-correctness-certificate.md`. The
validator derives one finite certificate from the accepted frontier selector,
substitution graph correctness target, correctness case rollup, and
fixed-point graph-correctness bridge.

Focused certificate verification passed:

```sh
python -m unittest tests.test_fixed_point_substitution_graph_correctness_certificate
```

Observed result:

```text
Ran 6 tests in 123.202s
OK
```

The first focused seam attempt caught a test-plan naming error:
`tests.test_substitution_graph_correctness` does not exist. The test plan now
uses the checked-in target module,
`tests.test_substitution_graph_correctness_target`.

The corrected certificate/bridge/selector/correctness seam passed:

```sh
python -m unittest tests.test_fixed_point_substitution_graph_correctness_certificate tests.test_fixed_point_substitution_graph_correctness_bridge tests.test_fixed_point_frontier_selector tests.test_substitution_graph_correctness_cases tests.test_substitution_graph_correctness_target
```

Observed result:

```text
Ran 47 tests in 214.501s
OK
```

The live JSON validator accepted one seven-step finite certificate:

```sh
python -m autarkic_systems.fixed_point_substitution_graph_correctness_certificate --format json
```

Observed result:

```text
accepted=true
certificate_count=1
certificate_step_count=7
observed_correctness_case_count=5
observed_finite_dependency_count=5
observed_selector_accepts_root=true
observed_correctness_target_accepted=true
observed_correctness_cases_accepted=true
observed_bridge_report_accepted=true
observed_bridge_links_construction_case=true
observed_proof_boundary_preserved=true
failed_subjects=[]
```

The suite index listed 157 discovered modules, with 130 fast modules, 27
extended fixed-point modules, and 157 all-suite modules:

```sh
python -m autarkic_systems.test_suite_selection --list-suites --format json
```

The fast suite passed:

```sh
python -m autarkic_systems.test_suite_selection --suite fast
```

Observed result:

```text
Ran 1188 tests in 146.035s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 130
```

The extended fixed-point suite passed:

```sh
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point
```

Observed result:

```text
Ran 378 tests in 2502.146s
OK
manifest: as-test-suite-selection-v1 suite: extended-fixed-point module_count: 27
```

Hygiene checks passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
```

This slice remains finite certificate support only. It does not close the
`substitution-graph-correctness-proof` proof case, prove bridge equality,
prove the fixed-point equation, introduce an arithmetized proof predicate, or
claim self-consistency.
