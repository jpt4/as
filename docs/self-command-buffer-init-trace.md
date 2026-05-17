# Self Command Buffer Init Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0039 adds `schematics/self_command_buffer_init_trace.json`, a structured
schematic-linked Universal Cell trace for the self-target init command-buffer
slice implemented in ADR-0037 and named as a claim in ADR-0038.
ADR-0040 adds the rendered SVG view of this trace.

## Trace Boundary

The trace records a stem cell with empty `automail` and `self_mailbox`, a
matching one-hot input/control pair, and a four-bit command buffer
`[0, 0, 1, 0]`. One `step_stem_cell` activation appends bit `1`, producing the
five-bit buffer `00101`. The ADR-0026 map decodes that value as
`self/proc-l-init`, and the transition must:

- return `stem-command-buffer-self-processed`;
- reconfigure the cell to `proc` with `left` memory;
- keep input/output/automail/`self_mailbox` empty after dispatch;
- clear control and buffer state.

This is not full command-buffer execution. It does not cover neighbor routing,
self-target `standard-signal`, write-buffer commands, larger GELC examples, or
physical simulation.

## Schematic Role

The artifact uses the same triangular RLEM/GELC schematic vocabulary as the
earlier single-node, processor, stem automail, stem buffer, and self-mailbox
traces. Its interpretive layers keep symbolic RLEM behavior, GELC geometry, UC
state, and candidate physical implementation distinct.

## Verification

Run:

```sh
python -m unittest tests.test_self_command_buffer_init_trace
```

The tests verify artifact identity, schema vocabulary, recorded decode flow,
execution replay through `step_stem_cell`, PRC witness-map validation, and
drift rejection for wrong target role, uncleared command buffer state, and
changed flow.
