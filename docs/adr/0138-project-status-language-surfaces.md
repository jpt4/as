# ADR-0138: Project Status Language Surfaces

Date: 2026-05-18

## Status

Accepted.

## Context

The project status command is the first diagnostic surface for operators. It
currently validates transition evidence, chain evidence, and source-status
frontier records, but ADR-0136 and ADR-0137 added direct validation commands
for the base and chain object-language surfaces.

Those language surfaces are now important enough to appear in project status.
Without them, the first diagnostic command can be green even though a lower
claim-language layer would fail when checked directly.

## Decision

Add summarized base and chain language validation sections to
`python -m autarkic_systems.project_status`.

Project status JSON will add:

- `transition_language`, summarizing
  `python -m autarkic_systems.object_language --format json`; and
- `chain_language`, summarizing
  `python -m autarkic_systems.chain_object_language --format json`.

Each summary will include accepted state, language ID, language path, claim and
certificate manifest paths, claim count, certificate count, result count,
failed subjects, and per-result validation details. The overall project
status is accepted only if both language summaries are accepted, along with the
existing evidence and frontier checks.

Default text output will include compact accepted/rejected lines for the two
language surfaces without rendering every syntax-class result.

The project status schema version will bump from `10` to `11`.

## Success Criteria

- Red tests fail before implementation because project status still reports
  schema version `10` and omits `transition_language` / `chain_language`.
- JSON project status reports accepted language summaries with the expected
  counts and failed-subject lists.
- Text project status reports compact transition and chain language status
  lines.
- The project status CLI JSON output carries schema version `11`.
- Full repository tests remain green.

## Consequences

The first diagnostic command now covers the language layers beneath evidence
and frontier reports. Detailed language failures remain available through the
dedicated object-language CLIs.

This does not change any claim, proof, evidence, or runtime semantics.

## Test Plan

- Red: update project-status tests to expect schema version `11`, language
  summary JSON fields, and text lines.
- Green: build transition and chain language summaries from the ADR-0136 and
  ADR-0137 validators, include them in accepted-state calculation, render
  compact text lines, and add CLI path overrides.
- Regression: run focused project-status tests, language CLIs, `py_compile`,
  `git diff --check`, and the full default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` with focused tests in
`tests/test_project_status_report.py`.

The red test run executed 52 project-status tests and failed because project
status still reported schema version `10` and the text report omitted compact
transition and chain language lines. The green implementation adds transition
and chain language summaries, includes them in the project-status accepted
state, renders compact text lines, adds CLI path overrides for both language
surfaces, and bumps `PROJECT_STATUS_SCHEMA_VERSION` to `11`.

The checked-in project status JSON now reports `accepted: true`,
`schema_version: 11`, `transition_language.accepted: true` with
`claim_count: 13`, `certificate_count: 13`, and `result_count: 63`, and
`chain_language.accepted: true` with `claim_count: 2`,
`certificate_count: 2`, and `result_count: 32`.

Verification passed: focused project-status tests ran 52 tests;
`python -m autarkic_systems.project_status --format json` reported accepted
schema version `11`; base and chain object-language JSON commands were
accepted; `py_compile` and `git diff --check` passed; and
`python -m unittest discover` passed 631 tests.
