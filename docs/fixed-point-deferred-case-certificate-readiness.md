# Fixed-Point Deferred Case Certificate Readiness

ADR-0306 adds
`autarkic_systems.fixed_point_deferred_case_certificate_readiness`, a compact
readiness surface for the fixed-point construction proof cases that the
frontier selector currently defers.

## Purpose

The frontier selector defers `substitution-representability-proof`,
`bridge-equality-proof`, and `fixed-point-equation-lifting` because their
predecessor proof cases remain open. ADR-0305 confirms that the two selected
root obligations have accepted finite certificate support. This readiness
report shows how that certificate support reaches the deferred cases without
promoting any deferred case to a proof.

## Run

```sh
python -m autarkic_systems.fixed_point_deferred_case_certificate_readiness
python -m autarkic_systems.fixed_point_deferred_case_certificate_readiness --format json
```

The readiness surface derives from:

- `claims/fixed_point_construction_obligation_graph.json`;
- `claims/fixed_point_frontier_selector.json`; and
- `claims/fixed_point_selected_root_certificate_coverage.json`.

## Checked Readiness

The readiness surface requires:

- three deferred downstream construction cases;
- predecessor counts matching the checked obligation graph;
- selected-root certificate coverage for the two root predecessors where those
  roots feed a deferred case; and
- open predecessor proof cases to continue blocking promotion.

## Boundary

This is deferred-case readiness only. It does not prove substitution
representability, bridge equality, the fixed-point equation, an arithmetized
proof predicate, or self-consistency.
