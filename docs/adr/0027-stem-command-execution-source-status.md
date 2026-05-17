# ADR-0027: Stem Command Execution Source Status

Date: 2026-05-17

Status: Accepted

## Context

ADR-0026 made PRC's five-bit stem command-buffer target/command map explicit.
The next tempting step is command execution. That is not yet safe: the PRC
formal model and legacy simulator sketches do not present a single clean
execution contract for target dispatch, self mailbox handling, and the
`standard-signal` command.

The formal model's command table supports ADR-0026's order, but later
`process-buffer` prose dispatches target/message pairs through a self mailbox
or neighbor outputs. Current AS `Cell` state has no self mailbox field and its
output channels do not yet carry all special messages. Some legacy files also
use a different command ordering or target interpretation.

## Decision

Add a structured source-status artifact before implementing full stem command
execution:

- `sources/stem_command_execution_source_status.json` records the formal-model
  execution anchor, observed legacy divergences, and implementation blockers;
- `docs/stem-command-execution-source-status.md` explains why command
  execution remains blocked even though the command-buffer decoder now exists;
- `tests/test_stem_command_execution_source_status.py` proves that the current
  decision, canonical command-table dependency, source divergences, and allowed
  next slices are recorded.

AS may continue with smaller execution-preparation ADRs, especially a
self-mailbox/output-token representation or a deliberately tiny self-target
subset. It should not implement general target delivery or special-message
execution until those state-model choices are explicit.

## Success Criteria

- Red tests fail before the structured status artifact exists.
- The status artifact preserves ADR-0026's canonical formal-model target and
  command order.
- The status artifact records at least one target-dispatch divergence and one
  command-order divergence from legacy sources.
- The decision blocks full command execution while naming concrete allowed next
  slices.

## Consequences

- This prevents AS from treating an ambiguous legacy simulator sketch as
  authoritative.
- The next command-execution implementation can be narrower and better tested.
- This is source-status work only; it does not change `step_stem_cell`.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_command_execution_source_status` failed
  because `sources/stem_command_execution_source_status.json` did not exist.

Green step:

- Added `sources/stem_command_execution_source_status.json`.
- Added `docs/stem-command-execution-source-status.md`.
- `python -m unittest tests.test_stem_command_execution_source_status` passed 4
  tests.

Full verification:

- `python -m unittest discover` passed 136 tests.
- `python -m py_compile tests/test_stem_command_execution_source_status.py`
  passed.
- `jq -e . sources/stem_command_execution_source_status.json` passed.
- `git diff --check` passed.

Coverage limits:

- This records source status only.
- It does not change `Cell` state.
- It does not execute or dispatch stem command-buffer commands.
