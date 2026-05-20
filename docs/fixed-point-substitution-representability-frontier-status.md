# Fixed-Point Substitution Representability Frontier Status

ADR-0275 adds a compact status surface for the
`substitution-representability-proof` case in the fixed-point construction
map.

The checked manifest is
`claims/fixed_point_substitution_representability_frontier_status.json`; the
validator is
`autarkic_systems.fixed_point_substitution_representability_frontier_status`.

The surface loads these current support manifests:

- `claims/fixed_point_construction_cases.json`;
- `claims/substitution_representability_targets.json`;
- `claims/substitution_graph_correctness_cases.json`;
- `claims/fixed_point_equation_bridge_targets.json`; and
- `claims/fixed_point_substitution_witness_bridge.json`.

It requires the construction case with kind
`substitution-representability-proof` to remain `proof-case-open`. The
frontier remains `blocked` by `substitution-representability-proof`.

This surface is intentionally non-promotional. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_substitution_representability_frontier_status
python -m autarkic_systems.fixed_point_substitution_representability_frontier_status --format json
```
