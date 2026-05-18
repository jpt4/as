# ADR-0152: Write-Buffer Recipient Surface Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

The write-buffer source-status record still has an over-broad unresolved
question, `recipient-vs-stem-surface`, which mixes recipient command-message
handling with self-target execution behavior.

AS already has a checked recipient non-init rejection boundary. That boundary
covers delivered recipient `write-buf-zero` and `write-buf-one` command
messages the same way it covers other non-init recipient command messages.

The self-target write-buffer questions remain open because the reviewed
witnesses disagree about buffer-full handling and post-append clearing.

## Decision

Move the recipient side of the write-buffer surface question into
`resolved_resolution_questions` as:

`reject-recipient-write-buffer-command-message-as-non-init`

Replace the unresolved `recipient-vs-stem-surface` question with a narrower
`self-target-surface` question.

This ADR does not implement write-buffer command execution. It leaves
`self-target-surface`, `buffer-full-boundary`, and `post-append-clearing`
unresolved.

## Consequences

The write-buffer source-status frontier should no longer present recipient
command-message input as an unresolved write-buffer runtime surface.

Future write-buffer work can focus on self-mailbox / self-target command-buffer
semantics, buffer-full behavior, and post-append clearing.

## Verification Plan

- Red: update write-buffer, project-status, and source-status frontier tests to
  expect the recipient surface as resolved and the self-target surface as the
  live unresolved surface question.
- Green: update the write-buffer source-status artifact and docs.
- Regression: run focused tests, both status CLIs in JSON mode, `py_compile`,
  `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `sources/write_buffer_command_semantics_status.json` and the
status/frontier test surfaces. The red run executed 84 focused tests and
failed before the source artifact was updated because the recipient surface
was still unresolved.

After implementation, the focused write-buffer/project-status/frontier suite
passed 84 tests. `sources/write_buffer_command_semantics_status.json` parses as
JSON. `python -m autarkic_systems.source_status --format json` accepts schema
1 with write-buffer unresolved questions narrowed to `self-target-surface`,
`buffer-full-boundary`, and `post-append-clearing`, and with
`recipient-surface` listed as resolved. `python -m
autarkic_systems.project_status --format json` accepts schema 14 with
write-buffer blocked runtime surfaces narrowed to `self-mailbox-command` and
`self-target-command-buffer`. `py_compile`, `git diff --check`, and
`python -m unittest discover` passed; the full suite ran 661 tests.
