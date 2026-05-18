# ADR-0210: Network Sequence Demo Registry Failure Detail

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0204 added registry mode to the vertical network-sequence demo report.
Registry JSON includes per-bundle demo reports, and each bundle report carries
its own validation failed subjects. The registry text output, however, only
lists bundle status and missing paths. A registered bundle can therefore be
shown as rejected without naming whether the rejected layer was
`sequence-witness`, `sequence-trace`, `sequence-svg`, or another subject.

After ADR-0209, project status preserves those inner failed subjects. The
demo registry should offer the same operator legibility on the vertical demo
surface.

## Decision

Extend network-sequence demo registry reports with an explicit
`bundle_failed_subjects` summary:

- accepted registry reports expose `bundle_failed_subjects: []`;
- rejected existing bundle reports add a `{bundle_id, failed_subjects}` entry;
- registry text renders `Failed subjects: ...` for rejected bundle reports;
  and
- existing single-bundle demo validation authority remains unchanged.

This does not add runtime behavior, claims, proof rules, evidence-bundle
validation authority, project-status fields, source-status boundaries, trace
or SVG rendering, scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because registry reports lack
  `bundle_failed_subjects` and rejected registry text does not name the inner
  failed subjects.
- Accepted registry JSON reports `bundle_failed_subjects: []`.
- A registry pointing at a drifted existing bundle reports that bundle ID and
  its inner failed subjects in registry JSON.
- Registry text for a rejected existing bundle renders the failed subjects.
- Existing missing-bundle registry behavior remains unchanged.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_demo_report`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent network sequence demo/evidence tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_demo.py`, with focused
coverage in `tests/test_network_sequence_demo_report.py` and operator notes in
`docs/network-sequence-demo-report.md`.

The red focused run failed as intended because registry reports lacked
`bundle_failed_subjects` and the rejected existing-bundle registry text had no
line naming the inner failed subjects.

The implementation derives `bundle_failed_subjects` from the existing
per-bundle validation payloads and renders `Failed subjects: ...` for rejected
existing bundles in registry text. The accepted registry path reports
`bundle_failed_subjects: []`; a temporary registry pointing at a drifted
existing bundle reports
`{"bundle_id": "post-handoff-signal-sequence-evidence-bundle",
"failed_subjects": ["sequence-witness", "sequence-trace"]}`.

Focused network-sequence demo tests passed 14 tests. Adjacent
demo/evidence/project-status tests passed 112 tests. Live registry JSON
reported `accepted: true`, `bundle_count: 1`, and
`bundle_failed_subjects: []`. `compileall`, `git diff --check`, and the full
default suite passed; the full suite ran 895 tests.
