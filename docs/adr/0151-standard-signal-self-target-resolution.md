# ADR-0151: Standard-Signal Self-Target Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0150 left one unresolved standard-signal command-token question:
`self-target-surface`.

AS already has two checked unsupported self-target boundaries:

- `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` preserves unsupported direct
  self-mailbox commands, with covered examples for `standard-signal`,
  `write-buf-zero`, and `write-buf-one`.
- `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` preserves completed
  self-target non-init command buffers at the append boundary, with covered
  examples for self `standard-signal`, self `write-buf-zero`, and self
  `write-buf-one`.

Those boundaries do not implement command-token execution. They do, however,
settle what AS currently does for self-target `standard-signal` command tokens:
preserve/report unsupported rather than replay ordinary binary-input behavior
or execute a new command rule.

## Decision

Move `self-target-surface` from unresolved to resolved in
`sources/standard_signal_command_semantics_status.json`.

The resolved decision is:

`preserve-self-target-standard-signal-as-unsupported`

This ADR does not implement `standard-signal` command-token execution. It
closes the standard-signal source-status frontier by pointing self-target
standard-signal command tokens at the existing unsupported preservation
boundaries.

## Consequences

The standard-signal source-status record should have no unresolved
`required_resolution_questions`.

Standard-signal may remain in the blocked-command summary as a command token
that AS refuses to execute, but the source-status record should no longer
present any open standard-signal resolution questions.

Future work on standard-signal command-token execution would need a new ADR
that intentionally replaces the unsupported preservation boundary.

## Verification Plan

- Red: update standard-signal, project-status, and source-status frontier
  tests to expect `self-target-surface` as resolved and no unresolved
  standard-signal questions.
- Green: update the standard-signal source-status artifact and unsupported
  boundary notes.
- Regression: run focused tests, both status CLIs in JSON mode, evidence
  registry validation, `py_compile`, `git diff --check`, and the full unittest
  suite.

## After Action Report

Implemented in `sources/standard_signal_command_semantics_status.json`,
`evidence/self_mailbox_unsupported_bundle.json`, and
`evidence/command_buffer_unsupported_bundle.json`. The standard-signal
source-status record now has no unresolved `required_resolution_questions`.

The red focused run executed 87 standard-signal, project-status, and
source-status frontier tests and failed because `self-target-surface` was
still unresolved and absent from `resolved_resolution_questions`.

The green focused run passed 99 tests across standard-signal status,
project-status, source-status frontier, and the two unsupported evidence
bundles. The evidence bundle registry accepted all 8 bundles. Source-status
JSON was accepted at `schema_version: 1` with no unresolved standard-signal
questions. Project-status JSON remained accepted at `schema_version: 14`,
`py_compile` and `git diff --check` passed, and `python -m unittest discover`
passed 660 tests.
