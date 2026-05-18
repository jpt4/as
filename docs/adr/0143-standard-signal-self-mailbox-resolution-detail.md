# ADR-0143: Standard-Signal Self-Mailbox Resolution Detail

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0127 recorded the formal-model self-mailbox exception for
`standard-signal`: productive ordinary standard-signal behavior applies to
wire, proc, and stem cells unless the signal is sent to the self-mailbox of a
stem cell. AS already preserves that source-backed fact in
`sources/standard_signal_command_semantics_status.json`.

The aggregate project status report exposes resolved source-status questions,
but it currently exposes only the standard-signal command-table offset
decision. That leaves an operator-visible gap: the first diagnostic command
still shows the broad `self-target-surface` question as unresolved, but does
not also show the narrower settled decision that stem self-mailbox
`standard-signal` must not be treated as ordinary binary-input
standard-signal behavior.

The broader self-target question remains open because the formal exception does
not select preserve, clear/no-op, or execution behavior for a command token. It
only rejects one tempting equivalence.

## Decision

Add a `resolved_resolution_questions` entry to
`sources/standard_signal_command_semantics_status.json` for the narrower
self-mailbox equivalence decision:

`self-mailbox-standard-signal-binary-input-equivalence`

The decision remains:

`do-not-treat-self-mailbox-standard-signal-as-binary-input`

This ADR does not remove `self-target-surface` from the unresolved standard
signal queue. It does not change Universal Cell runtime behavior. It does not
change project status JSON schema.

## Success Criteria

- Red focused tests fail before implementation because the standard-signal
  resolved question list does not expose the self-mailbox equivalence decision.
- Standard-signal source-status tests verify the resolved detail points to the
  formal self-mailbox exception and keeps the broader self-target question
  unresolved.
- Project-status JSON exposes the resolved self-mailbox equivalence decision.
- Project-status text names the resolved decision and its source artifact.
- Runtime behavior remains unchanged.
- Project status remains accepted at `schema_version: 13`.
- Full repository tests remain green.

## Consequences

Future command-token work should not argue that stem self-mailbox
`standard-signal` can simply replay ordinary binary-input standard-signal
behavior. It still must choose the actual command-token behavior for
self-mailbox and self-target command-buffer surfaces before runtime execution
can widen.

## Test Plan

- Red: run focused standard-signal source-status and project-status tests after
  adding assertions for the missing resolved question.
- Green: update `sources/standard_signal_command_semantics_status.json` and
  the standard-signal status note.
- Regression: run focused standard-signal and project-status tests, project
  status text/JSON checks, and the full default suite.

## After Action Report

Implemented in `sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md` by adding
`self-mailbox-standard-signal-binary-input-equivalence` to
`resolved_resolution_questions`.

The red focused run executed 65 tests and failed because the resolved
self-mailbox equivalence decision was absent from the standard-signal
source-status artifact and project status text/JSON.

The green focused run passed 65 standard-signal and project-status tests after
implementation. Project status text now renders the resolved self-mailbox
equivalence decision under `standard-signal`, while the JSON frontier keeps
`self-target-surface` in the unresolved standard-signal queue.

Runtime behavior remains unchanged. Project status remains accepted at
`schema_version: 13`.

Verification passed: JSON formatting, `py_compile`, and `git diff --check`
passed; project status text and JSON were accepted at `schema_version: 13`;
and `python -m unittest discover` passed 638 tests.
