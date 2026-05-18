# ADR-0158: Resolution Question ID Uniqueness

Date: 2026-05-18

## Status

Accepted.

## Context

Source-status validation now checks question shape, evidence coverage,
unresolved/resolved disjointness, and execution-readiness consistency.

However, a record can still repeat the same unresolved question ID inside
`required_resolution_questions`, or repeat the same resolved question ID inside
`resolved_resolution_questions`. The current coverage checks use sets, so such
duplicates can pass while producing ambiguous frontier text and JSON.

## Decision

Reject source-status records with duplicate unresolved
`required_resolution_questions[].question_id` values.

Reject source-status records with duplicate
`resolved_resolution_questions[].question_id` values.

This is a validation-only tightening. It does not change accepted JSON shape,
status schema versions, or Universal Cell runtime behavior.

## Consequences

The source-status frontier cannot present the same blocker or settled decision
twice inside one source-status record.

Project-status remains schema 15, and source-status frontier remains schema 2.

## Verification Plan

- Red: add schema tests for duplicate unresolved and duplicate resolved
  question IDs.
- Green: tighten source-status validation to fail closed on those duplicates.
- Regression: run focused status tests, both status CLIs in JSON mode,
  `py_compile`, `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py` with tests in
`tests/test_project_status_report.py`.

The red run covered the two new schema fixtures and failed because duplicate
unresolved and duplicate resolved `question_id` values were accepted.

The green implementation rejects duplicates in each list before evidence,
readiness, or unresolved/resolved disjointness checks depend on set semantics.
This preserves project-status schema 15, source-status frontier schema 2, and
all Universal Cell runtime behavior.

Verification passed:

- the two targeted red/green tests;
- `python -m unittest tests.test_project_status_report tests.test_source_status_frontier_cli`
  ran 85 tests;
- `python -m autarkic_systems.source_status --format json` accepted schema 2;
- `python -m autarkic_systems.project_status --format json` accepted schema 15;
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py`;
- `git diff --check`; and
- `python -m unittest discover` ran 671 tests.
