# ADR-0110: Project Status Text Resolution Questions

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0108 exposed source-status `required_resolution_questions` in the project
status JSON report, and ADR-0109 made that metadata shape-checked. The default
text report still names the blocked command tokens without naming the question
IDs that explain what must be resolved before those tokens can be executed.

That leaves the first-run operator path weaker than the automation path: a
human running `python -m autarkic_systems.project_status` can see that
`standard-signal`, `write-buf-zero`, and `write-buf-one` are blocked, but must
switch to JSON or inspect source-status files to see the concrete decision
questions.

## Decision

Render accepted per-source resolution question IDs in the text project status
report.

The text report will add a `Resolution questions:` section. Source-status
entries that have no question IDs are omitted from that section; if no accepted
source-status entry has question IDs, the section reports `none`.

This is a text-report visibility change only. The machine-readable project
status JSON shape remains unchanged, so `schema_version` remains `3`.

## Success Criteria

- Red tests fail before implementation because the text status report omits
  the `Resolution questions:` section.
- The default text report names the standard-signal resolution question IDs.
- The default text report names the write-buffer resolution question IDs.
- JSON status output remains at `schema_version: 3` with the same accepted
  frontier.
- Existing source-status validation and registry failure behavior remains
  unchanged.

## Consequences

The default operator command now shows both the blocked command tokens and the
question IDs that define the next source-backed decision work. This makes the
plain text report a better handoff surface for future agents without widening
the command-token execution semantics.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  text formatter renders resolution question IDs.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI text and JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because the text report omitted the `Resolution questions:` section and only
named the blocked command tokens.

`autarkic_systems.project_status` now renders a text `Resolution questions:`
section for accepted source-status entries that carry question IDs. The default
status command names the standard-signal and write-buffer blocker question IDs.
The JSON report remains `schema_version: 3`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 29 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 54 tests.
- `python -m autarkic_systems.project_status` reported accepted transition
  evidence with 8 bundles, accepted chain evidence with 2 bundles, blocked
  commands `standard-signal`, `write-buf-zero`, and `write-buf-one`, and text
  resolution-question lines for standard-signal and write-buffer blockers.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 3`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution,
  standard-signal and write-buffer resolution question IDs, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 565 tests.
