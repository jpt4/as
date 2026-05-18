# ADR-0196: Post-Handoff Signal Witness

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0194 and ADR-0195 make the two-cell neighbor-delivery handoff inspectable,
including the case where a delivered `proc-l-init` command reconfigures an
empty recipient from `wire/right` to `proc/left`. The next substantive question
is whether that accepted handoff can be observed to have a durable behavioral
consequence in a later step without adding scheduler or topology semantics.

The existing transition code already answers this in pieces: the recipient
after the handoff is a normal fixed `proc` cell, and `step_fixed_cell` already
routes binary standard-signal input and toggles processor memory.

## Decision

Add a post-handoff signal witness that composes:

1. the existing two-cell neighbor-delivery witness for an init-family delivery;
2. installation of one explicit binary follow-up input on the recipient state
   produced by that handoff; and
3. the existing fixed/stem transition function for the recipient follow-up
   step.

The witness will report accepted only when the delivery witness consumed an
init-family command and the follow-up step routes a standard binary signal. It
will not introduce scheduler, timing, topology, output-clearing, or new command
semantics.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_sequence` does not exist.
- The accepted fixture records the original delivery witness, recipient
  before-follow-up state, routed follow-up status, output tuple, and toggled
  processor memory.
- A consumed write-buffer handoff is rejected as not an init handoff for this
  witness.
- A malformed follow-up input is rejected as not routed while preserving the
  underlying delivery witness.
- Text and JSON CLI output expose the same sequence status and final recipient
  state.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_post_handoff_signal_witness`.
- Green: the same focused suite passes after implementation.
- Regression: run accepted and rejected CLI fixtures, `python -m compileall -q
  autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_post_handoff_signal_witness` run failed because
`autarkic_systems.network_sequence` did not exist.

The implementation added `autarkic_systems/network_sequence.py`, which composes
the existing two-cell network witness with one explicit recipient follow-up
input and the existing fixed/stem cell step function. The accepted fixture
records delivery of `proc-l-init`, recipient reconfiguration to `proc/left`,
follow-up binary input `(1, 0, 0)`, routed output `(0, 0, 1)`, and processor
memory toggled back to `right`.

The focused post-handoff witness suite passed with 7 tests. Live JSON/text runs
for accepted and rejected fixtures exposed the expected sequence status and
recipient final state. `compileall`, `git diff --check`, and the full default
suite also passed; the full suite ran 823 tests.
