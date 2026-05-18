# ADR-0131: Project Status Resolved Question Source Paths

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0130 exposes `resolved_resolution_questions` in project status JSON and
text. The first checked-in resolved question points `command-table-offset` at
`sources/stem_command_buffer_map.json`, the artifact that settled the formal
command offset.

That path is now part of the operator trail. If it is missing, invalid JSON, or
not a JSON object, project status should fail closed instead of presenting the
resolved decision as checked evidence.

## Decision

When an accepted source-status record provides
`resolved_resolution_questions[].source_status`, project status will require the
path to exist and contain parseable top-level JSON object content.

Malformed resolved-question source paths will reject the owning source-status
record as `source-status-schema`. The project status JSON shape remains
`schema_version: 9` because this tightens validation for the existing field
rather than adding a new report field.

## Success Criteria

- Red tests fail before implementation because missing, invalid-JSON, and
  non-object resolved-question `source_status` paths are still accepted.
- The checked-in standard-signal resolved question remains accepted and points
  at `sources/stem_command_buffer_map.json`.
- Project status JSON remains accepted at `schema_version: 9`.
- Project status text continues to render the resolved `command-table-offset`
  decision.
- Full repository tests remain green.

## Consequences

Resolved blocker decisions now have the same basic source-trail safety as
additional source-status cross-links: the operator report cannot silently
present a dead or non-JSON path as evidence.

This ADR does not change runtime behavior, source-status decisions, or project
status output shape.

## Test Plan

- Red: add project-status schema tests for missing, invalid-JSON, and non-object
  resolved-question `source_status` paths.
- Green: update `autarkic_systems.project_status` validation to check those
  paths.
- Regression: run focused project-status tests, project status text/JSON, and
  the full default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by extending resolved
resolution-question validation so optional `source_status` paths must exist and
contain parseable top-level JSON object content.

The red focused run executed 50 tests and failed because missing, invalid-JSON,
and non-object resolved-question source paths were still accepted. The green
focused run passed 50 tests after implementation.

Runtime behavior, source-status decisions, and project status output shape remain
unchanged. Project status still reports `schema_version: 9`; it now fails closed
if a resolved decision points at a dead or non-consumable artifact.

Verification passed: adjacent project-status and standard-signal tests ran 57
tests; `py_compile` and `git diff --check` passed; project status text and JSON
remained accepted at `schema_version: 9`; and `python -m unittest discover`
passed 597 tests.
