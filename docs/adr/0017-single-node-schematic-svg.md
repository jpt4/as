# ADR-0017: Single-Node Schematic SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0016 added a structured single-node triangular RLEM/Universal Cell trace.
That artifact is executable and source-backed, but it is not yet a visible
schematic. P7 still needs hardware/schematic evidence, and a human-readable
diagram is useful only if it is generated from the structured trace rather than
maintained as an independent drawing.

The immediate risk is drift. A hand-edited SVG could show a different port
orientation, memory direction, or routed signal flow from the JSON artifact and
still look plausible. The renderer should therefore treat the JSON trace as the
source of truth and make enough SVG structure testable to catch drift.

## Decision

Add a small SVG renderer for the ADR-0016 artifact:

- `autarkic_systems/schematic_svg.py` renders and validates an SVG document
  from `SingleNodeSchematicTrace`;
- `schematics/single_node_triangular_rlem_trace.svg` is the checked-in rendered
  view;
- `tests/test_single_node_schematic_svg.py` verifies the SVG document is
  nonblank, sourced from the JSON artifact, labels the three ports, records the
  routed signal flow, carries the four interpretive layer IDs, and matches the
  committed SVG file;
- `docs/single-node-schematic-svg.md` explains the render boundary.

The SVG is deliberately plain. It is not a final hardware diagram or a physics
simulation. Its job is to make the single-node trace inspectable while keeping
the JSON artifact authoritative.

## Success Criteria

- Red tests fail before implementation because `autarkic_systems.schematic_svg`
  and the SVG artifact are absent.
- The renderer consumes `schematics/single_node_triangular_rlem_trace.json`.
- The committed SVG exactly matches renderer output for the current trace.
- The SVG contains a triangle, three labeled port groups, memory direction, the
  trace ID, the transition function, and the routed signal flow.
- The SVG exposes all four interpretive layer IDs.
- Validation rejects an SVG that does not match the renderer output.

## Consequences

- P7 gains its first visible schematic artifact without weakening the structured
  trace as source of truth.
- Later visual design can improve the SVG while keeping renderer tests as the
  drift guard.
- Larger GELC renders, processor traces, and stem traces remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_single_node_schematic_svg` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.schematic_svg'`.

Green step:

- Added `autarkic_systems/schematic_svg.py`.
- Added `schematics/single_node_triangular_rlem_trace.svg`.
- Added `docs/single-node-schematic-svg.md`.
- `python -m unittest tests.test_single_node_schematic_svg` passed 7 tests.

Full verification:

- `python -m unittest tests.test_single_node_schematic_svg` passed 7 tests.
- `python -m unittest discover` passed 69 tests.
- `python -m py_compile autarkic_systems/schematic_svg.py
  tests/test_single_node_schematic_svg.py` passed.
- `python - <<'PY' ... ET.parse('schematics/single_node_triangular_rlem_trace.svg')
  ... PY` passed.
- `git diff --check` passed.

Coverage limits:

- This is a generated single-node SVG view, not a complete GELC circuit
  diagram.
- It does not claim physical circulator verification.
- It renders one fixed-role wire trace only.
