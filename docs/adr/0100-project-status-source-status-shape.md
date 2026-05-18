# ADR-0100: Project Status Source Status Shape

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0099 added `frontier.failed_subjects` to the project status report. Missing
source-status files now report `source-status-file`, and malformed JSON reports
`source-status-json`.

One class of drift remains: a source-status path can contain valid JSON that is
not a usable source-status object. For example, `{}` is parseable but has no
decision or safe-next-slice signal, and a JSON array is not an object at all.
Treating those inputs as an empty frontier would hide artifact drift.

## Decision

Extend `autarkic_systems.project_status` so source-status JSON must have the
minimal shape needed by the report:

- top-level JSON object;
- text `decision`; and
- text `safe_next_slice`.

Shape failures will report `source-status-schema` in
`frontier.failed_subjects` and will be listed with the invalid source-status
files. JSON parse failures will keep reporting `source-status-json`.

## Success Criteria

- Red tests fail before implementation because schema-invalid source-status
  JSON is treated as accepted empty frontier state.
- `{}` reports `frontier.failed_subjects: ["source-status-schema"]`.
- `[]` reports `frontier.failed_subjects: ["source-status-schema"]` without a
  traceback.
- Malformed JSON still reports `source-status-json`.
- Checked-in source-status records remain accepted.

## Consequences

The project status command now rejects source-status artifacts that are present
but do not carry the fields needed to explain the active frontier.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  source-status shape checks exist.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` showed
two distinct drift paths: `{}` was silently accepted as an empty frontier, and
`[]` crashed with `AttributeError` because the report tried to call `.get` on a
list.

`autarkic_systems.project_status` now checks that source-status JSON is a
top-level object with non-empty text `decision` and `safe_next_slice` fields.
Shape failures report `source-status-schema`; JSON parse failures continue to
report `source-status-json`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 16 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 41 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `accepted: true`, transition `bundle_count: 8`, chain `bundle_count: 2`, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 552 tests.
