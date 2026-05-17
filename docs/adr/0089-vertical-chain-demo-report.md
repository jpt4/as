# ADR-0089: Vertical Chain Demo Report

Date: 2026-05-17

## Status

Accepted.

## Context

The neighbor delivery recipient-consumption chain is now represented across
many small artifacts: executable transition code, transition-chain claims,
proof certificates, object-language manifests, evidence bundles, a chain trace,
an SVG render, and source-status boundaries.

That decomposition is useful for auditability, but it is not yet a good first
run surface for someone asking whether the project is producing an integrated
artifact rather than only accumulating process records.

## Decision

Add a small vertical demo report for a single transition-chain evidence bundle.
The report will not invent new validation semantics. It will load the existing
chain evidence bundle, run the existing validator, and present one compact
claim-to-evidence view with:

- the chain claim, predicate, positive example, chain function, and expected
  status;
- accepted status, result count, and failed subjects;
- chain claim/proof/language/trace/SVG artifact paths;
- underlying transition bundle paths;
- source-status boundary paths; and
- explicit boundary terms.

Expose the report both as text for humans and JSON for automation.

## Success Criteria

- Red tests fail before implementation because no vertical chain demo module
  exists.
- The demo payload names the checked-in neighbor delivery chain bundle and all
  required evidence layers.
- The text report gives an inspectable claim-to-evidence summary without
  requiring callers to know the internal bundle schema.
- JSON mode emits the same accepted status, failed subjects, and evidence
  layers.
- Drifted bundle input returns a failing report and preserves rejected subjects
  instead of hiding validation failure.
- Existing chain evidence validation and full repository tests remain green.

## Consequences

The current transition-chain work gains a visible operator/demo surface while
staying anchored to the existing validator rather than duplicating semantics.

## Test Plan

- Red: `python -m unittest tests.test_chain_demo_report` fails before the
  module exists.
- Green: the same focused test passes after implementation.
- Regression: run adjacent chain evidence tests, demo CLI text/JSON checks,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented `autarkic_systems.chain_demo` as a thin reporting layer over the
existing transition-chain evidence bundle validator.

The red focused run, before implementation, failed in
`tests.test_chain_demo_report` because `autarkic_systems.chain_demo` did not
exist. After implementation:

- `python -m unittest tests.test_chain_demo_report` passed 6 tests.
- `python -m unittest tests.test_chain_demo_report tests.test_neighbor_delivery_chain_evidence_bundle tests.test_chain_evidence_bundle_registry tests.test_chain_evidence_cli_target_selection`
  passed 30 tests.
- `python -m autarkic_systems.chain_demo` printed the claim, predicate,
  example, chain helper, validation status, trace, SVG, two transition
  bundles, five source-status boundaries, and explicit boundary terms.
- `python -m autarkic_systems.chain_demo --format json` reported
  `accepted: true`, `validation.result_count: 9`, and
  `validation.failed_subjects: []`.
- `python -m py_compile autarkic_systems/chain_demo.py tests/test_chain_demo_report.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 514 tests.

The report makes the current transition-chain evidence stack easier to inspect
without weakening the source-of-truth validator boundary.
