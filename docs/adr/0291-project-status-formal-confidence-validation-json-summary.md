# ADR-0291: Project Status Formal Confidence Validation JSON Summary

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0288 made formal-confidence validation visible in project-status text and
summary output while preserving the existing JSON shape. That was sufficient
for operators, but automation still has to scan
`formal_confidence.results` to find accepted frontier validation subjects.

The accepted fixed-point construction frontier dependency is especially
important:
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`.
It should be available as a compact, top-level JSON summary without changing
the nested formal-confidence payload or any validation semantics.

## Decision

Bump `PROJECT_STATUS_SCHEMA_VERSION` from `22` to `23` and add a top-level
`formal_confidence_validation` JSON field to project-status payloads.

The field is derived from the existing `formal_confidence.results` list and
contains:

- `accepted_validation_count`;
- `failed_validation_count`;
- `accepted_frontier_subjects`; and
- `accepted_frontier_labels`.

The nested `formal_confidence` payload remains unchanged in shape and content.
Text output keeps the ADR-0288 wording, reusing the existing validation helper
logic where possible.

Do not change formal-confidence target validation, project-status acceptance
semantics, proof status, blockers, fixed-point validators, substitution graph
validators, or source-status boundaries.

## Success Criteria

- Red tests fail before implementation because project-status JSON still
  reports schema version `22` and lacks the top-level
  `formal_confidence_validation` field.
- Project-status JSON reports schema version `23`.
- The top-level `formal_confidence_validation` field reports `19` accepted
  validations, `0` failed validations, the accepted
  `AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
  subject, and the compact `fixed_point_construction_frontier_status` label.
- The nested `formal_confidence` payload preserves its existing key set and
  contents.
- Existing project-status text and summary output remain stable.

## Test Plan

- Red:
  `python -m unittest tests.test_project_status_report.ProjectStatusReportTests.test_status_payload_summarizes_evidence_registries_and_frontier tests.test_project_status_report.ProjectStatusReportTests.test_status_payload_exposes_derived_formal_confidence_validation_summary tests.test_project_status_report.ProjectStatusReportTests.test_json_cli_reports_project_status`.
- Green:
  `python -m unittest tests.test_project_status_report tests.test_suite_selection`.
- Run `tests.test_handoff_status` if the payload nesting affects handoff
  expectations.
- Live JSON assertion:
  `python -m autarkic_systems.project_status --format json`.
- Assert schema `23`, `accepted is True`, no formal-confidence failed subjects,
  and the top-level validation summary includes the expected count, subject,
  and compact label.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Parse any changed JSON files with `python -m json.tool`.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_project_status_report.ProjectStatusReportTests.test_status_payload_summarizes_evidence_registries_and_frontier tests.test_project_status_report.ProjectStatusReportTests.test_status_payload_exposes_derived_formal_confidence_validation_summary tests.test_project_status_report.ProjectStatusReportTests.test_json_cli_reports_project_status
```

It failed in all three expected places: the payload and JSON CLI still reported
schema version `22` instead of `23`, and the new derived-summary test could not
find top-level `formal_confidence_validation`. The red run executed 3 tests in
183.176s.

The implementation stayed in `autarkic_systems.project_status`. It bumps
`PROJECT_STATUS_SCHEMA_VERSION` to `23` and derives
`formal_confidence_validation` from the existing nested
`formal_confidence.results` list. The derived field reports 19 accepted
validations, 0 failed validations, the accepted
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
subject, and the compact `fixed_point_construction_frontier_status` label. The
nested `formal_confidence` key set and text output remain unchanged.

The exact red run then passed:

```text
Ran 3 tests in 176.689s
OK
```

Focused verification passed:

```sh
python -m unittest tests.test_project_status_report tests.test_suite_selection
```

Observed result:

```text
Ran 93 tests in 349.269s
OK
```

The live JSON assertion ran:

```sh
python -m autarkic_systems.project_status --format json
```

It completed in 176.65s and confirmed `schema_version == 23`,
`accepted is True`, no formal-confidence failed subjects, 19 accepted
validations, 0 failed validations, the accepted frontier subject, and the
compact frontier label.

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

`compileall` completed in 0.69s. No JSON files changed in this slice, so there
were no changed JSON files to parse with `json.tool`. The fast suite reported
manifest `as-test-suite-selection-v1`, suite `fast`, 129 modules, and 1171
tests passed in 233.412s.

This is a derived JSON presentation improvement only. It does not change
formal-confidence semantics, project-status acceptance semantics, proof
status, blockers, fixed-point validators, substitution graph validators, or the
nested `formal_confidence` payload.
