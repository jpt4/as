# ADR-0092: Neighbor Delivery Rejection Chain Trace

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0091 names the delivered non-init recipient rejection boundary as a
transition-chain claim. The project now has a predicate and manifest proof for
that path, but the only recorded composed-chain trace still covers the
successful init-family consumption handoff.

The rejection claim should get a machine-checked trace before any rendered SVG
or evidence bundle work. Otherwise the negative composed path remains less
inspectable than the green path.

## Decision

Add `schematics/chains/neighbor_delivery_rejection_chain_trace.json`, a
two-step chain trace for the non-init delivery rejection path:

- sender completes `neighbor-c/write-buf-one` delivery;
- sender output `["_", "_", "write-buf-one"]` is installed as recipient
  upstream state;
- recipient rejects the non-init command token with `rejected-input`; and
- the whole chain reports `recipient-not-consumed`.

Update the trace validator so a trace can validate an expected rejection status
when the recorded steps, handoff, cells, status, and boundary terms all match
the helper replay.

## Success Criteria

- Red tests fail before implementation because the rejection trace artifact ID
  and trace file are missing.
- The rejection trace loads with claim ID
  `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`.
- The trace records sender delivery, handoff, recipient rejection, and the
  `recipient-not-consumed` chain status.
- The trace validator accepts the rejection trace even though the chain helper
  reports `accepted: false`.
- The existing consumed-handoff trace still validates.

## Consequences

The negative chain claim now has the same first trace layer as the positive
handoff claim, without implementing non-init command execution.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_trace` fails
  before the rejection trace constant and artifact are added.
- Green: the focused trace test passes after implementation.
- Regression: run chain claim and evidence bundle tests,
  `python -m autarkic_systems.chain_evidence_bundle --format json`,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented the delivered non-init rejection chain trace and adjusted trace
validation so an expected rejection status can be a valid recorded replay.

The red focused run, before implementation, failed in
`tests.test_neighbor_delivery_chain_trace` because
`NEIGHBOR_DELIVERY_REJECTION_CHAIN_TRACE_ARTIFACT_ID` did not exist. After
implementation:

- `python -m unittest tests.test_neighbor_delivery_chain_trace` passed 11
  tests.
- `python -m unittest tests.test_neighbor_delivery_chain_trace tests.test_neighbor_delivery_chain_claim tests.test_chain_object_language tests.test_transition_chain_claim_cli`
  passed 31 tests.
- `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle tests.test_chain_evidence_bundle_registry tests.test_chain_demo_report`
  passed 29 tests.
- `python -m autarkic_systems.chain_evidence_bundle --format json` remained
  accepted with `result_count: 9` and `failed_subjects: []`.
- `python -m py_compile autarkic_systems/chain_trace.py tests/test_neighbor_delivery_chain_trace.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 522 tests.

The rejected non-init chain path now has a replay-checked trace artifact while
still refusing non-init command execution semantics.
