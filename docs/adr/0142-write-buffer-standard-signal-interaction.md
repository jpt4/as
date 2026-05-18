# ADR-0142: Write-Buffer Standard-Signal Interaction Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0129 recorded that the named write-buffer commands carry literal append
bits: `write-buf-zero` appends `0`, and `write-buf-one` appends `1`. That
source-backed sub-decision is present in the formal command table and in the
RAA, SEMSIM, and FSMSIM legacy witnesses.

The write-buffer frontier still contains several unresolved execution
questions. The remaining disagreements concern which runtime surface may
execute the commands, how full buffers are handled, and what state is cleared
after append. However, the older `standard-signal-interaction` question bundled
two concerns together: whether write-buffer command bits are derived from the
ordinary standard-signal high-rail comparison path, and whether write-buffer
execution clears or otherwise interacts with high-rail state after append.

The first concern is now settled by ADR-0129. The second concern remains part
of the broader post-append clearing question.

## Decision

Move `standard-signal-interaction` out of the write-buffer unresolved question
queue and record it as a resolved resolution question in
`sources/write_buffer_command_semantics_status.json`.

The recorded decision is:

`write-buffer-command-bits-are-literal-not-high-rail-derived`

This ADR does not implement write-buffer command execution. It does not decide
recipient versus stem execution, buffer-full behavior, or post-append clearing.
Those questions remain unresolved and continue to block runtime behavior.

This ADR does not change project status JSON schema.

## Success Criteria

- Red project-status tests fail before implementation because
  `standard-signal-interaction` remains unresolved and no write-buffer resolved
  question is exposed.
- Write-buffer source-status tests verify that
  `standard-signal-interaction` is no longer in the unresolved queue.
- Project status JSON exposes the write-buffer resolved question and preserves
  the remaining unresolved write-buffer questions.
- Project status text names the resolved write-buffer question and its source
  artifact.
- Runtime behavior remains unchanged.
- Project status remains accepted at `schema_version: 13`.
- Full repository tests remain green.

## Consequences

Future write-buffer work should not reopen the bit-source/high-rail derivation
question. It should focus on the still-open execution surface, buffer-full, and
post-append clearing decisions. If post-append clearing later chooses a
high-rail-clearing rule, that will be an execution-state decision, not a change
to the literal command bit source.

## Test Plan

- Red: run focused project-status and write-buffer source-status tests after
  adding assertions for the resolved write-buffer question.
- Green: update `sources/write_buffer_command_semantics_status.json` and the
  write-buffer status note.
- Regression: run focused project-status and write-buffer source-status tests,
  project status text/JSON checks, and the full default suite.

## After Action Report

Implemented in `sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md` by moving
`standard-signal-interaction` from unresolved write-buffer questions to a
resolved question with the decision
`write-buffer-command-bits-are-literal-not-high-rail-derived`.

The red focused run executed 64 tests and failed because the write-buffer
source-status artifact still listed `standard-signal-interaction` as
unresolved and did not expose `resolved_resolution_questions`.

The green focused run passed 64 project-status and write-buffer source-status
tests after implementation. Project status text now renders the resolved
write-buffer decision under `write-buf-zero, write-buf-one`, while the JSON
frontier leaves only `recipient-vs-stem-surface`, `buffer-full-boundary`, and
`post-append-clearing` in the unresolved write-buffer queue.

Runtime behavior remains unchanged. Project status remains accepted at
`schema_version: 13`.

Verification passed: JSON formatting, `py_compile`, and `git diff --check`
passed; project status text and JSON were accepted at `schema_version: 13`;
and `python -m unittest discover` passed 637 tests.
