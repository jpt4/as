# Fixed-Point Frontier Selector

ADR-0302 adds `autarkic_systems.fixed_point_frontier_selector`, a compact
selector over the checked fixed-point construction obligation graph.

## Purpose

The selector answers a narrow scheduling question:

Which open fixed-point construction proof obligations are currently root
obligations, and which open obligations remain deferred because predecessor
obligations are still open?

It is not a proof surface. It preserves the aggregate blocker
`fixed-point-construction`.

## Run

```sh
python -m autarkic_systems.fixed_point_frontier_selector
python -m autarkic_systems.fixed_point_frontier_selector --format json
```

The selector derives its result from
`claims/fixed_point_construction_obligation_graph.json`.

## Current Selection

The selected open root obligations are:

- `diagonal-instance-closure`; and
- `substitution-graph-correctness-proof`.

The deferred open obligations are:

- `substitution-representability-proof`;
- `bridge-equality-proof`; and
- `fixed-point-equation-lifting`.

The selector does not rank the two selected root obligations by theorem
promise, difficulty, or confidence. It only records that neither currently has
an open predecessor in the checked obligation graph.

## Boundary

This is a scheduling surface only. It does not prove substitution
representability, substitution graph correctness, bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.
