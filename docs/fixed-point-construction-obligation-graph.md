# Fixed-Point Construction Obligation Graph

ADR-0301 adds `autarkic_systems.fixed_point_construction_obligation_graph`, a
compact dependency graph over the five open fixed-point construction proof
cases.

## Purpose

The aggregate fixed-point construction frontier already reports that all five
construction cases remain open and that the blocker remains
`fixed-point-construction`. This graph preserves that boundary while making the
case ordering explicit for later proof-frontier work.

## Run

```sh
python -m autarkic_systems.fixed_point_construction_obligation_graph
python -m autarkic_systems.fixed_point_construction_obligation_graph --format json
```

The report derives nodes from
`claims/fixed_point_construction_cases.json` and cross-checks
`claims/fixed_point_construction_frontier_status.json`.

## Graph

The checked graph has five nodes:

- `diagonal-instance-closure`;
- `substitution-graph-correctness-proof`;
- `substitution-representability-proof`;
- `bridge-equality-proof`; and
- `fixed-point-equation-lifting`.

It has six directed dependency edges:

- `diagonal-instance-closure -> substitution-representability-proof`;
- `diagonal-instance-closure -> bridge-equality-proof`;
- `substitution-graph-correctness-proof -> substitution-representability-proof`;
- `substitution-representability-proof -> bridge-equality-proof`;
- `substitution-graph-correctness-proof -> bridge-equality-proof`; and
- `bridge-equality-proof -> fixed-point-equation-lifting`.

The root obligations are `diagonal-instance-closure` and
`substitution-graph-correctness-proof`. The terminal obligation is
`fixed-point-equation-lifting`.

## Boundary

This is an obligation-routing surface only. It does not prove substitution
representability, substitution graph correctness, bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.
