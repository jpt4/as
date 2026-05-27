# Fixed-Point Expanded Available Predecessor Certificate Coverage

ADR-0310 adds
`autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage`,
an expanded coverage surface for currently available finite predecessor
certificates feeding deferred fixed-point construction cases.

## Purpose

ADR-0308 recorded available predecessor certificate coverage before the
substitution-representability certificate existed. ADR-0309 then added that
certificate support. This report composes both surfaces so downstream
certificate-support visibility reflects the newly available
`substitution-representability-proof` certificate without promoting any proof
case.

## Run

```sh
python -m autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage
python -m autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage --format json
```

The coverage surface derives from:

- `claims/fixed_point_available_predecessor_certificate_coverage.json`; and
- `claims/fixed_point_substitution_representability_certificate.json`.

## Checked Coverage

The expanded coverage surface requires:

- three deferred coverage entries;
- four available predecessor certificate subjects;
- twenty-seven total available finite certificate steps;
- no missing certificate predecessor for `substitution-representability-proof`;
- no missing certificate predecessor for `bridge-equality-proof`; and
- no missing certificate predecessor for `fixed-point-equation-lifting`.

## Boundary

This is expanded available predecessor certificate coverage only. It does not
prove substitution representability, substitution graph correctness, bridge
equality, the fixed-point equation, an arithmetized proof predicate, or
self-consistency.
