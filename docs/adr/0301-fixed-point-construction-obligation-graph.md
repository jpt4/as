# ADR-0301: Fixed-Point Construction Obligation Graph

Date: 2026-05-27

## Status

Accepted.

## Context

ADR-0300 added finite certificate support for the bridge-equality construction
case and fed that support into the aggregate fixed-point construction frontier.
The frontier is still correctly blocked by `fixed-point-construction`, with
five open construction cases.

The current status surfaces say which cases are open and which finite support
surfaces exist. They do not yet expose a compact dependency graph showing which
open proof obligations feed later obligations. That makes the frontier harder
to schedule without rereading the larger case manifests.

## Decision

Add `autarkic_systems.fixed_point_construction_obligation_graph`, a checked
text/JSON surface over `claims/fixed_point_construction_obligation_graph.json`.

The graph has one node for each open construction case and six directed
dependency edges:

- `diagonal-instance-closure -> substitution-representability-proof`;
- `diagonal-instance-closure -> bridge-equality-proof`;
- `substitution-graph-correctness-proof -> substitution-representability-proof`;
- `substitution-representability-proof -> bridge-equality-proof`;
- `substitution-graph-correctness-proof -> bridge-equality-proof`; and
- `bridge-equality-proof -> fixed-point-equation-lifting`.

The validator derives nodes from the existing construction-case manifest,
cross-checks the aggregate frontier status, rejects stale edges, checks that
the graph is acyclic, and preserves the non-claims already used by the
fixed-point frontier.

Do not change fixed-point construction semantics, discharge any proof case,
change formal-confidence status, or alter the project-status/handoff surfaces
in this slice.

## Success Criteria

- Red tests fail before implementation because the obligation-graph module does
  not exist.
- The checked-in graph validates against the current construction cases and
  aggregate construction frontier.
- JSON output exposes five nodes, six edges, two root cases
  `diagonal-instance-closure` and `substitution-graph-correctness-proof`, and
  one terminal case
  `fixed-point-equation-lifting`.
- Text output renders the blocked frontier, root/terminal cases, edges, and
  non-claims.
- Stale edge metadata is rejected fail-closed.
- No output claims that any proof obligation, fixed-point equation, proof
  predicate, or self-consistency theorem has been proved.

## Failure Criteria

- The graph includes a node that is not an open construction case.
- An edge references an unknown case kind.
- The graph becomes cyclic.
- The aggregate fixed-point construction frontier stops reporting blocked
  status.
- The slice changes mathematical semantics, project-status semantics, handoff
  behavior, or unrelated suite-selection behavior.

## Test Plan

- Red:
  `python -m unittest tests.test_fixed_point_construction_obligation_graph`.
- Green:
  `python -m unittest tests.test_fixed_point_construction_obligation_graph`.
- Focused seam:
  `python -m unittest tests.test_fixed_point_construction_obligation_graph tests.test_fixed_point_construction_cases tests.test_fixed_point_construction_frontier_status`.
- Live JSON:
  `python -m autarkic_systems.fixed_point_construction_obligation_graph --format json`.
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
python -m unittest tests.test_fixed_point_construction_obligation_graph
```

It failed as intended before implementation with:

```text
ImportError: cannot import name 'fixed_point_construction_obligation_graph'
```

The implementation adds
`autarkic_systems.fixed_point_construction_obligation_graph`,
`claims/fixed_point_construction_obligation_graph.json`, and
`docs/fixed-point-construction-obligation-graph.md`. The validator derives five
open obligation nodes from the existing construction-case manifest,
cross-checks the aggregate construction frontier, rejects stale edge metadata,
and verifies that the obligation graph is acyclic.

Focused graph verification passed:

```sh
python -m unittest tests.test_fixed_point_construction_obligation_graph
```

Observed result:

```text
Ran 6 tests in 99.063s
OK
```

The focused graph/cases/frontier seam passed:

```sh
python -m unittest tests.test_fixed_point_construction_obligation_graph tests.test_fixed_point_construction_cases tests.test_fixed_point_construction_frontier_status
```

Observed result:

```text
Ran 35 tests in 573.689s
OK
```

Live JSON passed:

```sh
python -m autarkic_systems.fixed_point_construction_obligation_graph --format json
```

The JSON reported `accepted=true`, five open nodes, six edges,
`acyclic=true`, root cases `diagonal-instance-closure` and
`substitution-graph-correctness-proof`, terminal case
`fixed-point-equation-lifting`, and blocker `fixed-point-construction`.

The suite index now reports 154 discovered modules: `fast=130`,
`extended-fixed-point=24`, and `all=154`.

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
Ran 1188 tests in 133.398s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 130
```

The extended selector passed:

```sh
python -m autarkic_systems.test_suite_selection --suite extended-fixed-point
```

Observed result:

```text
Ran 360 tests in 2320.644s
OK
manifest: as-test-suite-selection-v1 suite: extended-fixed-point module_count: 24
```

This slice does not change fixed-point construction semantics,
formal-confidence status, project-status semantics, or handoff behavior. It
adds only a checked obligation-routing graph over the existing open
construction cases.
