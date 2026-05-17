# Neighbor Delivery Chain Traces

ADR-0082 adds the first recorded transition-chain trace:
`schematics/chains/neighbor_delivery_recipient_chain_trace.json`.
ADR-0092 adds the corresponding non-init rejection trace:
`schematics/chains/neighbor_delivery_rejection_chain_trace.json`.

The first trace records the two-step handoff behind
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`:

1. a stem sender completes `neighbor-b/proc-l-init` command-buffer delivery;
2. the sender output tuple `["_", "proc-l-init", "_"]` is installed as an
   empty recipient's upstream tuple; and
3. the recipient consumes `proc-l-init` through the existing init-family
   command-message transition.

The second trace records the two-step handoff behind
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`:

1. a stem sender completes `neighbor-c/write-buf-one` command-buffer delivery;
2. the sender output tuple `["_", "_", "write-buf-one"]` is installed as an
   empty recipient's upstream tuple; and
3. the recipient rejects `write-buf-one` through the existing non-init
   command-message boundary with chain status `recipient-not-consumed`.

## Validation

`autarkic_systems/chain_trace.py` loads and validates both traces. It checks the
sender step, handoff tuple, recipient step, whole-chain helper replay, and
boundary terms.

Run:

```sh
python -m unittest tests.test_neighbor_delivery_chain_trace
```

The consumed trace is also validated by the composed-chain evidence bundle:

```sh
python -m autarkic_systems.chain_evidence_bundle
```

ADR-0083 adds the renderer-locked SVG view of the consumed trace at
`schematics/chains/neighbor_delivery_recipient_chain_trace.svg`.
ADR-0093 adds the renderer-locked SVG view of the rejection trace at
`schematics/chains/neighbor_delivery_rejection_chain_trace.svg`.

## Boundary

These are trace artifacts, not renderers. They do not add SVG output,
scheduler semantics, graph topology, multi-cell timing, non-init command
execution, `standard-signal` command-token execution, or write-buffer
command-token execution.
