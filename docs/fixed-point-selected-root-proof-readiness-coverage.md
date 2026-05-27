# Fixed-Point Selected Root Proof Readiness Coverage

ADR-0318 adds
`autarkic_systems.fixed_point_selected_root_proof_readiness_coverage`, a
focused coverage surface for the two currently selected fixed-point
construction root proof obligations.

The validator checks `claims/fixed_point_selected_root_proof_readiness_coverage.json`
against the fixed-point frontier selector and the two selected-root
proof-readiness reports. It records that the selected roots are
`diagonal-instance-closure` and `substitution-graph-correctness-proof`, both
selected roots have accepted certificate-ready but proof-open readiness
handoffs, and the three downstream construction cases remain deferred.

Run it with:

```sh
python -m autarkic_systems.fixed_point_selected_root_proof_readiness_coverage
python -m autarkic_systems.fixed_point_selected_root_proof_readiness_coverage --format json
```

This is not a diagonal-instance closure proof, substitution graph correctness
proof, substitution representability proof, bridge-equality proof, fixed-point
equation proof, fixed-point construction proof, arithmetized proof predicate,
or self-consistency theorem.
