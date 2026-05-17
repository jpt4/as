# ADR-0093: Neighbor Delivery Rejection Chain SVG

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0092 records the delivered non-init rejection chain as a checked JSON
trace. The positive consumed handoff already has a renderer-locked SVG, but
the rejection path does not.

Rendering the rejection trace makes the negative boundary inspectable in the
same visual layer as the green path. The renderer also needs to stop assuming
all handoffs use channel 1, because the rejection trace delivers
`write-buf-one` on output/upstream channel 2.

## Decision

Add `schematics/chains/neighbor_delivery_rejection_chain_trace.svg`, generated
from `schematics/chains/neighbor_delivery_rejection_chain_trace.json`.

Update the chain SVG renderer and validator so the visible handoff channel is
derived from the delivered tuple rather than hard-coded to index 1.

## Success Criteria

- Red tests fail before implementation because the rejection SVG artifact
  constant and committed SVG are missing.
- The rejection SVG records the rejection claim, `recipient-not-consumed`
  status, channel-2 handoff, delivered tuple, and recipient rejection step.
- The committed rejection SVG exactly matches renderer output.
- The SVG validator accepts both consumed and rejected committed SVGs.
- Existing chain trace, evidence bundle, and full repository tests remain
  green.

## Consequences

Both current transition-chain claims now have trace and visual layers, while
non-init command execution remains explicitly blocked.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_svg` fails
  before the rejection SVG constant/artifact exist.
- Green: the focused SVG test passes after implementation.
- Regression: run chain trace/evidence tests, chain evidence JSON CLI,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented the rejection chain SVG and made the renderer derive handoff
channel labels from trace data.

The red focused run, before implementation, failed in
`tests.test_neighbor_delivery_chain_svg` because
`NEIGHBOR_DELIVERY_REJECTION_CHAIN_SVG_ARTIFACT` did not exist. The first
implementation pass also exposed the hard-coded channel-1 handoff label, which
was corrected before adding the committed SVG. After implementation:

- `python -m unittest tests.test_neighbor_delivery_chain_svg` passed 9 tests.
- `python -m unittest tests.test_neighbor_delivery_chain_svg tests.test_neighbor_delivery_chain_trace tests.test_neighbor_delivery_chain_evidence_bundle`
  passed 30 tests.
- `python -m unittest tests.test_chain_evidence_bundle_registry tests.test_chain_demo_report`
  passed 19 tests.
- `python -m autarkic_systems.chain_evidence_bundle --format json` remained
  accepted with `result_count: 9` and `failed_subjects: []`.
- `python -m py_compile autarkic_systems/chain_svg.py tests/test_neighbor_delivery_chain_svg.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 525 tests.

The consumed and rejected chain traces now both have renderer-locked SVG views.
