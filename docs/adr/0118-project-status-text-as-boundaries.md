# ADR-0118: Project Status Text AS Boundaries

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0117 requires source-status records consumed by project status to expose a
non-empty top-level `as_boundary`. Project status JSON now carries that
boundary for each accepted source-status entry.

The default text report still omits those boundaries. A human operator can see
blocked commands, runtime surfaces, and resolution questions, but not the
current AS boundary without switching to JSON mode or opening the source-status
files.

## Decision

Render accepted source-status `as_boundary` values in the default project
status text report under an `AS boundaries:` section. Each entry is grouped by
the contributing command labels, falling back to the source-status path if a
future accepted entry has no commands.

This ADR changes only text output. Project status JSON remains
`schema_version: 6`, and source-status validation semantics are unchanged.

## Success Criteria

- Red tests fail before implementation because the default text report omits
  `AS boundaries:`.
- Text project status reports the recipient non-init AS boundary.
- Text project status reports the standard-signal command-token AS boundary.
- Text project status reports the write-buffer command-token AS boundary.
- Project status JSON remains `schema_version: 6`.
- Existing registry validation, source-status validation, project-status JSON,
  and full repository tests remain green.

## Consequences

The human first-run status report now exposes the same boundary explanation as
the machine-readable frontier. Operators can see not only what remains blocked
but what AS boundary is being preserved.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  text report renders source-status AS boundaries.
- Green: focused project-status tests pass after text rendering is added.
- Regression: run adjacent registry and source-status tests, project status
  text and JSON commands, `py_compile`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

The red run of `python -m unittest tests.test_project_status_report` ran 35
tests and failed one text-output assertion because the default project status
report omitted `AS boundaries:`.

The implementation added `AS boundaries:` lines to
`format_project_status_report`, rendering each accepted source-status boundary
under its contributing command labels. Project status JSON remained
`schema_version: 6`.

Verification passed with:

- `python -m unittest tests.test_project_status_report` (35 tests)
- `python -m unittest tests.test_project_status_report tests.test_recipient_non_init_command_source_status tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` (69 tests)
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py`
- `git diff --check`
- `python -m autarkic_systems.project_status`
- `python -m autarkic_systems.project_status --format json`
- `python -m unittest discover` (575 tests)
