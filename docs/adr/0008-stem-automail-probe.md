# ADR-0008: Stem Automail Probe

Date: 2026-05-17

Status: Accepted

## Context

The current Universal Cell probe covers fixed wire/proc behavior and fixed-cell
stem-init reset. PRC's central contribution, however, is organic
component-wise reconfiguration. The smallest next slice is not full stem buffer
processing; it is the explicit automail path where a stem cell becomes a fixed
wire or processor role.

PRC's formal model and Scheme simulator describe automail commands:

- `wr`: become wire with right memory;
- `wl`: become wire with left memory;
- `pr`: become processor with right memory;
- `pl`: become processor with left memory.

## Decision

Extend the Universal Cell probe with:

- stem-state fields for automail, control, and buffer;
- `step_stem_cell` for the automail subset;
- tests for all four automail commands, idle/no-mail behavior, output blocking,
  and invalid automail values.

Do not implement full stem input classification or buffer processing in this
ADR.

## Success Criteria

- Tests are written before implementation and fail while the stem automail API
  is absent.
- `python -m unittest discover` remains green after implementation.
- The implementation documents the coverage limit clearly.

## Consequences

- AS now has an executable reconfiguration foothold.
- Later predicates and claims can cover automail reconfiguration separately
  from fixed-role routing.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_automail` failed because
  `step_stem_cell` was not importable from `autarkic_systems.universal_cell`.

Green step:

- `python -m unittest tests.test_stem_automail` passed 8 tests.
- `python -m unittest discover` passed 28 tests.
- `git diff --check` passed.

Coverage limits:

- This slice covers only automail-driven reconfiguration from stem to fixed
  wire/proc roles.
- It does not model stem input classification, command-buffer construction,
  target routing, or full buffer processing.
