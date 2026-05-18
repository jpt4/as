# ADR-0104: Project Status Nonempty Source Commands

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0102 made project status reject source-status records that do not expose
any command token fields. ADR-0103 then attributed extracted command tokens to
each accepted source-status entry.

The extraction logic still treats blank strings as command tokens. A drifted
source-status artifact can therefore pass the command-token shape check while
contributing an invisible or whitespace-only frontier term.

## Decision

Reject source-status records whose command-token fields contain blank command
strings.

The check applies to every accepted command-token surface used by project
status:

- `command`;
- `commands`; and
- `blocked_runtime_commands`.

The project status JSON shape remains `schema_version: 2`; this ADR tightens
validation of that existing shape rather than adding new fields.

## Success Criteria

- Red tests fail before implementation because blank command strings are
  accepted as source-status command tokens.
- Blank command strings report
  `frontier.failed_subjects: ["source-status-schema"]`.
- Accepted source-status command attribution still reports the checked-in
  `standard-signal`, `write-buf-zero`, and `write-buf-one` frontier.
- Existing missing, malformed, and commandless source-status failure behavior
  remains unchanged.

## Consequences

The project status frontier cannot contain invisible command terms. Source
status records must name command tokens as non-empty text if they participate
in the blocked-command frontier.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  nonempty command-token check exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because a source-status record with `commands: ["standard-signal", "  "]` was
accepted as a valid frontier contributor.

`autarkic_systems.project_status` now treats blank strings in `command`,
`commands`, or `blocked_runtime_commands` as `source-status-schema` failures.
The project status JSON shape remains `schema_version: 2`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 18 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 43 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 2`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 554 tests.
