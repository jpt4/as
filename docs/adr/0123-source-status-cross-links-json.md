# ADR-0123: Project Status Source-Status Cross-Links

Date: 2026-05-18

## Status

Accepted.

## Context

The current project status JSON carries each accepted source-status record's
blocked commands, runtime surfaces, AS boundary, and resolution questions. The
standard-signal and write-buffer source-status records also name
`additional_source_statuses`: the Guile ASMSIM, process-buffer, and official
TLA source reviews that strengthen or preserve the blocker.

Those cross-links are part of the evidence trail needed to revisit the safe
next slice, but project status drops them. Automation can see that a command is
blocked and which questions remain open, but not the adjacent source-status
artifacts that explain why the blocker survived later source review.

## Decision

Expose source-status cross-links in project status JSON:

- each accepted `frontier.source_statuses` entry will include
  `additional_source_statuses`;
- each cross-link entry will carry `adr`, `path`, and `summary`;
- source-status records that omit `additional_source_statuses` will report an
  empty list; and
- malformed cross-link metadata will reject the source-status file as
  `source-status-schema`.

Project status JSON will bump to `schema_version: 8`. The default text report
will remain unchanged in this ADR; it already names the immediate blocker
questions and safe next slice.

## Success Criteria

- Red tests fail before implementation because project status JSON still
  reports `schema_version: 7`.
- Red tests fail before implementation because accepted source-status entries
  do not carry `additional_source_statuses`.
- Accepted project status JSON exposes the standard-signal and write-buffer
  cross-links to Guile ASMSIM, ASMSIM process-buffer, and official TLA
  source-status artifacts.
- Source-status records without cross-links report an empty list.
- Malformed `additional_source_statuses` containers, entries, or required text
  fields report `source-status-schema`.
- Project status text remains unchanged.
- Full repository tests remain green.

## Consequences

The project-status JSON frontier now preserves the source-review trail needed
to decide whether the blocked command-token semantics can be revisited. This
does not implement standard-signal or write-buffer command execution; it makes
the existing blocker evidence more inspectable.

## Test Plan

- Red: run `python -m unittest tests.test_project_status_report` after adding
  schema, cross-link, and malformed-cross-link assertions.
- Green: update `autarkic_systems.project_status` to carry and validate the
  cross-link metadata.
- Regression: run focused project-status tests, adjacent source-status
  project-status checks, project status text/JSON, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by adding
`additional_source_statuses` to each accepted `frontier.source_statuses` entry,
defaulting omitted cross-links to `[]`, validating cross-link metadata shape,
and bumping project status JSON to `schema_version: 8`.

The red project-status run executed 38 tests and failed in five places:
project status still reported `schema_version: 7`, and malformed
`additional_source_statuses` inputs were still accepted. The green focused run
passed 38 project-status tests after implementation.

Regression verification passed: the focused project-status and referenced
source-status suite ran 63 tests; `py_compile` and `git diff --check` passed;
project status JSON was accepted at `schema_version: 8` with standard-signal
and write-buffer cross-links; default project status text remained accepted;
and `python -m unittest discover` passed 582 tests.
