# Fixed-Point Diagonal Instance Closure Frontier Status

ADR-0277 adds a compact status surface for the
`diagonal-instance-closure` case in the fixed-point construction map.

The checked manifest is
`claims/fixed_point_diagonal_instance_closure_frontier_status.json`; the
validator is
`autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status`.

The surface loads these current support manifests:

- `claims/fixed_point_construction_cases.json`;
- `claims/fixed_point_targets.json`;
- `claims/diagonal_construction_targets.json`;
- `claims/fixed_point_equation_bridge_targets.json`;
- `claims/fixed_point_diagonal_instance_closure.json`; and
- `claims/fixed_point_diagonal_instance_candidate_surface.json`.

It requires the construction case
`AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE` with kind
`diagonal-instance-closure` to remain `proof-case-open`. The frontier remains
`blocked` by `diagonal-instance-closure`. The compact support facts require
one fixed-point target, one diagonal construction, one bridge target, one
closure point, one candidate surface, and the 296-token diagonal-instance
length.

This surface is intentionally non-promotional. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status
python -m autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status --format json
```
