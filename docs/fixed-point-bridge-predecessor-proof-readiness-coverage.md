# Fixed-Point Bridge Predecessor Proof Readiness Coverage

ADR-0315 adds a compact aggregate handoff for the three predecessor proof
blockers named by the bridge-equality proof-readiness surface.

The checked surface composes:

- `claims/fixed_point_bridge_equality_proof_closure_readiness.json`;
- `claims/fixed_point_diagonal_instance_closure_proof_readiness.json`;
- `claims/fixed_point_substitution_representability_proof_readiness.json`; and
- `claims/fixed_point_substitution_graph_correctness_proof_readiness.json`.

The report accepts only when the bridge-equality open proof blocker list is
covered exactly by the three accepted predecessor readiness handoffs. Each
predecessor remains certificate-ready but proof-open, and bridge equality
remains `blocked-certificate-ready-proof-open`.

This is coverage metadata, not a theorem. It does not prove diagonal-instance
closure, substitution representability, substitution graph correctness, bridge
equality, the fixed-point equation, an arithmetized proof predicate, or
self-consistency.

Run it with:

```bash
python -m autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage
python -m autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage --format json
```
