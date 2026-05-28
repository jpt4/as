# Fixed-Point Selected Root Proof Target Coverage

ADR-0321 adds
`autarkic_systems.fixed_point_selected_root_proof_target_coverage`, a compact
coverage surface for the two selected fixed-point construction root proof
targets.

The validator checks
`claims/fixed_point_selected_root_proof_target_coverage.json` against the
selected-root proof-readiness coverage report, the diagonal-instance closure
proof target, and the substitution graph correctness proof target. It records
that both selected roots have accepted blocked proof targets, while neither is
ready for proof closure.

Run it with:

```sh
python -m autarkic_systems.fixed_point_selected_root_proof_target_coverage
python -m autarkic_systems.fixed_point_selected_root_proof_target_coverage --format json
```

This is not a diagonal-instance closure proof, substitution graph correctness
proof, substitution representability proof, bridge-equality proof,
fixed-point equation proof, fixed-point construction proof, arithmetized proof
predicate, or self-consistency theorem.
