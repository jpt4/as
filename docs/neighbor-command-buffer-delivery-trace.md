# Neighbor Command Buffer Delivery Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0046 adds `schematics/neighbor_command_buffer_delivery_trace.json`, a
structured schematic-linked Universal Cell trace for the neighbor delivery
behavior implemented in ADR-0044 and named as a claim in ADR-0045.
ADR-0076 registers this trace in the integrated evidence-bundle surface.

## Trace Boundary

The trace records a stem cell with empty `automail` and `self_mailbox`, a
matching one-hot input/control pair, and a four-bit command buffer
`[1, 0, 1, 0]`. One `step_stem_cell` activation appends bit `1`, producing the
five-bit buffer `10101`. The ADR-0026 map decodes that value as
`neighbor-b/proc-l-init`, and the transition must:

- return `stem-command-buffer-neighbor-delivered`;
- keep the cell in the `stem` role with `right` memory;
- preserve upstream state;
- clear consumed input, control, and buffer;
- keep automail and `self_mailbox` empty;
- place `proc-l-init` on output channel 1 only.

This does not execute the delivered command token on a neighbor. It does not
cover recipient-side command-message consumption, rendered SVG output,
self-target non-init execution, larger GELC examples, or physical simulation.

## Schematic Role

The artifact uses the same triangular RLEM/GELC schematic vocabulary as the
earlier single-node, processor, stem automail, stem buffer, self-mailbox, self
command-buffer, and unsupported command-buffer traces. Its interpretive layers
keep symbolic RLEM behavior, GELC geometry, UC state, and candidate physical
implementation distinct.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_command_buffer_delivery_trace
```

The tests verify artifact identity, schema vocabulary, recorded decode flow,
execution replay through `step_stem_cell`, PRC witness-map validation, and
drift rejection for wrong output channels, uncleared command state, and changed
flow.
