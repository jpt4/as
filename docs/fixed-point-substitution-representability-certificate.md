# Fixed-Point Substitution Representability Certificate

ADR-0309 adds
`autarkic_systems.fixed_point_substitution_representability_certificate`, a
finite certificate support surface for the open
`substitution-representability-proof` construction case.

## Purpose

ADR-0308 shows that `substitution-representability-proof` has available
predecessor certificate coverage for `diagonal-instance-closure` and
`substitution-graph-correctness-proof`. This report composes that predecessor
coverage with the existing substitution-representability frontier status,
which already records five accepted finite support surfaces for the still-open
case.

## Run

```sh
python -m autarkic_systems.fixed_point_substitution_representability_certificate
python -m autarkic_systems.fixed_point_substitution_representability_certificate --format json
```

The certificate derives from:

- `claims/fixed_point_substitution_representability_frontier_status.json`; and
- `claims/fixed_point_available_predecessor_certificate_coverage.json`.

## Checked Certificate

The certificate surface requires:

- one certificate support object;
- seven checked certificate steps;
- the open `substitution-representability-proof` construction case;
- two covered predecessor certificate subjects;
- no missing predecessor certificate support;
- five accepted frontier support surfaces; and
- the checked 296-token witness output code length.

## Boundary

This is finite certificate support only. It does not prove substitution
representability, substitution graph correctness, bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.
