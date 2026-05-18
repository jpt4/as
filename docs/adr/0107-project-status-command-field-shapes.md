# ADR-0107: Project Status Command Field Shapes

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0106 made project status reject non-text entries inside source-status
command-token lists. The report still ignores command-token fields whose
container shape is wrong. For example, a source-status artifact can include a
non-text `command` field or a scalar `commands` field and still pass if another
valid command-token field is present.

That silently discards malformed source-status data while presenting the
artifact as accepted.

## Decision

Reject source-status records with malformed command-token field shapes:

- `command`, when present, must be text;
- `commands`, when present, must be a list; and
- `blocked_runtime_commands`, when present, must be a list.

This tightens validation of the existing project status JSON contract without
changing the JSON shape, so `schema_version` remains `2`.

## Success Criteria

- Red tests fail before implementation because malformed command-token field
  shapes are silently ignored.
- Malformed command-token field shapes report
  `frontier.failed_subjects: ["source-status-schema"]`.
- Accepted source-status command attribution still reports the checked-in
  `standard-signal`, `write-buf-zero`, and `write-buf-one` frontier.
- Existing missing, malformed, commandless, blank-command, blank-text, and
  non-text command-entry source-status failure behavior remains unchanged.

## Consequences

Project status no longer normalizes malformed command-token fields by omission.
If a source-status artifact chooses one of the recognized command-token
surfaces, that surface must have the expected shape.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  command-token field-shape check exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because non-text `command`, scalar `commands`, and scalar
`blocked_runtime_commands` fields were accepted when another command-token
field supplied a usable command.

`autarkic_systems.project_status` now treats malformed `command`, `commands`,
and `blocked_runtime_commands` field shapes as `source-status-schema` failures.
The project status JSON shape remains `schema_version: 2`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 24 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 49 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 2`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 560 tests.
