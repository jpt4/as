# ADR-0018: Processor Memory Toggle Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0016 and ADR-0017 gave AS its first schematic-linked trace and rendered
view, but that trace exercises only wire routing. PRC Universal Cells also
distinguish processor behavior: processor cells route a standard signal and
toggle memory. The existing AS executable probe already tests this behavior, so
the next schematic-linked artifact can add processor coverage without inventing
new transition semantics.

The risk is representational drift. If AS adds a processor trace as a separate
one-off format, the schematic evidence path will fragment immediately. The new
artifact should reuse the ADR-0016 trace schema while making the validator
explicitly understand more than the single ADR-0015 recommended artifact.

## Decision

Add a second structured schematic-linked Universal Cell trace:

- `schematics/processor_memory_toggle_trace.json` records one triangular
  RLEM/Universal Cell node in processor role with left memory, one standard
  input signal, expected output, and expected memory toggle;
- `autarkic_systems/schematic_trace.py` gains generic trace loading and
  validation wrappers while preserving the ADR-0016 single-node wrapper;
- `tests/test_processor_memory_toggle_trace.py` verifies processor-role field
  coverage, left-memory routed signal flow, executable replay through
  `step_fixed_cell`, and rejection when expected memory does not toggle;
- `docs/processor-memory-toggle-trace.md` explains the artifact and its
  boundary.

This is not a new Universal Cell behavior. It is a schematic-linked witness for
the already implemented processor transition.

## Success Criteria

- Red tests fail before implementation because the processor trace artifact and
  generic validation path are absent.
- The processor artifact reuses the same Cell field list and interpretive layer
  vocabulary as the ADR-0016 trace.
- The trace's before-cell role is `proc`, before memory is `left`, and expected
  after memory is `right`.
- The recorded left-memory signal flow is checked against the validator.
- Replaying the trace through `step_fixed_cell` produces the recorded status and
  after-cell.
- A drifted expected memory is rejected by validation.

## Consequences

- P7 advances from a single wire example to fixed-role wire and processor
  schematic-linked traces.
- The schematic trace module becomes a small reusable trace validator rather
  than a one-artifact-only loader.
- Stem automail, rendered processor SVGs, and larger GELC examples remain
  separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_processor_memory_toggle_trace` failed because
  `PROCESSOR_MEMORY_TOGGLE_TRACE_ARTIFACT_ID` was not yet exported from
  `autarkic_systems.schematic_trace`.

Green step:

- Added `schematics/processor_memory_toggle_trace.json`.
- Added generic `load_schematic_trace` and `validate_schematic_trace` support
  while preserving `load_single_node_schematic_trace` and
  `validate_single_node_schematic_trace`.
- Added `docs/processor-memory-toggle-trace.md`.
- `python -m unittest tests.test_processor_memory_toggle_trace` passed 7 tests.

Full verification:

- `python -m unittest tests.test_single_node_schematic_trace
  tests.test_single_node_schematic_svg tests.test_processor_memory_toggle_trace`
  passed 22 tests.
- `python -m unittest discover` passed 76 tests.
- `python -m py_compile autarkic_systems/schematic_trace.py
  tests/test_processor_memory_toggle_trace.py` passed.
- `jq -e . schematics/processor_memory_toggle_trace.json` passed.
- `git diff --check` passed.

Coverage limits:

- This slice covers one processor memory-toggle trace only.
- It does not add a rendered processor SVG.
- It does not cover stem automail or dynamic reconfiguration.
