# Fixed-Point Diagonal Instance Closure Certificate

ADR-0303 adds
`autarkic_systems.fixed_point_diagonal_instance_closure_certificate`, a compact
finite certificate support surface for the selected
`diagonal-instance-closure` root obligation.

## Purpose

The frontier selector identifies `diagonal-instance-closure` as one of the two
currently selectable open root obligations. Existing closure and candidate
reports already check the relevant finite syntax facts. This certificate ties
those reports together so the selected root has one concise support object.

## Run

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_closure_certificate
python -m autarkic_systems.fixed_point_diagonal_instance_closure_certificate --format json
```

The certificate derives from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/fixed_point_diagonal_instance_closure.json`; and
- `claims/fixed_point_diagonal_instance_candidate_surface.json`.

## Checked Steps

The certificate records seven finite checks:

- `select-open-root-obligation`;
- `accept-closure-report`;
- `accept-candidate-surface`;
- `check-closed-diagonal-instance`;
- `check-codebook-roundtrip`;
- `match-candidate-to-closure`; and
- `preserve-open-proof-boundary`.

## Boundary

This is certificate support only. It does not prove substitution
representability, substitution graph correctness, bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.
