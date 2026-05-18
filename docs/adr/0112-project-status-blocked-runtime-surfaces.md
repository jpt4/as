# ADR-0112: Project Status Blocked Runtime Surfaces

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0111 made project status a usable blocker work queue by carrying
summary-bearing resolution questions. The same source-status records already
name the runtime surfaces where unresolved command-token semantics remain
blocked, for example recipient command-message input, self-mailbox command
state, and self-target command-buffer dispatch.

Project status currently drops those surfaces. It can tell an operator what
command tokens are blocked and what questions need resolution, but not where
in the runtime those questions apply without a second source-status file pass.

## Decision

Add a `blocked_runtime_surfaces` list to each accepted
`frontier.source_statuses` entry in project status JSON. Source-status records
without the field report an empty list.

Because this adds a JSON field to accepted source-status entries, bump
`PROJECT_STATUS_SCHEMA_VERSION` from `4` to `5`.

The text report will add a `Blocked runtime surfaces:` section. Source-status
entries with no blocked runtime surfaces are omitted from that section; if no
accepted entry has surfaces, the section reports `none`.

Since project status will now recognize `blocked_runtime_surfaces`, it must
also validate the field when present. The field must be a list of non-empty
text entries.

## Success Criteria

- Red tests fail before implementation because project status remains
  `schema_version: 4`, lacks `blocked_runtime_surfaces`, and text output omits
  the surface section.
- In-process status reports include `schema_version: 5`.
- JSON CLI output includes `schema_version: 5`.
- Accepted standard-signal and write-buffer source-status entries expose their
  blocked runtime surfaces.
- The default text report names blocked runtime surfaces under the contributing
  command labels.
- Malformed `blocked_runtime_surfaces` fields report
  `frontier.failed_subjects: ["source-status-schema"]`.
- Existing registry, command-token, resolution-question, and source-status
  failure behavior remains unchanged.

## Consequences

Project status now reports not only the blocked terms and decision questions,
but also the runtime boundaries where those questions matter. This makes the
safe next slice more explicit without widening command-token execution
semantics.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  blocked-runtime-surface status contract exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI text and JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because project status still emitted `schema_version: 4`, did not expose
per-source `blocked_runtime_surfaces`, text output omitted the blocked runtime
surface section, and malformed surface lists were accepted.

`autarkic_systems.project_status` now emits `schema_version: 5` and includes
`blocked_runtime_surfaces` on each accepted `frontier.source_statuses` entry.
The default text report renders blocked runtime surfaces under the contributing
command label. Malformed `blocked_runtime_surfaces` fields now report
`source-status-schema`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 33 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 58 tests.
- `python -m autarkic_systems.project_status` reported accepted transition
  evidence with 8 bundles, accepted chain evidence with 2 bundles, blocked
  commands `standard-signal`, `write-buf-zero`, and `write-buf-one`, blocked
  runtime surfaces for standard-signal and write-buffer blockers, and
  summary-bearing resolution-question lines.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 5`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution,
  per-source `blocked_runtime_surfaces`, preserved
  `required_resolution_questions` ID lists, summary-bearing
  `resolution_questions`, and `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 569 tests.
