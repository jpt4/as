# ADR-0124: Project Status Text Source-Status Cross-Links

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0123 adds `additional_source_statuses` to project status JSON so
automation can inspect the source-review trail behind the blocked
standard-signal and write-buffer command-token frontier. The default text
report still omits those cross-links.

That leaves a human operator with the immediate blocker questions but not the
nearby source-status artifacts that explain why later source reviews preserved
the blocker. The text report should not require switching to JSON to see the
source-status trail behind the safe next slice.

## Decision

Render accepted source-status cross-links in the default project status text
report:

- add an `Additional source statuses:` section;
- group cross-links under the blocked command label for the source-status
  record that named them;
- render each cross-link as `ADR -> path: summary`; and
- render `Additional source statuses: none` when no accepted source-status
  entry names cross-links.

This ADR does not change project status JSON, which remains
`schema_version: 8`.

## Success Criteria

- Red tests fail before implementation because default project status text
  omits the `Additional source statuses:` section.
- Red tests fail before implementation because default project status text
  omits the Guile ASMSIM, ASMSIM process-buffer, and official TLA cross-links
  behind the standard-signal and write-buffer blockers.
- Text status reports `Additional source statuses: none` when accepted
  source-status records have no cross-links.
- Project status JSON remains `schema_version: 8`.
- Existing source-status validation, project-status JSON, and full repository
  tests remain green.

## Consequences

The human first-run status report now exposes both the blocked command-token
questions and the source-status reviews that kept those questions blocked.
This still does not implement standard-signal or write-buffer command-token
execution.

## Test Plan

- Red: run `python -m unittest tests.test_project_status_report` after adding
  text assertions for source-status cross-links.
- Green: update `format_project_status_report` to render the cross-link
  section.
- Regression: run focused project-status tests, adjacent referenced
  source-status tests, project status text/JSON, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by adding an
`Additional source statuses:` section to the default text report. The section
groups cross-links by blocked command label and renders each cross-link as
`ADR -> path: summary`. Source-status records without cross-links render the
fallback `Additional source statuses: none`.

The red project-status run executed 40 tests and failed in two places because
the text report omitted the cross-link section and the no-cross-link fallback.
The green focused run passed 40 project-status tests after implementation.

Regression verification passed: focused project-status and referenced
source-status tests ran 65 tests; `py_compile` and `git diff --check` passed;
default project status text rendered the standard-signal and write-buffer
cross-links; project status JSON remained accepted at `schema_version: 8`; and
`python -m unittest discover` passed 584 tests.
