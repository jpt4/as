# ADR-0288: Project Status Formal Confidence Validation Summary

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0286 made aggregate formal-confidence validation consume the compact
fixed-point construction frontier status. ADR-0287 then made that validation
safe to reuse inside repeated project-status checks by adding a process-local
cache.

Project status already includes the full formal-confidence JSON payload and a
compact target-status line. That line says the target is blocked, but it does
not make the validation surface itself visible to operators. In particular,
the accepted
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
result can only be found by inspecting JSON output or running the
formal-confidence command directly.

The full status text and compact handoff summary should expose that validation
surface without changing the formal-confidence payload shape or promoting any
proof boundary.

## Decision

Extend `autarkic_systems.project_status` text formatting with a derived
formal-confidence validation summary. The summary is computed from the
existing `formal_confidence.results` list:

- accepted validation count;
- failed validation count; and
- the accepted `fixed_point_construction_frontier_status` validation subject.

Render the full project-status text with the complete accepted subject, and
render compact summary mode with the shorter frontier dependency field name so
handoff text stays small.

Do not change formal-confidence target validation, fixed-point validators,
aggregate project-status acceptance semantics, JSON payload shape, or
`PROJECT_STATUS_SCHEMA_VERSION`.

## Success Criteria

- Red tests fail before implementation because project-status text and summary
  omit the formal-confidence validation count and frontier dependency subject.
- Full project-status text reports accepted and failed formal-confidence
  validation counts and includes the accepted
  `AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
  subject.
- Compact project-status summary, and therefore handoff text, reports the same
  validation counts and a compact
  `fixed_point_construction_frontier_status accepted` dependency note.
- Project-status JSON remains schema version `22` and preserves the existing
  `formal_confidence` payload shape.
- No target semantics, blockers, proof status, or fixed-point validator
  behavior changes.

## Test Plan

- Red:
  `python -m unittest tests.test_project_status_report.ProjectStatusReportTests.test_text_status_names_green_evidence_and_blocked_commands tests.test_project_status_report.ProjectStatusReportTests.test_summary_status_formats_operator_digest tests.test_handoff_status.HandoffStatusTests.test_handoff_payload_combines_project_and_submission_status`.
- Green:
  `python -m unittest tests.test_project_status_report tests.test_handoff_status tests.test_suite_selection`.
- Live project-status text and JSON smoke:
  `python -m autarkic_systems.project_status` and
  `python -m autarkic_systems.project_status --format json`.
- Confirm the JSON smoke still reports schema version `22` and an accepted
  `AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
  result without adding derived JSON fields.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

The focused red run was:

```sh
python -m unittest tests.test_project_status_report.ProjectStatusReportTests.test_text_status_names_green_evidence_and_blocked_commands tests.test_project_status_report.ProjectStatusReportTests.test_summary_status_formats_operator_digest tests.test_handoff_status.HandoffStatusTests.test_handoff_payload_combines_project_and_submission_status
```

It failed in all three expected places: full project-status text lacked the
formal-confidence validation line, compact project-status summary lacked the
new line, and the handoff payload inherited that missing compact summary. The
red run executed 3 tests in 184.926s.

The implementation stayed in `autarkic_systems.project_status`. It derives
accepted and failed validation counts from the existing
`formal_confidence.results` list, renders the complete accepted
`AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status`
subject in full text, and renders
`fixed_point_construction_frontier_status accepted` in compact summary mode.
No formal-confidence validator, fixed-point validator, blocker, acceptance, or
JSON payload shape changed.

The exact red trio then passed:

```text
Ran 3 tests in 175.006s
OK
```

The requested focused suite passed:

```text
Ran 100 tests in 501.972s
OK
```

Live smoke checks passed:

```sh
python -m autarkic_systems.project_status
python -m autarkic_systems.project_status --format json
```

The text smoke accepted in 2m36.797s and rendered:

```text
Formal confidence validation: 19 accepted, 0 failed; accepted frontier subject: AS-FORMAL-CONFIDENCE-TARGET-001.fixed_point_construction_frontier_status
```

The JSON smoke accepted in 2m45.518s. A JSON assertion confirmed
`accepted is True`, `schema_version == 22`, unchanged `formal_confidence`
keys, `result_count == 19`, no failed subjects, and the accepted frontier
subject in `formal_confidence.results`.

Additional verification passed:

```text
python -m compileall autarkic_systems tests
git diff --check
python -m autarkic_systems.test_suite_selection --suite fast
```

`compileall` completed in 0.871s. No JSON files changed in this slice, so
there were no changed JSON files to parse with `json.tool`. The fast suite
reported manifest `as-test-suite-selection-v1`, suite `fast`, 129 modules,
and 1170 tests passed in 239.525s.

This remains a status-presentation improvement only. It does not prove or
promote substitution representability, substitution graph correctness, bridge
equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.
