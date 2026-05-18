# ADR-0206: Sequence Trace Evidence Link

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0205 added a checked post-handoff sequence trace artifact and validator.
The network-sequence evidence bundle still predates that trace: it cites and
validates the sequence claim, proof certificate, object language, executable
witness, underlying chain bundle, and source-status boundaries, but not
`schematics/sequences/post_handoff_signal_sequence_trace.json`.

Evidence bundles should expose every checked artifact layer that makes the
claimed behavior auditable. If the sequence trace drifts or disappears, the
bundle and vertical demo should fail rather than letting the trace sit beside
the evidence path as an unchecked side artifact.

## Decision

Add the post-handoff sequence trace as an explicit evidence-bundle artifact:

- add `sequence_trace` to the checked bundle artifact list;
- load it into `NetworkSequenceEvidenceBundle.sequence_trace_path`;
- include it in schema path validation;
- validate it with `autarkic_systems.network_sequence_trace`;
- ensure the trace agrees with the bundle claim ID, helper, and expected
  status; and
- render it in the vertical network-sequence demo report.

This does not add runtime behavior, claims, proof rules, project-status fields,
scheduler, topology, timing, SVG output, or command semantics.

## Success Criteria

- Red tests fail before implementation because loaded bundles have no
  `sequence_trace_path`, the validation result set lacks `sequence-trace`,
  missing trace paths are not rejected by bundle validation, reports omit
  `OK sequence-trace:`, and the demo omits the trace layer.
- The checked bundle records
  `schematics/sequences/post_handoff_signal_sequence_trace.json`.
- Bundle text/JSON validation includes accepted `sequence-trace`.
- Missing or invalid sequence trace input rejects the evidence bundle.
- The demo report lists the sequence trace layer and path.
- Registry validation remains green.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_evidence_bundle tests.test_network_sequence_demo_report`.
- Green: the same focused suites pass after implementation.
- Regression: run adjacent post-handoff sequence trace/demo/evidence tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_evidence_bundle.py`,
`autarkic_systems/network_sequence_demo.py`, and
`evidence/sequences/post_handoff_signal_bundle.json`, with documentation in
`docs/network-sequence-evidence-bundles.md` and
`docs/network-sequence-demo-report.md`.

The red focused run failed as intended because loaded bundles had no
`sequence_trace_path`, the validation result set lacked `sequence-trace`,
missing trace paths were not rejected by bundle validation, reports lacked
`OK sequence-trace:`, and the demo omitted the trace layer.

The green focused run passed 25 sequence evidence-bundle and demo-report tests
after the bundle loader, schema check, validation report, and vertical demo
were linked to the checked sequence trace. Adjacent sequence
evidence/demo/trace/witness/language/claim tests passed 62 tests. Live bundle
JSON reported 9 accepted checks including `sequence-trace`, and demo JSON
listed the sequence trace evidence layer with `exists: true`. Registry demo
JSON reported `bundle_count: 1`, `accepted_count: 1`, and no missing evidence
paths. The full default suite passed 885 tests.
