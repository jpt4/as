# ADR-0096: Project Status Report

Date: 2026-05-17

## Status

Accepted.

## Context

The project now has many executable and inspectable surfaces: transition
evidence bundles, composed-chain evidence bundles, registry validators, demo
reports, and source-status records for blocked command-token semantics.

That is useful, but the answer to "what is actually green, and what remains
blocked?" still requires knowing several commands and files. A project-status
surface should answer that from the checked artifacts rather than from memory
or a prose summary.

## Decision

Add `autarkic_systems.project_status`, an operator-facing status report that:

- validates the transition evidence registry;
- validates the transition-chain evidence registry;
- reads the current source-status records for recipient non-init,
  `standard-signal`, and write-buffer command-token blockers;
- reports accepted/failed registry status and bundle counts;
- summarizes blocked command tokens and the safe next slice; and
- exposes text and JSON CLI output.

The report will reuse existing validators and source-status JSON. It will not
become a new proof checker, simulator, or source authority.

## Success Criteria

- Red tests fail before implementation because `autarkic_systems.project_status`
  does not exist.
- JSON status reports transition evidence accepted with 8 bundles and chain
  evidence accepted with 2 bundles.
- JSON status reports the blocked command-token frontier:
  `standard-signal`, `write-buf-zero`, and `write-buf-one`.
- Text status names the accepted registries, bundle counts, blocked commands,
  and safe next slice.
- Missing source-status files produce structured rejected output rather than a
  traceback.
- Module execution works through `python -m autarkic_systems.project_status`.

## Consequences

The project gains a live status command that lets agents and operators inspect
the current evidence state before choosing another slice. The command is only
as strong as the registries and source-status records it reuses.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  project status module exists.
- Green: focused project-status tests pass after implementation.
- Regression: run adjacent registry tests, project-status text/JSON CLI,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
with `ModuleNotFoundError: No module named 'autarkic_systems.project_status'`.

`autarkic_systems.project_status` now composes the transition evidence registry
validator, the transition-chain evidence registry validator, and the three
current command-token source-status files into one text/JSON status report.
The report returns structured rejected output for missing source-status files.

Verification:

- `python -m unittest tests.test_project_status_report` passed 5 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry tests.test_chain_demo_report` passed 43 tests.
- `python -m autarkic_systems.project_status` reported accepted transition
  evidence with 8 bundles, accepted chain evidence with 2 bundles, blocked
  commands `standard-signal`, `write-buf-zero`, and `write-buf-one`, and no
  missing source-status files.
- `python -m autarkic_systems.project_status --format json` reported
  `accepted: true`, transition `bundle_count: 8`, chain `bundle_count: 2`,
  and the same blocked command list.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 541 tests.
