# ADR-0016: Single-Node Schematic Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0015 established the PRC hardware witness map and selected the next
artifact:

`single-node-triangular-rlem-schematic-and-uc-transition-trace`

The project now needs a first concrete schematic/simulation bridge, but the
artifact must remain small enough to audit. A full GELC circuit, 3-D lattice, or
circulator physics simulation would be premature. The next artifact should
instead make one triangular RLEM/Universal Cell node inspectable and connect it
to one already tested AS Universal Cell transition.

## Decision

Add a structured single-node schematic trace:

- `schematics/single_node_triangular_rlem_trace.json` records one triangular
  RLEM/Universal Cell node, its three oriented ports, its four interpretive
  layers, and one executable UC transition trace;
- `autarkic_systems/schematic_trace.py` loads and validates the artifact against
  ADR-0015's witness map and the existing Universal Cell transition code;
- `tests/test_single_node_schematic_trace.py` verifies the required schematic
  vocabulary, witness references, field coverage, and executable trace result;
- `docs/single-node-schematic-trace.md` explains the artifact in human terms.

The first trace uses a fixed-role wire cell. This keeps the behavior tied to
already accepted Universal Cell code while still forcing the schematic layer to
name ports, memory direction, routing, state fields, and candidate physical
interpretation explicitly.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.schematic_trace` and the schematic artifact are absent.
- The artifact ID matches ADR-0015's recommended next artifact.
- The schematic names exactly three oriented ports.
- The schematic distinguishes symbolic RLEM behavior, GELC geometry, UC state,
  and candidate physical implementation layers.
- The trace maps every current AS `Cell` field: role, memory, upstream, input,
  output, automail, control, and buffer.
- The trace is executable through the existing AS Universal Cell transition
  function, and the recorded result matches the computed result.
- The artifact cites the PRC hardware witness IDs it depends on.

## Consequences

- P7 advances from a source map to the first concrete schematic-linked
  execution trace.
- The artifact remains intentionally smaller than a hardware simulator.
- Later work can add SVG rendering, larger GELC examples, or physical
  circulator simulation without changing this trace's acceptance contract.

## After Action Report

Red step:

- `python -m unittest tests.test_single_node_schematic_trace` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.schematic_trace'`.

Green step:

- Added `autarkic_systems/schematic_trace.py`.
- Added `schematics/single_node_triangular_rlem_trace.json`.
- Added `docs/single-node-schematic-trace.md`.
- `python -m unittest tests.test_single_node_schematic_trace` passed 8 tests.

Full verification:

- `python -m unittest tests.test_single_node_schematic_trace` passed 8 tests.
- `python -m unittest discover` passed 62 tests.
- `python -m py_compile autarkic_systems/schematic_trace.py
  tests/test_single_node_schematic_trace.py` passed.
- `jq -e . schematics/single_node_triangular_rlem_trace.json` passed.
- `git diff --check` passed.

Coverage limits:

- This slice is a structured schematic key and one trace, not a full circuit
  design.
- It does not verify circulator physics; the physical layer remains an explicit
  candidate hypothesis.
- It exercises one fixed-role wire transition only. Processor toggling, stem
  automail, larger GELC circuits, and dynamic reconfiguration remain separate
  ADRs.
