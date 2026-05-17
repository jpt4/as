# Processor Memory Toggle Trace

Status: second schematic-linked Universal Cell trace, 2026-05-17.

This artifact adds processor behavior to the P7 schematic evidence path. The
first schematic trace covered a wire cell with right memory. This one covers a
processor cell with left memory, using the same triangular RLEM/Universal Cell
schema and replaying the recorded transition through the existing
`step_fixed_cell` implementation.

The structured artifact lives in
`schematics/processor_memory_toggle_trace.json`. ADR-0020 renders the same trace
as `schematics/processor_memory_toggle_trace.svg`.

## Trace Shape

The processor starts with:

```json
{
  "role": "proc",
  "memory": "left",
  "input": [1, 0, 0],
  "output": ["_", "_", "_"]
}
```

The left-memory routing flow is:

```text
input[1] -> output[0]
input[2] -> output[1]
input[0] -> output[2]
```

Running that cell through `step_fixed_cell` produces status `routed`, output
`[0, 0, 1]`, input cleared, and memory toggled from `left` to `right`.

## Boundary

This is a schematic-linked witness for behavior AS already implements. It does
not introduce new processor semantics, simulate circulator physics, or address
stem automail. ADR-0020 covers the separate processor SVG render.

## Verification

Run:

```sh
python -m unittest tests.test_processor_memory_toggle_trace
```

The test validates schema reuse, processor role and memory toggle, left-memory
signal flow, PRC witness references, and replay through the existing Universal
Cell probe.
