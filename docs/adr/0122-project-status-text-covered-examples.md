# ADR-0122: Project Status Text Covered Examples

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0121 adds `positive_example` and `covered_positive_examples` to transition
evidence bundle entries in registry JSON and project-status JSON. That makes
validated positive-example coverage visible to automation.

The default project status text still renders only bundle IDs and paths. A
human operator can see which bundle files were checked, but not which primary
and covered examples made those checks meaningful without switching to JSON or
opening individual bundle files.

## Decision

Render transition bundle example coverage in the default project status text
report:

- each bundle with a `positive_example` renders `positive example: ...`; and
- each bundle with `covered_positive_examples` renders
  `covered examples: ...`.

This ADR does not change project status JSON, which remains
`schema_version: 7`. Chain evidence text remains unchanged because chain
bundle entries do not yet expose covered positive examples.

## Success Criteria

- Red tests fail before implementation because default project status text
  omits transition bundle `positive example:` lines.
- Red tests fail before implementation because default project status text
  omits transition bundle `covered examples:` lines.
- Text status reports the unsupported self-mailbox covered examples.
- Text status reports the unsupported command-buffer covered examples.
- Project status JSON remains `schema_version: 7`.
- Existing registry validation, source-status validation, project-status JSON,
  and full repository tests remain green.

## Consequences

The first-run human status report now exposes both which artifacts were
validated and which positive examples those artifacts cover. This keeps the
default status command aligned with the JSON surface without changing the
underlying evidence or command-token semantics.

## Test Plan

- Red: run `python -m unittest tests.test_project_status_report` after adding
  assertions for covered-example text.
- Green: update `format_project_status_report` bundle rendering.
- Regression: run focused project-status tests, adjacent evidence-registry
  tests, project status text/JSON, `py_compile`, `git diff --check`, and the
  full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by extending bundle text
rendering to include optional `positive_example` and
`covered_positive_examples` fields when present. The existing chain bundle text
surface stayed unchanged because those bundle entries do not expose those
fields.

The red project-status test run failed before implementation because the
default text report omitted the unsupported self-mailbox positive example. The
green focused run passed 35 project-status tests after implementation.

Regression verification passed: focused project-status and transition-registry
tests ran 52 tests; `py_compile` and `git diff --check` passed; default project
status text rendered the self-mailbox and command-buffer covered examples;
project status JSON remained accepted at `schema_version: 7`; and
`python -m unittest discover` passed 579 tests.
