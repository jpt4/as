# ADR-0147: Resolution Evidence Coverage

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0144 added source evidence for unresolved command-token questions. ADR-0146
then required each evidence entry to point at a live unresolved question in the
same source-status record. One remaining drift path is still open: a record can
name unresolved `required_resolution_questions` while omitting
`resolution_question_evidence` entirely, or while giving evidence for only some
of those questions.

That weakens both `python -m autarkic_systems.project_status` and the focused
`python -m autarkic_systems.source_status` frontier report. They can show a
work queue of unresolved questions without proving that every live blocker has
the source conflict or missing-authority note that makes it actionable.

## Decision

Require `resolution_question_evidence` to cover every unresolved
`required_resolution_questions[].question_id` in the same source-status record.

Source-status records with no unresolved questions may still omit the field or
provide an empty evidence list. Records with one or more unresolved questions
must provide a list with an evidence entry for each unresolved question ID.
Unmatched evidence IDs continue to fail closed under ADR-0146.

This preserves project status `schema_version: 14` and source-status frontier
`schema_version: 1` because the emitted JSON shape is unchanged. Only the
validation contract is tightened.

## Success Criteria

- Red tests fail before implementation because scratch source-status records
  with unresolved questions but missing evidence are still accepted.
- Project status rejects missing or partial evidence coverage as
  `source-status-schema`.
- The focused source-status frontier report rejects the same drift through the
  shared validator.
- Checked-in source-status records remain accepted.
- Runtime behavior remains unchanged.
- Full repository tests remain green.

## Consequences

The unresolved-question queue becomes self-auditing: every open blocker carried
by the diagnostic reports has an attached source evidence note. That should
reduce ungrounded work selection and make typo/staleness errors visible before
future agents act on the frontier.

This does not resolve any command-token question and does not change Universal
Cell behavior.

## Test Plan

- Red: add project-status and source-status frontier tests for unresolved
  questions missing evidence coverage.
- Green: tighten the shared source-status frontier validator.
- Regression: run focused project-status/source-status tests, project status
  and source-status text/JSON checks, `py_compile`, `git diff --check`, and the
  full default suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py`.

The red focused run executed 74 tests and failed because project status and the
focused source-status frontier report still accepted scratch source-status
records with unresolved questions but missing or partial
`resolution_question_evidence` coverage.

The green implementation makes the shared frontier validator reject records
with unresolved `required_resolution_questions` unless
`resolution_question_evidence` contains an entry for every unresolved question
ID. Records without unresolved questions may still omit the field or provide an
empty list.

Runtime behavior remains unchanged.

Verification passed: focused project-status and source-status frontier tests
ran 74 tests; source-status JSON was accepted at `schema_version: 1`; project
status JSON remained accepted at `schema_version: 14`; `py_compile` and
`git diff --check` passed; and `python -m unittest discover` passed 655 tests.
