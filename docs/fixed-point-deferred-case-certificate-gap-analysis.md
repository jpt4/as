# Fixed-Point Deferred Case Certificate Gap Analysis

ADR-0307 adds
`autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis`, a compact
gap-analysis surface over deferred fixed-point construction cases.

## Purpose

ADR-0306 shows which deferred cases have predecessor certificate coverage from
the selected fixed-point root obligations. This report separates missing
certificate-support predecessors from open proof blockers so later work can
prioritize the next certificate-support surfaces without promoting any
downstream proof case.

## Run

```sh
python -m autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis
python -m autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis --format json
```

The gap analysis derives from:

- `claims/fixed_point_deferred_case_certificate_readiness.json`.

## Checked Gaps

The gap analysis requires:

- three deferred gap entries;
- no certificate-support gap for `substitution-representability-proof`;
- `substitution-representability-proof` as the missing certificate predecessor
  for `bridge-equality-proof`;
- `bridge-equality-proof` as the missing certificate predecessor for
  `fixed-point-equation-lifting`; and
- open proof blockers preserved for every deferred case.

## Boundary

This is certificate gap analysis only. It does not prove substitution
representability, bridge equality, the fixed-point equation, an arithmetized
proof predicate, or self-consistency.
