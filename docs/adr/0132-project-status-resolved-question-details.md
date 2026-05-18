# ADR-0132: Project Status Resolved Question Details

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0130 made resolved source-status questions visible in project status, and
ADR-0131 made their optional source paths fail closed. The checked-in
standard-signal resolved question, however, carries more detail than project
status currently exposes:

- `formal_command_offset: 0`;
- `legacy_divergence`, explaining the RAA offset-7 divergence that AS declined.

Dropping those details weakens the settled-decision trail. An operator can see
that `command-table-offset` is resolved, but not the concrete formal offset or
the legacy divergence that motivated recording the decision.

## Decision

Carry optional resolved-question detail fields into project status JSON and
text.

Project status JSON will bump to `schema_version: 10`. Each accepted
`frontier.source_statuses[].resolved_resolution_questions[]` entry may include:

- `formal_command_offset`, an integer offset when the source-status artifact
  names a resolved command-table offset; and
- `legacy_divergence`, non-empty text explaining a legacy-source disagreement
  preserved by the resolved decision.

The default text report will render those details under the resolved question.
Malformed optional detail fields will reject the owning source-status record as
`source-status-schema`.

## Success Criteria

- Red tests fail before implementation because project status remains at
  `schema_version: 9`, omits resolved-question detail fields, does not render
  the detail lines, and accepts malformed detail metadata.
- Project status JSON includes `formal_command_offset: 0` and the RAA legacy
  divergence for the standard-signal `command-table-offset` resolved question.
- Project status text renders the formal command offset and legacy divergence.
- Malformed optional detail metadata is reported as `source-status-schema`.
- Full repository tests remain green.

## Consequences

The first diagnostic command now preserves the useful content of a settled
source-status question, not only the question ID and decision label.

This ADR does not change runtime behavior or any source-status decision.

## Test Plan

- Red: update project-status tests for schema version 10, resolved-question JSON
  detail fields, text detail lines, and malformed optional detail metadata.
- Green: update `autarkic_systems.project_status` to validate, expose, and
  render the detail fields.
- Regression: run focused project-status tests, project status text/JSON, and
  the full default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by carrying optional
`formal_command_offset` and `legacy_divergence` fields from resolved
source-status questions into project status JSON and text, with fail-closed
validation for malformed optional detail metadata.

The red focused run executed 52 tests and failed because project status still
reported `schema_version: 9`, omitted the resolved-question detail fields from
JSON/text, and accepted malformed optional detail metadata. The green focused
run passed 52 tests after implementation.

Runtime behavior and source-status decisions remain unchanged. Project status
now reports `schema_version: 10` and preserves the formal offset and legacy
divergence behind the settled `command-table-offset` decision.

Verification passed: adjacent project-status and standard-signal tests ran 59
tests; `py_compile` and `git diff --check` passed; project status text and JSON
were accepted at `schema_version: 10`; and `python -m unittest discover` passed
599 tests.
