# ADR-0204: Network Sequence Demo Report

Date: 2026-05-18

## Status

Accepted.

## Context

The network-sequence layer now has an executable post-handoff witness, a named
sequence claim, proof certificates, an explicit object language, and a checked
evidence bundle. The validation commands are precise, but the layer lacks the
kind of one-command vertical demo surface already available for
transition-chain evidence.

This is a legibility problem, not a semantic gap. Operators should be able to
see the current post-handoff claim-to-evidence path without knowing the bundle
JSON schema or manually composing the validator outputs.

## Decision

Add `autarkic_systems.network_sequence_demo` as a reporting layer over the
existing network-sequence evidence-bundle validators. The demo will:

- build a single-bundle report for the checked post-handoff signal sequence;
- list the sequence claim, proof, language, validator, witness, underlying
  chain bundles, source-status records, and boundary text;
- include artifact-presence flags and a `missing_evidence_paths` summary;
- expose text and JSON output; and
- add registry mode that summarizes every registered network-sequence bundle.

This ADR does not add runtime behavior, claims, proof rules, validators,
project-status fields, scheduler, topology, timing, traces, SVGs, or command
semantics. Acceptance remains delegated to
`autarkic_systems.network_sequence_evidence_bundle`.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_sequence_demo` does not exist.
- The checked single-bundle report is accepted and names every evidence layer.
- Missing artifact paths appear in `missing_evidence_paths` with `exists:
  false`.
- Text mode summarizes validation, failed subjects, missing paths, artifact
  layers, and boundary terms.
- JSON mode preserves the same validation and evidence-layer data.
- Registry mode reports bundle count, accepted count, failed count, missing
  paths, and per-bundle reports.
- Drifted bundles preserve validation failed subjects instead of hiding them.
- Existing network-sequence evidence validation and full repository tests
  remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_demo_report`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent network-sequence demo/evidence/language/claim tests,
  demo CLI text/JSON checks, `python -m compileall -q autarkic_systems tests`,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_demo.py`, with operator
notes in `docs/network-sequence-demo-report.md`.

The red focused run failed as intended because
`autarkic_systems.network_sequence_demo` did not exist. The green focused run
passed 13 tests after the demo delegated acceptance to the existing
network-sequence evidence-bundle validator and added text/JSON reports for one
bundle or the registry.

Adjacent demo/evidence/language/claim tests passed 46 tests. Live text output
named the post-handoff sequence claim, language, witness, one chain bundle,
five source-status boundaries, and explicit boundary terms. Live JSON output
reported `accepted: true`, 8 validation checks, all evidence layers present,
and registry `bundle_count: 1`. The full default suite passed 876 tests.
