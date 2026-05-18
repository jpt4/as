# ADR-0117: Project Status Source AS Boundary

Date: 2026-05-18

## Status

Accepted.

## Context

The project status frontier summarizes source-status records that explain why
`standard-signal`, `write-buf-zero`, and `write-buf-one` command-token
execution remains blocked.

Project status already exposes an `as_boundary` field for each accepted
source-status entry, but the field is optional. The checked-in recipient
non-init command-message source-status record therefore appears in project
status with `as_boundary: ""`, even though it has nested boundary text for its
standard-signal, write-buffer, and multi-command subdecisions.

## Decision

Require every source-status record consumed by project status to provide a
non-empty top-level `as_boundary` string. Add that top-level boundary to the
recipient non-init command-message source-status artifact.

This ADR tightens source-status validation only. Project status JSON remains
`schema_version: 6`.

## Success Criteria

- Red tests fail before implementation because the checked-in recipient
  non-init source-status boundary is blank in project status.
- Missing top-level `as_boundary` fields report `source-status-schema`.
- Blank top-level `as_boundary` values report `source-status-schema`.
- Checked-in project status remains accepted and exposes non-empty
  `as_boundary` text for every accepted source-status entry.
- Project status JSON remains `schema_version: 6`.
- Existing registry validation, project-status text/JSON output, and full
  repository tests remain green.

## Consequences

The project status frontier can no longer accept a source-status record that
names blocked commands without also stating the AS boundary those blockers
enforce.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before
  source-status `as_boundary` is required and before the recipient non-init
  source-status artifact has a top-level boundary.
- Green: focused project-status tests pass after validation and source-status
  artifact updates.
- Regression: run adjacent registry tests, project status text and JSON
  commands, `py_compile`, `jq`, `git diff --check`, and the full default suite
  before commit.

## After Action Report

The red run of `python -m unittest tests.test_project_status_report` ran 35
tests and failed three assertions. Missing and blank `as_boundary` fields were
accepted, and the checked-in recipient non-init source-status appeared in
project status with `as_boundary: ""`.

The implementation added a non-empty top-level `as_boundary` requirement to
project status source-status validation and added the aggregate boundary to
`sources/recipient_non_init_command_source_status.json`. The project status
JSON shape remained `schema_version: 6`.

Verification passed with:

- `python -m unittest tests.test_project_status_report` (35 tests)
- `python -m unittest tests.test_project_status_report tests.test_recipient_non_init_command_source_status tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` (69 tests)
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py`
- `jq -e . sources/recipient_non_init_command_source_status.json`
- `git diff --check`
- `python -m autarkic_systems.project_status --format json`
- `python -m autarkic_systems.project_status`
- `python -m unittest discover` (575 tests)
