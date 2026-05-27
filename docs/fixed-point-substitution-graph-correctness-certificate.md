# Fixed-Point Substitution Graph Correctness Certificate

ADR-0304 adds
`autarkic_systems.fixed_point_substitution_graph_correctness_certificate`, a
compact finite certificate support surface for the selected
`substitution-graph-correctness-proof` root obligation.

## Purpose

The frontier selector identifies `substitution-graph-correctness-proof` as one
of the two currently selectable open root obligations. Existing target, case,
and bridge reports already check the relevant finite graph-correctness support
facts. This certificate ties those reports together so the selected root has
one concise support object.

## Run

```sh
python -m autarkic_systems.fixed_point_substitution_graph_correctness_certificate
python -m autarkic_systems.fixed_point_substitution_graph_correctness_certificate --format json
```

The certificate derives from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/substitution_graph_correctness_targets.json`;
- `claims/substitution_graph_correctness_cases.json`; and
- `claims/fixed_point_substitution_graph_correctness_bridge.json`.

## Checked Steps

The certificate records seven finite checks:

- `select-open-root-obligation`;
- `accept-correctness-target`;
- `accept-correctness-case-rollup`;
- `accept-bridge-report`;
- `check-correctness-case-count`;
- `check-finite-dependency-coverage`; and
- `preserve-open-proof-boundary`.

## Boundary

This is certificate support only. It does not prove substitution graph
correctness, bridge equality, the fixed-point equation, an arithmetized proof
predicate, or self-consistency.
