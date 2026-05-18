# ADR-0148: Standard-Signal Recipient Surface Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

The standard-signal command-token frontier still lists three unresolved
questions:

- whether the command token replays ordinary binary-input standard-signal
  behavior;
- whether delivered recipient command-message inputs may execute
  `standard-signal`; and
- what self-mailbox and self-target command-buffer surfaces should do.

ADR-0143 already resolved only the narrow self-mailbox equivalence question:
a stem self-mailbox `standard-signal` command token must not simply be treated
as ordinary binary-input standard-signal behavior. That did not decide the
actual self-target behavior.

The recipient side has stronger evidence. AS already has a named and bundled
recipient non-init command-message rejection boundary. The formal model names
`standard-signal` in the command table and has a generic special-message
handoff, but does not provide a recipient execution rule for delivered
`standard-signal` command messages. The reviewed legacy witnesses exclude
`standard-signal` from their special-message sets and treat ordinary standard
signals through the binary-input path.

## Decision

Move the standard-signal `recipient-surface` question from unresolved to
resolved in `sources/standard_signal_command_semantics_status.json`.

The resolved decision is:

`reject-recipient-standard-signal-command-message-as-non-init`

This ADR does not implement standard-signal command-token execution. It does
not resolve whether the command token is equivalent to ordinary binary input,
and it does not select self-mailbox or self-target command-buffer behavior.

## Consequences

The source-status frontier should now show only two unresolved standard-signal
questions: `command-token-vs-binary-input` and `self-target-surface`.

The resolved question list should make the recipient rejection decision visible
to both the aggregate project-status report and the focused source-status
frontier report.

The recipient command-message runtime boundary remains the already-claimed
rejection path rather than a new execution behavior.

## Verification Plan

- Red: update the standard-signal source-status and project-status tests to
  expect `recipient-surface` as a resolved question before changing the source
  artifact.
- Green: update the standard-signal source-status artifact and human note.
- Regression: run focused standard-signal, project-status, and source-status
  tests; run source-status and project-status CLIs in JSON mode; run the full
  unittest suite.

## After Action Report

Implemented in `sources/standard_signal_command_semantics_status.json` and
the standard-signal/recipient/frontier docs. The source-status frontier now
shows standard-signal unresolved questions as `command-token-vs-binary-input`
and `self-target-surface`, while `recipient-surface` appears as a resolved
decision pointing at
`sources/recipient_non_init_command_source_status.json`.

The red focused run executed 83 tests and failed because `recipient-surface`
was still unresolved and `recipient-command-message` still appeared as a
blocked standard-signal runtime surface.

The green focused run passed 83 standard-signal, project-status, and
source-status frontier tests. Source-status JSON was accepted at
`schema_version: 1`, project-status JSON remained accepted at
`schema_version: 14`, `py_compile` and `git diff --check` passed, and
`python -m unittest discover` passed 656 tests.
