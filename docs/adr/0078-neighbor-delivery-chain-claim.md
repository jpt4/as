# ADR-0078: Neighbor Delivery Chain Claim

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0077 added an executable two-step handoff from a stem neighbor-delivery
transition into recipient init-family command consumption. That helper is more
than a single Universal Cell transition: it runs a sender step, installs the
delivered output tuple into an empty recipient upstream tuple, and runs a
recipient step.

The existing `claims/transition_claims.json` and
`language/transition_claim_language.json` intentionally cover single
transition predicates of the form `predicate(before_cell, step_result)`.
Forcing a two-step chain into that schema would hide the handoff state and
weaken the language boundary.

The chain should instead receive its own small manifest and proof-certificate
surface, using the same manifest-example discipline while keeping the chain
shape explicit.

## Decision

Add a transition-chain claim surface for the ADR-0077 helper:

- `claims/transition_chain_claims.json`;
- `claims/transition_chain_proof_certificates.json`;
- `autarkic_systems/transition_chain_predicates.py`; and
- `autarkic_systems/chain_claims.py`.

The first claim is
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`, checked by
`neighbor_delivery_consumed_by_recipient`.

The manifest examples will cover:

- accepted `neighbor-b/proc-l-init` delivery into an empty recipient;
- sender precondition failure when the sender does not deliver;
- recipient readiness failure when upstream is already occupied; and
- delivered non-init command-token rejection.

This ADR does not add new Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the chain-claim loader or
  manifest is absent.
- The chain claim manifest names the new claim, predicate, and executable
  examples.
- Chain claim evaluation proves the positive example holds and the boundary
  examples do not.
- Chain proof certificates cover every manifest example with
  `manifest-example` steps.
- Runtime single-cell behavior and the ADR-0077 chain helper remain unchanged.

## Consequences

AS now has a distinct claim/proof surface for two-step handoff behavior without
pretending it is a single transition. Later chain language or evidence-bundle
work can build on this surface if multi-step artifacts multiply.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_claim` fails
  before the chain-claim module and manifest exist.
- Green: the same focused test passes after adding the manifest, predicate,
  loader, evaluator, and certificate verifier.
- Regression: run ADR-0077 chain tests, adjacent recipient/neighbor tests, and
  the full default suite before commit.

## After Action Report

Implemented in `claims/transition_chain_claims.json`,
`claims/transition_chain_proof_certificates.json`,
`autarkic_systems/transition_chain_predicates.py`, and
`autarkic_systems/chain_claims.py`.

The focused red run failed because `autarkic_systems.chain_claims` was absent.
The green implementation adds a separate chain-claim loader, evaluator, and
manifest-example certificate verifier for the ADR-0077 two-step handoff.

The claim surface deliberately remains separate from
`claims/transition_claims.json` and `language/transition_claim_language.json`,
because this claim is not a single `predicate(before_cell, step_result)`
transition. The transition-claim language note now records that boundary.

The positive chain example proves a completed `neighbor-b/proc-l-init`
delivery can be installed as an empty recipient's upstream tuple and consumed
through existing recipient init-family command logic. The negative examples
cover sender-not-delivered, recipient-not-ready, and delivered non-init
command-token boundaries.

Runtime single-cell behavior and the ADR-0077 chain helper remain unchanged.

Verification passed:

- focused red:
  `python -m unittest tests.test_neighbor_delivery_chain_claim` failed before
  the module was added;
- focused green:
  `python -m unittest tests.test_neighbor_delivery_chain_claim` passed 5 tests;
- adjacent chain/object-language/proof stack passed 21 tests;
- JSON parsing passed for the chain claim and chain certificate manifests;
- `py_compile` passed for the new modules and focused test;
- `git diff --check` passed;
- `python -m unittest discover` passed 459 tests; and
- the evidence registry JSON CLI still reported `accepted: true` and
  `bundle_count: 8`.
