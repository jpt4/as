# Fixed-Point Bridge Equality Frontier Status

ADR-0276 adds a compact status surface for the fixed-point
`bridge-equality-proof` construction case.

The checked manifest is
`claims/fixed_point_bridge_equality_frontier_status.json`; the validator is
`autarkic_systems.fixed_point_bridge_equality_frontier_status`.

The surface loads the current bridge-equality frontier dependencies:

- `claims/fixed_point_construction_cases.json`;
- `claims/fixed_point_equation_bridge_targets.json`;
- `claims/substitution_representability_targets.json`;
- `claims/substitution_graph_correctness_cases.json`;
- `claims/fixed_point_bridge_equality_alignment.json`; and
- `claims/fixed_point_bridge_equality_evaluation.json`; and
- `claims/fixed_point_bridge_equality_certificate.json`.

It requires the `bridge-equality-proof` construction case to remain
`proof-case-open`. The frontier remains `blocked` by `bridge-equality-proof`.
The compact support facts require the accepted alignment, evaluation, and
certificate surfaces to expose the 4815-token bridge equation, the evaluation
surface to expose the 296-token output, and the certificate surface to expose
one six-step finite certificate support object.

This surface is intentionally non-promotional. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_bridge_equality_frontier_status
python -m autarkic_systems.fixed_point_bridge_equality_frontier_status --format json
```
