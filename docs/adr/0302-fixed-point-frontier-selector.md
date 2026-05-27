# ADR-0302: Fixed-Point Frontier Selector

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0301 exposed the five open fixed-point construction proof cases as an
acyclic obligation graph. The graph now identifies two root obligations:
`diagonal-instance-closure` and `substitution-graph-correctness-proof`.

The graph is useful, but operators still need a compact checked surface that
answers: which proof obligations are currently selectable, and which are
deferred because predecessor obligations remain open?

## Decision

Add `autarkic_systems.fixed_point_frontier_selector`, a text/JSON validator for
`claims/fixed_point_frontier_selector.json`.

The selector will load the checked obligation graph, select open root
obligations, and defer every open obligation with at least one open
predecessor. The current selected cases are:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

The current deferred cases are:

- `substitution-representability-proof`;
- `bridge-equality-proof`; and
- `fixed-point-equation-lifting`.

The selector preserves the aggregate frontier blocker
`fixed-point-construction` and all fixed-point non-claims. It does not rank the
two selected root obligations by promise, difficulty, or theorem status.

## Success Criteria

- Red tests fail before implementation because the selector module does not
  exist.
- The checked-in selector validates against the current obligation graph.
- JSON output exposes two selected open root obligations and three deferred
  open obligations with blocking predecessor lists.
- Text output renders the selected/deferred split and non-claims.
- Stale expected selected-case metadata is rejected fail-closed.
- No output claims that any proof obligation, fixed-point equation, proof
  predicate, or self-consistency theorem has been proved.

## Failure Criteria

- A non-root obligation is selected while one of its predecessor obligations
  remains open.
- An open root obligation is omitted from the selected set.
- The aggregate fixed-point construction frontier stops reporting blocked
  status.
- The selector ranks selected roots as mathematical progress claims rather
  than scheduling candidates.
- The slice changes mathematical semantics, project-status semantics, handoff
  behavior, or unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_frontier_selector`.
- Green:
  `python -m unittest tests.test_fixed_point_frontier_selector`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_frontier_selector tests.test_fixed_point_construction_obligation_graph tests.test_fixed_point_construction_frontier_status`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_frontier_selector --format json`.
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
python -m unittest tests.test_fixed_point_frontier_selector
```

It failed as intended before implementation with:

```text
ImportError: cannot import name 'fixed_point_frontier_selector'
```

The implementation adds `autarkic_systems.fixed_point_frontier_selector`,
`claims/fixed_point_frontier_selector.json`, and
`docs/fixed-point-frontier-selector.md`. The selector validates against the
ADR-0301 obligation graph, selects the two open root obligations, defers the
three downstream open obligations, and preserves the aggregate
`fixed-point-construction` blocker.

The first green attempt caught an integration mismatch: the obligation graph
report stores frontier status on its manifest, not as direct report fields. The
selector now reads the existing graph report shape without changing ADR-0301.

Focused selector verification passed:

```sh
python -m unittest tests.test_fixed_point_frontier_selector
```

Observed result:

```text
Ran 6 tests in 89.672s
OK
```

The focused selector/graph/frontier seam passed:

```sh
python -m unittest tests.test_fixed_point_frontier_selector tests.test_fixed_point_construction_obligation_graph tests.test_fixed_point_construction_frontier_status
```

Observed result:

```text
Ran 28 tests in 125.193s
OK
```

Live JSON passed:

```sh
python -m autarkic_systems.fixed_point_frontier_selector --format json
```

The JSON reported `accepted=true`, selected open roots
`diagonal-instance-closure` and `substitution-graph-correctness-proof`, three
deferred downstream open obligations with predecessor blockers, and blocker
`fixed-point-construction`.

The suite index now reports 155 discovered modules: `fast=130`,
`extended-fixed-point=25`, and `all=155`.

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
Ran 1188 tests in 135.551s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 130
```

The extended selector passed:

```sh
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point
```

Observed result:

```text
Ran 366 tests in 2338.976s
OK
manifest: as-test-suite-selection-v1 suite: extended-fixed-point module_count: 25
```

This slice does not change fixed-point construction semantics,
formal-confidence status, project-status semantics, or handoff behavior. It
adds only a checked scheduling selector over the existing open proof-obligation
graph.
