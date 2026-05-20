# Fixed-Point Equation Lifting Frontier Status

ADR-0278 adds a compact status surface for the
`fixed-point-equation-lifting` case in the fixed-point construction map.

The checked manifest is
`claims/fixed_point_equation_lifting_frontier_status.json`; the validator is
`autarkic_systems.fixed_point_equation_lifting_frontier_status`.

The surface loads these current support manifests:

- `claims/fixed_point_construction_cases.json`;
- `claims/fixed_point_targets.json`;
- `claims/fixed_point_equation_bridge_targets.json`;
- `language/formal_codebook.json`; and
- `claims/fixed_point_equation_lifting_alignment.json`.

It requires the construction case with id
`AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING` and kind
`fixed-point-equation-lifting` to remain `proof-case-open`. The frontier
remains `blocked` by `fixed-point-equation-lifting`.

The compact support facts require all four support surfaces to accept, preserve
the support-subject order `fixed_point`, `fixed_point_equation_bridge`,
`codebook`, and `equation_lifting_alignment`, and expose the current
4528-token direct target form and 4815-token bridge equation.

This surface is intentionally non-promotional. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_equation_lifting_frontier_status
python -m autarkic_systems.fixed_point_equation_lifting_frontier_status --format json
```
