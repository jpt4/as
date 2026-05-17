# ADR-0021: Stem Automail SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0019 added the first schematic-linked stem automail reconfiguration trace.
ADR-0017 and ADR-0020 render the fixed-role wire and processor traces, but the
visible schematic layer still does not cover reconfiguration. P7 explicitly
lists stem rendering as an open gap.

The stem trace is not just another fixed-role signal-routing example. Its
human-facing render must make the reconfiguration facts visible: the stem role
before the transition, the processor role after the transition, the `pl`
automail command, and automail consumption. Otherwise the SVG would look like a
generic triangular node while hiding the actual AS claim.

## Decision

Add a generated SVG for the stem automail reconfiguration trace:

- `schematics/stem_automail_reconfiguration_trace.svg` renders
  `schematics/stem_automail_reconfiguration_trace.json`;
- `autarkic_systems/schematic_svg.py` exports a stem SVG artifact path and
  teaches the generic renderer to expose stem reconfiguration fields when a
  trace records them;
- `tests/test_stem_automail_svg.py` verifies the stem SVG is parseable,
  source-linked, port/layer annotated, records role and memory before/after,
  records automail before/after, displays the automail flow, and exactly
  matches renderer output;
- `docs/stem-automail-reconfiguration-svg.md` explains the render boundary.

The stem SVG is a visual view of the already executable ADR-0019 trace. It does
not add full stem buffering or dynamic circuit reconfiguration.

## Success Criteria

- Red tests fail before implementation because the stem SVG artifact or export
  is absent.
- The committed stem SVG exactly matches renderer output for the stem JSON
  trace.
- Existing wire and processor SVG tests still pass unchanged.
- The SVG exposes artifact ID, trace ID, three ports, four interpretive layers,
  before role `stem`, after role `proc`, before memory `right`, after memory
  `left`, automail before `pl`, automail after `_`, transition function, and
  automail flow.
- Validation rejects a drifted SVG that disagrees with renderer output.

## Consequences

- P7 gains visible renders for the current wire, processor, and stem trace set.
- The SVG renderer stays JSON-authoritative while becoming explicit about
  reconfiguration fields.
- Full stem buffering, dynamic reconfiguration, larger GELC visualization, and
  physical simulation remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_automail_svg` failed with `ImportError:
  cannot import name 'STEM_AUTOMAIL_SVG_ARTIFACT'` from
  `autarkic_systems.schematic_svg`.

Green step:

- Added `STEM_AUTOMAIL_SVG_ARTIFACT`.
- Added conditional reconfiguration summary fields to `render_schematic_svg`
  for traces whose role or automail changes.
- Added `schematics/stem_automail_reconfiguration_trace.svg`.
- Added `docs/stem-automail-reconfiguration-svg.md`.
- `python -m unittest tests.test_stem_automail_svg
  tests.test_processor_memory_toggle_svg tests.test_single_node_schematic_svg`
  passed 21 tests.

Full verification:

- `python -m unittest discover` passed 98 tests.
- `python -m py_compile autarkic_systems/schematic_svg.py
  tests/test_stem_automail_svg.py` passed.
- `python - <<'PY' ... ET.parse(...) ... PY` passed for all three checked-in
  SVGs.
- `git diff --check` passed.

Coverage limits:

- This renders one stem automail trace only.
- It does not model full stem buffering.
- It does not claim dynamic GELC reconfiguration or physical circulator
  verification.
