# Fixed-Point Selected Root Certificate Coverage

ADR-0305 adds
`autarkic_systems.fixed_point_selected_root_certificate_coverage`, a compact
coverage surface for the finite certificates attached to the two selected
fixed-point construction root obligations.

## Purpose

The frontier selector currently selects `diagonal-instance-closure` and
`substitution-graph-correctness-proof` as open root obligations. ADR-0303 and
ADR-0304 give each selected root its own finite certificate support surface.
This coverage report checks that both selected roots are covered by accepted
certificate support while keeping the construction proof cases open.

## Run

```sh
python -m autarkic_systems.fixed_point_selected_root_certificate_coverage
python -m autarkic_systems.fixed_point_selected_root_certificate_coverage --format json
```

The coverage surface derives from:

- `claims/fixed_point_frontier_selector.json`;
- `claims/fixed_point_diagonal_instance_closure_certificate.json`; and
- `claims/fixed_point_substitution_graph_correctness_certificate.json`.

## Checked Coverage

The coverage surface requires:

- two selected root obligations;
- two accepted finite certificate support reports;
- fourteen total checked certificate steps; and
- three deferred downstream construction cases with predecessor blockers.

## Boundary

This is certificate coverage only. It does not prove diagonal-instance
closure, substitution graph correctness, substitution representability, bridge
equality, the fixed-point equation, an arithmetized proof predicate, or
self-consistency.
