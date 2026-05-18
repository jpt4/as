# ADR-0187: Chain Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0186 migrated every checked base transition proof
certificate from implicit `manifest-example` steps to explicit
`predicate-result` steps. The transition-chain proof-certificate manifest still
uses only `manifest-example` steps, and the chain object language currently only
admits that rule.

The chain claims already name explicit predicates:
`neighbor_delivery_consumed_by_recipient` and
`neighbor_delivery_rejected_by_recipient`. The chain verifier can therefore use
the same predicate-named proof-object discipline now used by the base transition
surface.

## Decision

Add `predicate-result` proof-step support to the transition-chain certificate
verifier and chain object language, then migrate both checked chain certificates
to `predicate-result` steps that explicitly name their chain predicates.

## Success Criteria

- Red tests fail before implementation because the checked chain certificate
  manifest still uses `manifest-example`, the chain verifier reports
  manifest-example details, and the chain language only admits
  `manifest-example`.
- `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED` has exactly six
  `predicate-result` proof steps naming
  `neighbor_delivery_consumed_by_recipient`.
- `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED` has exactly three
  `predicate-result` proof steps naming
  `neighbor_delivery_rejected_by_recipient`.
- The chain verifier rejects missing or mismatched predicate metadata on
  `predicate-result` steps.
- The chain object language admits `predicate-result` proof rules.
- Chain claim text/JSON, chain object-language text/JSON, and aggregate
  project-status output accept the updated surface.
- The checked chain proof-certificate manifest no longer contains
  `manifest-example` rules.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_neighbor_delivery_chain_claim tests.test_transition_chain_claim_cli tests.test_chain_object_language tests.test_project_status_report`
  fails before verifier/language/manifest updates.
- Green: the same focused suite passes after implementing verifier support and
  updating the chain proof-certificate and language manifests.
- Regression: run JSON parsing for touched JSON, chain-claim CLI JSON, chain
  object-language CLI JSON, project-status JSON, `compileall`,
  `git diff --check`, a direct check that chain proof certificates contain no
  `manifest-example` rules, and the full default suite before commit.

## After Action Report

Implemented. The focused red run
`python -m unittest tests.test_neighbor_delivery_chain_claim tests.test_transition_chain_claim_cli tests.test_chain_object_language tests.test_project_status_report`
ran 104 tests and failed because the chain verifier still rejected
`predicate-result` steps, the chain object language still lacked the
`predicate-result` proof-object rule, the checked chain certificates still used
`manifest-example`, and project status still reported 28 chain language clauses.

The implementation added `predicate-result` support to
`autarkic_systems/chain_claims.py`, including required predicate metadata,
predicate-name mismatch checks, predicate result-name checks, and rule-count
details. It added `predicate-result` to the chain proof-object language and
migrated both checked chain proof certificates to predicate-named steps. No
runtime behavior, transition-chain claims, chain evidence bundles,
source-status records, or status schema versions changed.

The same focused suite then passed with 104 tests. The chain-claim CLI JSON,
chain object-language CLI JSON, and project-status JSON checks accepted the
updated surface. JSON parsing for the touched chain proof-certificate and
language manifests, `compileall`, `git diff --check`, and the full default suite
also passed; the full suite ran 788 tests. A direct `rg` check confirmed the
checked chain proof-certificate manifest no longer contains `manifest-example`
rules.
