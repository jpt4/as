# ADR-0106: Project Status Command Token Types

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0104 made project status reject blank command-token strings in
source-status records. The command extraction logic still ignores non-string
items inside `commands` and `blocked_runtime_commands` lists.

That silent drop is unsafe for an operator-facing frontier report. A malformed
source-status artifact can pass as long as one valid string token remains,
while another malformed token disappears from the report.

## Decision

Reject source-status records when `commands` or `blocked_runtime_commands`
lists contain non-string command-token entries.

This tightens validation of the existing project status JSON contract without
changing the JSON shape, so `schema_version` remains `2`.

## Success Criteria

- Red tests fail before implementation because non-string command-list entries
  are silently ignored.
- Non-string command-list entries report
  `frontier.failed_subjects: ["source-status-schema"]`.
- Accepted source-status command attribution still reports the checked-in
  `standard-signal`, `write-buf-zero`, and `write-buf-one` frontier.
- Existing missing, malformed, commandless, blank-command, and blank-text
  source-status failure behavior remains unchanged.

## Consequences

Project status no longer normalizes malformed command-token lists by omission.
If a source-status artifact lists commands, every command token in that list
must be text.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  command-token type check exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because a source-status record with `commands: ["standard-signal", 0]` was
accepted after silently dropping the integer entry.

`autarkic_systems.project_status` now treats non-string entries in `commands`
or `blocked_runtime_commands` as `source-status-schema` failures. The project
status JSON shape remains `schema_version: 2`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 21 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 46 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 2`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 557 tests.
