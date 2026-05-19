# Fixed-Point Substitution Graph Correctness Bridge

Status: finite graph-correctness dependency coverage, not a correctness proof,
2026-05-19.

ADR-0266 adds
`claims/fixed_point_substitution_graph_correctness_bridge.json` and
`autarkic_systems/fixed_point_substitution_graph_correctness_bridge.py`. The
surface checks the third fixed-point construction proof case against the
current substitution graph correctness target, correctness case map, and five
finite graph-domain dependency surfaces.

## Purpose

ADR-0263 made `substitution-graph-correctness-proof` the third open
construction case. ADR-0266 narrows that case from broad dependency names to a
finite checked bridge over the graph correctness case map.

The verifier derives the current graph-correctness bridge and checks that:

- the fixed-point construction case remains open;
- the construction case requires the graph correctness target, graph
  correctness case map, and graph-correctness bridge;
- the graph correctness target and case map remain accepted;
- all five correctness case kinds are present;
- all five finite graph-domain dependencies remain accepted; and
- the diagonal-witness composition links the current fixed-point target to the
  current graph correctness target.

## Run

```sh
python -m autarkic_systems.fixed_point_substitution_graph_correctness_bridge
python -m autarkic_systems.fixed_point_substitution_graph_correctness_bridge --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the construction-case, substitution graph correctness target, correctness
  case map, codebook-roundtrip, quotation-term-closure,
  meta-substitution-semantics, formula-schema-relation, and
  diagonal-witness-composition dependencies remain accepted;
- exactly one graph-correctness bridge point is derived;
- the correctness case count is five;
- all required finite dependency subjects are accepted; and
- future work and non-claims remain explicit.

## Boundary

This is not a substitution graph correctness proof, not a bridge equality
proof, not a fixed-point equation proof, not an arithmetized proof predicate,
and not a self-consistency theorem. The formal-confidence target remains
blocked on `fixed-point-construction`.
