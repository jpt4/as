# ADR-0020: Processor Memory Toggle SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0018 added a structured processor memory-toggle trace. ADR-0017 rendered
only the first wire trace as SVG, so the visible schematic layer still lags the
structured trace set. P7 now needs the processor trace to become inspectable
without turning the SVG into a hand-maintained source of truth.

The existing SVG module is deliberately small and wire-trace shaped. The next
step should generalize the renderer enough to support both the wire and
processor traces while preserving exact renderer-output tests for the existing
wire SVG.

## Decision

Add a generated SVG for the processor memory-toggle trace:

- `schematics/processor_memory_toggle_trace.svg` renders
  `schematics/processor_memory_toggle_trace.json`;
- `autarkic_systems/schematic_svg.py` gains generic `render_schematic_svg` and
  `validate_schematic_svg` functions, with the existing single-node wrapper
  retained for compatibility;
- `tests/test_processor_memory_toggle_svg.py` verifies the processor SVG is
  parseable, source-linked, port/layer annotated, records before/after memory,
  displays the left-memory routed flow, and exactly matches renderer output;
- `docs/processor-memory-toggle-svg.md` explains the render boundary.

The processor SVG is a visual view of an already executable trace. It does not
create new processor semantics.

## Success Criteria

- Red tests fail before implementation because the generic SVG renderer or
  processor SVG artifact is absent.
- The committed processor SVG exactly matches renderer output for the processor
  JSON trace.
- The existing wire SVG tests still pass unchanged.
- The SVG exposes artifact ID, trace ID, three ports, four interpretive layers,
  before memory `left`, after memory `right`, transition function, and routed
  signal flow.
- Validation rejects a drifted SVG that disagrees with renderer output.

## Consequences

- P7 gains visible renders for both wire and processor traces.
- The SVG renderer becomes reusable for additional trace artifacts.
- Stem SVG rendering and larger GELC visualization remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_processor_memory_toggle_svg` failed with
  `ImportError: cannot import name 'PROCESSOR_SVG_ARTIFACT'` from
  `autarkic_systems.schematic_svg`.

Green step:

- Added generic `render_schematic_svg` and `validate_schematic_svg` support
  while preserving `render_single_node_schematic_svg` and
  `validate_single_node_schematic_svg`.
- Added `schematics/processor_memory_toggle_trace.svg`.
- Added `docs/processor-memory-toggle-svg.md`.
- `python -m unittest tests.test_processor_memory_toggle_svg
  tests.test_single_node_schematic_svg` passed 14 tests.

Full verification:

- `python -m unittest discover` passed 91 tests.
- `python -m py_compile autarkic_systems/schematic_svg.py
  tests/test_processor_memory_toggle_svg.py` passed.
- `python - <<'PY' ... ET.parse(...) ... PY` passed for
  `schematics/single_node_triangular_rlem_trace.svg` and
  `schematics/processor_memory_toggle_trace.svg`.
- `git diff --check` passed.

Coverage limits:

- This renders one processor memory-toggle trace only.
- It does not render the stem automail trace.
- It does not claim physical circulator verification.
