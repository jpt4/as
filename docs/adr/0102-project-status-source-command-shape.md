# ADR-0102: Project Status Source Command Shape

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0100 made project status reject source-status JSON that is not a usable
object with a decision and safe-next slice. The status command also exists to
summarize the blocked command-token frontier, so a source-status object that
has process fields but no command token fields is still too weak.

Without an explicit command-token shape check, a drifted source-status file can
parse, carry a decision, and still erase the blocked-command frontier from the
project report.

## Decision

Treat source-status records with no extractable blocked command tokens as
`source-status-schema` failures in `autarkic_systems.project_status`.

The command-token extraction remains compatible with the current source-status
forms:

- `command`, for a single command token;
- `commands`, for a command-token list; and
- `blocked_runtime_commands`, for aggregate frontier records.

## Success Criteria

- Red tests fail before implementation because commandless source-status JSON
  is accepted as an empty frontier.
- Commandless source-status JSON reports
  `frontier.failed_subjects: ["source-status-schema"]`.
- The checked-in project status remains accepted and continues to report
  `standard-signal`, `write-buf-zero`, and `write-buf-one`.
- Existing source-status file, JSON, and schema failure behavior remains
  unchanged.

## Consequences

The project status command becomes a better guard against quiet frontier loss.
If a source-status artifact is intended to participate in the command-token
frontier, it must name at least one command token in the accepted fields.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  command-token shape check exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because a source-status record with `decision` and `safe_next_slice`, but no
`command`, `commands`, or `blocked_runtime_commands`, was accepted as an empty
blocked-command frontier.

`autarkic_systems.project_status` now treats that record as
`source-status-schema`, while the checked-in `command`, `commands`, and
`blocked_runtime_commands` forms remain accepted.

Verification:

- `python -m unittest tests.test_project_status_report` passed 17 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 42 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 1`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, blocked commands `standard-signal`, `write-buf-zero`, and
  `write-buf-one`, and `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 553 tests.
