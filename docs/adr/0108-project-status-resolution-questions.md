# ADR-0108: Project Status Resolution Questions

Date: 2026-05-18

## Status

Accepted.

## Context

The project status report now validates evidence registries and summarizes the
blocked command-token frontier. It also attributes blocked commands to the
source-status files that contribute them.

The same source-status files already record `required_resolution_questions`
for the command semantics that remain blocked. Project status currently omits
those question IDs, so automation can see that `standard-signal`,
`write-buf-zero`, and `write-buf-one` are blocked but cannot see the decision
questions that would unblock a future ADR without re-reading each source file.

## Decision

Add `required_resolution_questions` to each accepted
`frontier.source_statuses` entry in the project status JSON report.

The field is a list of question IDs extracted from each source-status record's
top-level `required_resolution_questions` list. Source-status records without
that list report an empty list.

Because this changes the JSON report shape, bump
`PROJECT_STATUS_SCHEMA_VERSION` from `2` to `3`.

## Success Criteria

- Red tests fail before implementation because source-status entries do not
  include `required_resolution_questions` and the report still has
  `schema_version: 2`.
- In-process status reports include `schema_version: 3`.
- JSON CLI output includes `schema_version: 3`.
- The standard-signal and write-buffer source-status entries expose their
  checked-in resolution question IDs.
- The checked-in project status remains accepted with the same blocked-command
  frontier.

## Consequences

The project status report becomes a better first diagnostic for the active
command-semantics frontier. It can show not only what is blocked, but also the
question IDs that need a future source-backed ADR.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  resolution-question attribution exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because project status still reported `schema_version: 2`; the pre-change JSON
also had no per-source `required_resolution_questions` entries.

`autarkic_systems.project_status` now emits `schema_version: 3` and includes
the source-status question IDs that still block standard-signal and
write-buffer command-token execution. The aggregate blocked-command frontier
remains unchanged.

Verification:

- `python -m unittest tests.test_project_status_report` passed 24 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 49 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 3`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution,
  standard-signal and write-buffer resolution question IDs, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 560 tests.
