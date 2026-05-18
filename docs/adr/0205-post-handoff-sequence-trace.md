# ADR-0205: Post-Handoff Sequence Trace

Date: 2026-05-18

## Status

Accepted.

## Context

The post-handoff network-sequence surface is currently executable, claim-backed,
language-checked, evidence-bundled, and visible through a vertical demo report.
It still lacks a stable trace artifact comparable to the transition and
transition-chain trace records.

Without a trace, the accepted post-handoff behavior is inspectable only by
running the witness or evidence validator. That is adequate for testing, but
weaker as an audit artifact: there is no checked JSON record of the initial
sender/recipient cells, delivered handoff tuple, follow-up input, recipient
before/after follow-up cells, and boundary terms.

## Decision

Add a checked post-handoff sequence trace:

- `schematics/sequences/post_handoff_signal_sequence_trace.json`;
- `autarkic_systems.network_sequence_trace` loader/replay/validator;
- tests covering trace identity, recorded cells, follow-up flow, replay, and
  drift rejection; and
- documentation that distinguishes the trace from scheduler, topology, timing,
  SVG, and new command-semantics claims.

The trace reuses `execute_post_handoff_signal_witness` as its execution
authority. It does not add runtime behavior, claims, proof rules, evidence
bundle fields, project-status fields, scheduler, topology, timing, SVG output,
or command semantics.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_sequence_trace` does not exist.
- The checked trace names the post-handoff sequence claim and helper.
- The trace records the sender initial cell, recipient initial cell, delivered
  tuple, follow-up input, recipient before-follow-up cell, and recipient
  after-follow-up cell.
- Replay through the existing sequence helper matches the recorded status and
  cells.
- Drifted status, delivered tuple, or recipient after-follow-up cells reject
  validation.
- The full default suite remains green.

## Test Plan

- Red: `python -m unittest tests.test_post_handoff_sequence_trace`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent post-handoff sequence/demo/evidence tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_trace.py` and
`schematics/sequences/post_handoff_signal_sequence_trace.json`, with operator
notes in `docs/post-handoff-sequence-trace.md`.

The red focused run failed as intended because
`autarkic_systems.network_sequence_trace` did not exist. The green focused run
passed 8 tests after the loader, replay helper, validator, and checked trace
artifact were added.

Adjacent post-handoff sequence/demo/evidence/language/claim tests passed 61
tests. Live witness JSON still reported accepted status,
`neighbor-delivery-consumed`, delivered tuple `["_", "proc-l-init", "_"]`,
follow-up status `routed`, and recipient after-follow-up output `[0, 0, 1]`.
The full default suite passed 884 tests.
