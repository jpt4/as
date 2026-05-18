# ADR-0127: Standard-Signal Self-Mailbox Exception Evidence

Date: 2026-05-18

## Status

Accepted.

## Context

Project status now correctly points at the blocked standard-signal and
write-buffer command-token frontier. The next useful work is source resolution,
not another display pass.

ADR-0058 recorded that `standard-signal` command-token execution remains
blocked across recipient command-message input, self-mailbox command, and
self-target command-buffer dispatch. While revisiting the PRC formal model, one
more source anchor is worth promoting: the formal-model prose says wire, proc,
and stem cells all perform productive behavior on standard signals "unless sent
to the self-mailbox of a stem cell."

That sentence does not define a complete runtime rule for `standard-signal` as
a command token, but it does narrow the self-mailbox question: AS should not
treat a stem self-mailbox `standard-signal` command as an ordinary
binary-input standard signal.

## Decision

Extend `sources/standard_signal_command_semantics_status.json` with a
formal-model self-mailbox exception witness. The witness will name the local
PRC source path, the line locus, the exception summary, and the narrowed
decision: stem self-mailbox `standard-signal` remains blocked from ordinary
binary-input execution until a later ADR selects preserve, clear/no-op, or some
other source-backed semantics.

This ADR does not change Universal Cell runtime behavior or project status JSON
schema.

## Success Criteria

- Red tests fail before implementation because the standard-signal
  source-status artifact does not expose the self-mailbox exception witness.
- Tests verify the formal model source text contains the self-mailbox exception
  anchor.
- The standard-signal source-status artifact still blocks recipient,
  self-mailbox, and self-target command-token execution.
- Project status remains accepted at `schema_version: 8`.
- Full repository tests remain green.

## Consequences

The `self-target-surface` resolution question is slightly less vague: ordinary
binary-input standard-signal behavior is explicitly not the right default for a
stem self-mailbox `standard-signal`. AS still needs a later ADR before changing
preserve/reject/no-op behavior.

## Test Plan

- Red: run `python -m unittest tests.test_standard_signal_command_semantics_status`
  after adding assertions for the missing self-mailbox exception witness.
- Green: update the standard-signal source-status JSON and human-facing note.
- Regression: run adjacent source-status tests, project status text/JSON, and
  the full default suite before commit.

## After Action Report

Implemented in `sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md` by adding the formal-model
self-mailbox exception witness. The witness records
`/home/sean/Projects/_upstream/prc/theory/official/formal-model.txt` lines
207-218 as source evidence that ordinary productive standard-signal behavior
does not automatically apply when a standard signal is sent to a stem
self-mailbox.

The red focused run executed 6 tests and failed because
`formal_model_self_mailbox_exception` was absent from the standard-signal
source-status artifact. The green focused run passed 6 tests after
implementation.

Runtime behavior remains unchanged. The narrowed source decision is that AS
must not treat stem self-mailbox `standard-signal` as ordinary binary-input
standard-signal behavior until a later ADR chooses preserve, clear/no-op, or
some other source-backed command-token semantics.

Regression verification passed: focused standard-signal, write-buffer, and
project-status tests ran 54 tests; `python -m json.tool` accepted the updated
source-status JSON; `py_compile` and `git diff --check` passed; default
project status text remained accepted; project status JSON remained accepted
at `schema_version: 8`; and `python -m unittest discover` passed 588 tests.
