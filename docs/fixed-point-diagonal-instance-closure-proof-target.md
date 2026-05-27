# Fixed-Point Diagonal Instance Closure Proof Target

ADR-0319 adds
`autarkic_systems.fixed_point_diagonal_instance_closure_proof_target`, a
blocked proof-closure target for the selected `diagonal-instance-closure`
root obligation.

The validator checks
`claims/fixed_point_diagonal_instance_closure_proof_target.json` against the
diagonal-instance closure certificate, diagonal-instance closure
proof-readiness report, and selected-root proof-readiness coverage report. It
records that the root has accepted finite support and an accepted
certificate-ready/proof-open handoff, while proof closure remains blocked on
three missing proof artifacts:

- formal diagonal-instance closure derivation;
- proof-rule derivation from certificate steps; and
- construction-case promotion rule.

Run it with:

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_target
python -m autarkic_systems.fixed_point_diagonal_instance_closure_proof_target --format json
```

This is not a diagonal-instance closure proof, substitution graph correctness
proof, substitution representability proof, bridge-equality proof, fixed-point
equation proof, fixed-point construction proof, arithmetized proof predicate,
or self-consistency theorem.
