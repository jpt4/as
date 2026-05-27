# Fixed-Point Substitution Graph Correctness Proof Target

ADR-0320 adds
`autarkic_systems.fixed_point_substitution_graph_correctness_proof_target`, a
blocked proof-closure target for the selected
`substitution-graph-correctness-proof` root obligation.

The validator checks
`claims/fixed_point_substitution_graph_correctness_proof_target.json` against
the substitution graph correctness certificate, substitution graph correctness
proof-readiness report, and selected-root proof-readiness coverage report. It
records that the root has accepted finite support and an accepted
certificate-ready/proof-open handoff, while proof closure remains blocked on
three missing proof artifacts:

- formal graph-correctness derivation;
- proof-rule derivation from certificate steps; and
- construction-case promotion rule.

Run it with:

```sh
python -m autarkic_systems.fixed_point_substitution_graph_correctness_proof_target
python -m autarkic_systems.fixed_point_substitution_graph_correctness_proof_target --format json
```

This is not a substitution graph correctness proof, bridge-equality proof,
fixed-point equation proof, fixed-point construction proof, arithmetized proof
predicate, or self-consistency theorem.
