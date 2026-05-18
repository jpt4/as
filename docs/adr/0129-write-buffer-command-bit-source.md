# ADR-0129: Write-Buffer Command Bit Source Evidence

Date: 2026-05-18

## Status

Accepted.

## Context

Write-buffer command execution remains blocked because the PRC witnesses still
disagree about buffer-full handling and post-append clearing. However, one
smaller part of the semantics is source-backed enough to record now:
`write-buf-zero` and `write-buf-one` name literal bit append commands.

The formal command table names `write-buf-zero` and `write-buf-one` as separate
commands. RAA dispatches those commands to `(write-buf 0)` and `(write-buf 1)`.
SEMSIM and FSMSIM likewise define separate append functions for `0` and `1`.
That does not decide when these commands should execute, what happens when the
buffer is full, or whether input/mail/high-rail state is cleared after append.
It does narrow the `standard-signal-interaction` question: the bit carried by a
write-buffer command is literal, not derived from the ordinary standard-signal
high-rail comparison path.

## Decision

Extend `sources/write_buffer_command_semantics_status.json` with a
`command_bit_source` witness set. The new status records that the named
write-buffer commands carry literal `0` and `1` append values across the
formal command table and the RAA, SEMSIM, and FSMSIM legacy witnesses.

This ADR does not remove `standard-signal-interaction` from the unresolved
queue. High-rail clearing and command-buffer interaction remain coupled to the
post-append-clearing decision.

This ADR does not change Universal Cell runtime behavior or project status JSON
schema.

## Success Criteria

- Red tests fail before implementation because the write-buffer source-status
  artifact does not expose the command bit-source witness.
- Tests verify the formal and legacy witness loci for literal zero/one command
  bits.
- Tests verify the unresolved write-buffer question set is unchanged.
- Project status remains accepted at `schema_version: 8`.
- Full repository tests remain green.

## Consequences

Future write-buffer execution work can stop asking where the appended bit comes
from. It still must decide the execution surface, buffer-full boundary,
post-append clearing, and high-rail/state interaction before changing runtime
behavior.

## Test Plan

- Red: run `python -m unittest tests.test_write_buffer_command_semantics_status`
  after adding assertions for the missing `command_bit_source` witness.
- Green: update the write-buffer source-status JSON and human-facing note.
- Regression: run adjacent write-buffer, project-status, and full default
  tests before commit.

## After Action Report

Implemented in `sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md` by adding a
`command_bit_source` witness. The witness records that `write-buf-zero` and
`write-buf-one` carry literal `0` and `1` append bits across the formal command
table and RAA, SEMSIM, and FSMSIM legacy witnesses.

The red focused run executed 6 tests and failed because `command_bit_source`
was absent from the write-buffer source-status artifact. The green focused run
passed 6 tests after implementation.

Runtime behavior remains unchanged. The unresolved write-buffer question set
is unchanged because execution surface, buffer-full behavior, post-append
clearing, and high-rail/state interaction still require a later decision.

Verification passed: adjacent write-buffer and project-status tests ran 49
tests; JSON formatting, `py_compile`, and `git diff --check` passed; project
status text and JSON remained accepted at `schema_version: 8`; and
`python -m unittest discover` passed 590 tests.
