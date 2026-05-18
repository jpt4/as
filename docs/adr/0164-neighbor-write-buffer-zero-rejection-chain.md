# ADR-0164: Neighbor Write-Buffer Zero Rejection Chain Coverage

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0091 added the rejected neighbor-delivery chain claim for a delivered
non-init command token. The current positive rejected-chain example exercises
neighbor delivery of `write-buf-one`.

ADR-0163 made the single-transition recipient rejection claim explicit for
both delivered `write-buf-zero` and `write-buf-one` command messages. The
transition-chain claim surface should now make the corresponding delivered
`write-buf-zero` handoff explicit too, so the composed-chain layer does not
lag behind the base recipient rejection coverage.

## Decision

Add a neighbor-delivered `write-buf-zero` chain example to the existing
transition-chain claim surface:

- as a negative example for
  `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`, proving the delivered token
  is not consumed as init-family behavior; and
- as a positive example for
  `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`, proving the delivered token
  is rejected through the recipient non-init boundary.

This ADR does not add new runtime behavior, chain traces, SVGs, or evidence
bundles. The existing rejection-chain trace remains the primary
`write-buf-one` witness.

## Success Criteria

- Red tests fail before implementation because the `write-buf-zero` chain
  examples are absent from the chain claim and proof-certificate manifests.
- The chain helper demonstrates a completed neighbor-c `write-buf-zero`
  delivery that the recipient rejects as `recipient-not-consumed`.
- The consumed chain claim includes the `write-buf-zero` delivery as a negative
  example.
- The rejected chain claim includes the `write-buf-zero` delivery as a
  positive example.
- The chain proof certificate covers both new examples.
- Chain claim CLI and project status report nine chain examples.
- Runtime behavior and existing chain trace/SVG/evidence artifacts remain
  unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_neighbor_delivery_recipient_chain tests.test_neighbor_delivery_chain_claim tests.test_transition_chain_claim_cli tests.test_project_status_report`
  fails before the chain manifest and proof-certificate coverage are updated.
- Green: the same focused suite passes after updating the manifests and docs.
- Regression: run chain-claim JSON, project-status JSON, JSON parsing for
  touched files, `compileall`, `git diff --check`, and the full default suite
  before commit.

## After Action Report

Implemented.

The focused red run failed before implementation because the delivered
`write-buf-zero` chain examples were absent from
`claims/transition_chain_claims.json`, absent from
`claims/transition_chain_proof_certificates.json`, and the chain claim
CLI/project-status surfaces still reported seven evaluated examples.

The implementation adds a completed neighbor-c `write-buf-zero` handoff test,
a negative consumed-chain example, a positive rejected-chain example, and
matching proof-certificate steps. The sender uses buffer `1111` plus a
non-matching input/control rail to complete command value `30`, delivering
`write-buf-zero` to the neighbor-c output channel. The recipient then rejects
the installed upstream command through the existing non-init boundary.

Runtime behavior, chain traces, SVG artifacts, evidence bundles,
project-status schema `15`, and source-status frontier schema `2` are
unchanged. Chain claim validation now evaluates nine examples.

Verification passed:

- focused red suite failed before implementation as expected;
- focused green suite passed 93 tests;
- adjacent chain helper/claim/CLI/project-status/object-language suite passed
  105 tests;
- `python -m autarkic_systems.chain_claims --format json` accepted two chain
  claims and reported nine evaluated examples;
- `python -m autarkic_systems.project_status --format json` accepted schema
  `15` with the same chain-claim coverage;
- JSON parsing passed for the touched chain claim/proof manifests;
- `python -m compileall -q autarkic_systems tests` passed;
- `git diff --check` passed; and
- `python -m unittest discover` ran 731 tests.
