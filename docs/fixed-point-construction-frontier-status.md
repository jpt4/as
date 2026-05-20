# Fixed-Point Construction Frontier Status

ADR-0273 adds a compact status surface for the post-ADR-0270 fixed-point
construction stack. ADR-0285 extends that aggregate status with a compact
construction-case status rollup.

The checked manifest is
`claims/fixed_point_construction_frontier_status.json`; the validator is
`autarkic_systems.fixed_point_construction_frontier_status`.

The surface loads the current construction/frontier dependencies:

- `claims/fixed_point_construction_cases.json`;
- `claims/fixed_point_diagonal_instance_candidate_surface.json`;
- `claims/fixed_point_substitution_witness_bridge.json`;
- `claims/fixed_point_substitution_graph_correctness_bridge.json`;
- `claims/fixed_point_bridge_equality_alignment.json`;
- `claims/fixed_point_bridge_equality_evaluation.json`; and
- `claims/fixed_point_equation_lifting_alignment.json`.

It also loads the compact status handoffs for the five construction cases:

- `claims/fixed_point_diagonal_instance_closure_frontier_status.json`;
- `claims/fixed_point_substitution_representability_frontier_status.json`;
- `claims/substitution_graph_correctness_frontier_status.json`;
- `claims/fixed_point_bridge_equality_frontier_status.json`; and
- `claims/fixed_point_equation_lifting_frontier_status.json`.

It reports per-case finite support and the compact construction-case status
rollup, requiring all five construction cases to remain `proof-case-open`.
The aggregate frontier remains `blocked` by `fixed-point-construction`. The
substitution graph correctness construction case intentionally rolls up the
compact status blocked by `substitution-graph-correctness`, not by the
construction case kind `substitution-graph-correctness-proof`.

This surface is intentionally non-promotional. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_construction_frontier_status
python -m autarkic_systems.fixed_point_construction_frontier_status --format json
```
