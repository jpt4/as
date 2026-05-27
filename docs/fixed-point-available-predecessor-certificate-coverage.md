# Fixed-Point Available Predecessor Certificate Coverage

ADR-0308 adds
`autarkic_systems.fixed_point_available_predecessor_certificate_coverage`, a
compact coverage surface for all currently available finite predecessor
certificates feeding deferred fixed-point construction cases.

## Purpose

ADR-0307 records certificate-support gaps using selected-root certificates.
This report widens that view to include the existing bridge-equality finite
certificate. The wider coverage shows that `fixed-point-equation-lifting` has
available finite certificate support for its `bridge-equality-proof`
predecessor while still remaining blocked by the open predecessor proof case.

## Run

```sh
python -m autarkic_systems.fixed_point_available_predecessor_certificate_coverage
python -m autarkic_systems.fixed_point_available_predecessor_certificate_coverage --format json
```

The coverage surface derives from:

- `claims/fixed_point_deferred_case_certificate_readiness.json`;
- `claims/fixed_point_selected_root_certificate_coverage.json`; and
- `claims/fixed_point_bridge_equality_certificate.json`.

## Checked Coverage

The coverage surface requires:

- three deferred coverage entries;
- three available predecessor certificate subjects;
- twenty total available finite certificate steps;
- no missing certificate predecessor for `substitution-representability-proof`;
- `substitution-representability-proof` as the remaining missing certificate
  predecessor for `bridge-equality-proof`; and
- no missing certificate predecessor for `fixed-point-equation-lifting`.

## Boundary

This is available predecessor certificate coverage only. It does not prove
substitution representability, bridge equality, the fixed-point equation, an
arithmetized proof predicate, or self-consistency.
