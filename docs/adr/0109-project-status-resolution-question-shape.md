# ADR-0109: Project Status Resolution Question Shape

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0108 added per-source `required_resolution_questions` IDs to the project
status JSON report. The current extractor treats malformed question lists as
empty or partial lists.

That is unsafe for the active command-semantics frontier. A malformed
source-status artifact can pass project status while silently dropping the
question IDs that explain why a command-token path remains blocked.

## Decision

When a source-status record includes `required_resolution_questions`, validate
the field before accepting the source-status record:

- `required_resolution_questions`, when present, must be a list;
- each entry must be an object; and
- each entry must include a non-whitespace text `question_id`.

This tightens validation of the existing project status JSON contract without
changing the JSON shape, so `schema_version` remains `3`.

## Success Criteria

- Red tests fail before implementation because malformed resolution-question
  fields are silently ignored.
- Malformed resolution-question fields report
  `frontier.failed_subjects: ["source-status-schema"]`.
- Accepted source-status entries still expose the checked-in standard-signal
  and write-buffer resolution question IDs.
- Existing missing, malformed, command-token, and source-status text failure
  behavior remains unchanged.

## Consequences

Project status no longer treats malformed blocker-question metadata as absent.
If a source-status artifact records resolution questions, those question IDs
must be shape-valid before automation can trust the project status report.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  resolution-question shape check exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because scalar `required_resolution_questions`, non-object entries, and blank
`question_id` values were accepted and silently dropped from the report.

`autarkic_systems.project_status` now treats malformed
`required_resolution_questions` metadata as `source-status-schema`. The project
status JSON shape remains `schema_version: 3`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 27 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 52 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 3`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution,
  standard-signal and write-buffer resolution question IDs, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 563 tests.
