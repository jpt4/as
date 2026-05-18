# ADR-0101: Project Status Schema Version

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0096 through ADR-0100 turned `autarkic_systems.project_status` into a
useful operator and automation surface. The report now summarizes transition
evidence, chain evidence, and the blocked command-token frontier, including
structured failure subjects for registry and source-status drift.

That JSON shape is now a contract. It should identify its own schema version
so future agents and scripts can detect intentional status-report changes.

## Decision

Add a top-level `schema_version` field to the project status report.

The initial schema version is `1`. Text output remains focused on operator
status; JSON output carries the version for automation.

## Success Criteria

- Red tests fail before implementation because `schema_version` is missing.
- In-process status reports include `schema_version: 1`.
- JSON CLI output includes `schema_version: 1`.
- Existing accepted status and failure summaries remain unchanged.

## Consequences

Future changes to the status report can explicitly bump the schema instead of
silently changing the automation contract.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  schema version exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
with `KeyError: 'schema_version'` in both the in-process report and JSON CLI
payload.

`autarkic_systems.project_status` now emits top-level `schema_version: 1`.
Existing evidence registry, chain registry, and frontier sections remain
unchanged.

Verification:

- `python -m unittest tests.test_project_status_report` passed 16 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 41 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 1`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, and `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 552 tests.
