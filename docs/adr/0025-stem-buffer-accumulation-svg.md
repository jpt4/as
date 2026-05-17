# ADR-0025: Stem Buffer Accumulation SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0024 added a structured schematic-linked trace for one matching-input stem
buffer append. The JSON trace is executable and source-backed, but the visible
SVG layer still covers only the wire, processor, and automail stem traces.

The existing generic SVG renderer would render the stem buffer trace as a
generic stem node with the routed flow text. That is not enough: the
human-facing view must expose the command-buffer facts that make this trace
different from automail reconfiguration: active control rail, buffer before,
buffer after, and cleared input.

## Decision

Add a generated SVG for the stem buffer accumulation trace:

- `schematics/stem_buffer_accumulation_trace.svg` renders
  `schematics/stem_buffer_accumulation_trace.json`;
- `autarkic_systems/schematic_svg.py` exports a stem-buffer SVG artifact path
  and shows buffer/control summary fields when a trace changes the buffer;
- `tests/test_stem_buffer_svg.py` verifies the SVG is parseable, source-linked,
  port/layer annotated, records control, buffer before/after, cleared input,
  transition status, and exactly matches renderer output;
- `docs/stem-buffer-accumulation-svg.md` explains the render boundary.

This SVG is a view of the ADR-0024 trace. It does not add command decoding or
new Universal Cell semantics.

## Success Criteria

- Red tests fail before implementation because the stem-buffer SVG artifact or
  export is absent.
- The committed stem-buffer SVG exactly matches renderer output for the JSON
  trace.
- Existing wire, processor, and stem automail SVG tests still pass unchanged.
- The SVG exposes artifact ID, trace ID, three ports, four interpretive layers,
  role `stem`, control before `[0, 1, 0]`, buffer before `[0]`, buffer after
  `[0, 1]`, input after `["_", "_", "_"]`, transition function, status, and
  buffer flow.
- Validation rejects a drifted SVG that disagrees with renderer output.

## Consequences

- P7 gains visible renders for all current structured schematic traces.
- The SVG renderer becomes explicit about stem buffer state without changing
  the JSON-as-authority rule.
- Full command decoding, target routing, and physical simulation remain
  separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_buffer_svg` failed with `ImportError:
  cannot import name 'STEM_BUFFER_SVG_ARTIFACT'` from
  `autarkic_systems.schematic_svg`.

Green step:

- Added `STEM_BUFFER_SVG_ARTIFACT`.
- Added conditional control/buffer summary fields to `render_schematic_svg` for
  traces whose buffer changes.
- Added `schematics/stem_buffer_accumulation_trace.svg`.
- Added `docs/stem-buffer-accumulation-svg.md`.
- `python -m unittest tests.test_stem_buffer_svg
  tests.test_stem_automail_svg tests.test_processor_memory_toggle_svg
  tests.test_single_node_schematic_svg` passed 28 tests.

Full verification:

- `python -m unittest discover` passed 124 tests.
- `python -m py_compile autarkic_systems/schematic_svg.py
  tests/test_stem_buffer_svg.py` passed.
- `python - <<'PY' ... ET.parse(...) ... PY` passed for all four checked-in
  SVGs.
- `git diff --check` passed.

Coverage limits:

- This renders one matching-input buffer append trace only.
- It does not render command decoding.
- It does not claim dynamic reconfiguration or physical circulator
  verification.
