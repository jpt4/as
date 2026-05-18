# ADR-0149: Resolution Question Disjointness

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0148 moved the standard-signal `recipient-surface` question from the
unresolved queue into `resolved_resolution_questions`. The project-status and
source-status frontier reports now expose both unresolved and resolved
question lists from each source-status record.

The shared validator already checks malformed unresolved-question entries,
malformed resolved-question entries, resolved-question source paths, and
resolution evidence coverage. It does not yet reject a contradictory record
that lists the same `question_id` as both unresolved and resolved.

## Decision

Make source-status validation fail closed when a question ID appears in both
`required_resolution_questions` and `resolved_resolution_questions` in the same
record.

This preserves project status `schema_version: 14` and source-status frontier
`schema_version: 1` because it tightens validation without changing accepted
payload shape.

## Consequences

A source-status record cannot simultaneously present a question as live work
and as settled history.

Moving future questions from unresolved to resolved now requires removing the
ID from `required_resolution_questions` and from unresolved
`resolution_question_evidence`, then adding it to `resolved_resolution_questions`
with its source trail.

## Verification Plan

- Red: add project-status and source-status frontier tests with an overlapping
  unresolved/resolved `question_id`.
- Green: update the shared source-status validation.
- Regression: run focused project-status and source-status frontier tests,
  both status CLIs in JSON mode, `py_compile`, `git diff --check`, and the
  full unittest suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by adding a shared
source-status schema check for overlap between unresolved and resolved
question IDs.

The red focused run executed 76 project-status and source-status frontier tests
and failed because a scratch record with `recipient-surface` in both
`required_resolution_questions` and `resolved_resolution_questions` was still
accepted.

The green focused run passed 76 tests. Source-status JSON was accepted at
`schema_version: 1`, project-status JSON remained accepted at
`schema_version: 14`, `py_compile` and `git diff --check` passed, and
`python -m unittest discover` passed 658 tests.
