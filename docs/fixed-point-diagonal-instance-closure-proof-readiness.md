# Fixed-Point Diagonal Instance Closure Proof Readiness

ADR-0312 adds
`autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness`, a
compact proof-readiness surface for the selected
`diagonal-instance-closure` root obligation.

## Purpose

The readiness surface composes two existing checked inputs:

- `claims/fixed_point_diagonal_instance_closure_frontier_status.json`; and
- `claims/fixed_point_diagonal_instance_closure_certificate.json`.

The resulting report records that the root construction case is
certificate-ready, while the case itself remains `proof-case-open` and the
frontier remains `blocked` by `diagonal-instance-closure`.

## Run

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness
python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness --format json
```

## Checked Surface

The validator checks the frontier report, certificate report, support-surface
count, single certificate, seven certificate steps, 296-token diagonal-instance
length, and the derived readiness entry for
`AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE`.

## Boundary

This is proof-readiness metadata only. It does not prove diagonal-instance
closure, substitution representability, substitution graph correctness, bridge
equality, the fixed-point equation, an arithmetized proof predicate, or
self-consistency.
