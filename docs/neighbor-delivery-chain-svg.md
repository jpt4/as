# Neighbor Delivery Chain SVGs

ADR-0083 adds the first rendered view of a composed transition-chain trace:
`schematics/chains/neighbor_delivery_recipient_chain_trace.svg`.
ADR-0093 adds the rendered view of the rejection trace:
`schematics/chains/neighbor_delivery_rejection_chain_trace.svg`.

The consumed SVG is generated from
`schematics/chains/neighbor_delivery_recipient_chain_trace.json` by
`autarkic_systems/chain_svg.py`. The checked-in SVG must exactly match the
renderer output, so the visual cannot drift away from the chain trace.
The rejection SVG is generated from
`schematics/chains/neighbor_delivery_rejection_chain_trace.json` by the same
renderer.

## View

The consumed view exposes:

- sender step `sender-neighbor-delivery`;
- recipient step `recipient-init-consumption`;
- whole-chain status `neighbor-delivery-consumed`;
- handoff `sender output[1] -> recipient upstream[1]`;
- delivered tuple `[_, proc-l-init, _]`;
- sender routed signal flow; and
- recipient routed signal flow.

The rejection view exposes the same layers for
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`, including the
`recipient-not-consumed` status, handoff `sender output[2] -> recipient
upstream[2]`, delivered tuple `[_, _, write-buf-one]`, and recipient
`rejected-input` step.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_svg
python -m autarkic_systems.chain_evidence_bundle
```

The SVG validator parses XML metadata, checks exact renderer output, checks
visible sender/recipient/status/tuple labels, and checks that the handoff and
both step flows are visible.

## Boundary

These are two-cell visuals for the current recorded chains. They are not a
general graph renderer and do not add scheduler, topology, multi-cell timing,
non-init command execution, `standard-signal` command-token execution, or
write-buffer command-token execution.
