# ADR-0208: Sequence SVG Evidence Link

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0207 added a renderer-locked SVG view for the checked post-handoff
sequence trace. The network-sequence evidence bundle now validates the trace,
but not the rendered SVG. That leaves the visual artifact outside the
claim-to-evidence path even though it is a checked projection of the same
trace.

As with transition-chain evidence bundles, the visual render should be part of
the integrated evidence surface once it exists. If the SVG drifts from the
renderer or disappears, bundle validation and the vertical demo should expose
that failure.

## Decision

Add the post-handoff sequence SVG as an explicit evidence-bundle artifact:

- add `sequence_svg` to the checked bundle artifact list;
- load it into `NetworkSequenceEvidenceBundle.sequence_svg_path`;
- include it in schema path validation;
- validate it with `autarkic_systems.network_sequence_svg` against the checked
  sequence trace;
- include a `sequence-svg` validation result; and
- render it in the vertical network-sequence demo report.

This does not add runtime behavior, claims, proof rules, project-status fields,
scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because loaded bundles have no
  `sequence_svg_path`, the validation result set lacks `sequence-svg`, missing
  SVG paths are not rejected by bundle validation, reports omit
  `OK sequence-svg:`, and the demo omits the SVG layer.
- The checked bundle records
  `schematics/sequences/post_handoff_signal_sequence_trace.svg`.
- Bundle text/JSON validation includes accepted `sequence-svg`.
- Missing or invalid SVG input rejects the evidence bundle.
- The demo report lists the sequence SVG layer and path.
- Registry validation remains green.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_evidence_bundle tests.test_network_sequence_demo_report`.
- Green: the same focused suites pass after implementation.
- Regression: run adjacent post-handoff sequence SVG/trace/demo/evidence tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_evidence_bundle.py`,
`autarkic_systems/network_sequence_demo.py`, and
`evidence/sequences/post_handoff_signal_bundle.json`, with documentation in
`docs/network-sequence-evidence-bundles.md` and
`docs/network-sequence-demo-report.md`.

The red focused run failed as intended because loaded bundles had no
`sequence_svg_path`, the validation result set lacked `sequence-svg`, missing
SVG paths were not rejected by bundle validation, reports lacked
`OK sequence-svg:`, and the demo omitted the SVG layer.

The green focused run passed 26 sequence evidence-bundle and demo-report tests
after the bundle loader, schema check, validation report, and vertical demo
were linked to the checked sequence SVG. Adjacent sequence
evidence/demo/SVG/trace/witness tests passed 47 tests. Live bundle JSON
reported 10 accepted checks including `sequence-svg`, and demo JSON listed both
sequence trace and SVG evidence layers with `exists: true`. Registry demo JSON
reported `bundle_count: 1`, `accepted_count: 1`, and no missing evidence paths.
The full default suite passed 892 tests.
