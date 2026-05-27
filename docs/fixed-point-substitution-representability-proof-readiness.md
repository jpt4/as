# Fixed-Point Substitution Representability Proof Readiness

ADR-0313 adds
`autarkic_systems.fixed_point_substitution_representability_proof_readiness`, a
compact proof-readiness surface for the
`substitution-representability-proof` construction case.

## Purpose

The readiness surface composes two existing checked inputs:

- `claims/fixed_point_substitution_representability_frontier_status.json`; and
- `claims/fixed_point_substitution_representability_certificate.json`.

The resulting report records that the construction case is certificate-ready,
while the case itself remains `proof-case-open` and the frontier remains
`blocked` by `substitution-representability-proof`.

## Run

```sh
python -m autarkic_systems.fixed_point_substitution_representability_proof_readiness
python -m autarkic_systems.fixed_point_substitution_representability_proof_readiness --format json
```

## Checked Surface

The validator checks the frontier report, certificate report, support-surface
count, single certificate, seven certificate steps, covered predecessor
certificate cases, zero missing predecessor certificates, 296-token witness
output length, and the derived readiness entry for
`AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY`.

## Boundary

This is proof-readiness metadata only. It does not prove substitution
representability, substitution graph correctness, bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.
