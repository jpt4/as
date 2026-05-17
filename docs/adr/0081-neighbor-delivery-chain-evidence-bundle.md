# ADR-0081: Neighbor Delivery Chain Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0077 made the first executable two-step transition chain from neighbor
command-buffer delivery into recipient init-family command consumption.
ADR-0078 through ADR-0080 then added a chain claim, proof certificate, chain
object language, and operator-facing claim CLI.

The resulting chain is validated, but its evidence remains spread across the
chain claim surface, the transition claim surface, the two underlying
single-transition evidence bundles, and several source-status blockers. AS
agents need a single artifact that says exactly which chain is being claimed,
which lower-level transition bundles support it, and which command-semantics
boundaries remain unresolved.

## Decision

Add a separate transition-chain evidence bundle under `evidence/chains/` rather
than adding it to the top-level transition evidence registry. The existing
`evidence/manifest.json` registry is a closed index over single-transition
`*_bundle.json` siblings; chain evidence composes those artifacts and should
not be mistaken for another single-transition bundle.

The bundle will connect:

- the `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED` chain claim;
- the chain proof certificate and chain object-language manifest;
- the chain-claim validator module;
- the neighbor command-buffer delivery transition bundle;
- the recipient init command-message transition bundle; and
- the source-status documents that keep non-init, standard-signal, and
  write-buffer command-token semantics blocked.

Add `autarkic_systems/chain_evidence_bundle.py` so the bundle can be loaded,
validated, formatted as text, emitted as JSON, and run directly from the
command line.

This ADR does not add a scheduler, topology model, new Universal Cell behavior,
or a new transition claim.

## Success Criteria

- Red tests fail before implementation because the chain evidence bundle module
  and bundle file are absent.
- The bundle records the chain claim ID, predicate, positive example, chain
  helper name, and expected chain status.
- Validation checks the chain example against the executable chain helper and
  predicate.
- Validation checks chain proof certificates, chain language, source-status
  files, and both underlying single-transition evidence bundles.
- Drifted expected chain status is rejected.
- The module command returns `0` for the checked-in bundle and can emit JSON.
- Existing chain claim/language tests and the top-level transition evidence
  registry remain green.

## Consequences

The first transition chain now has an inspectable evidence object comparable
to the single-transition bundles, while preserving the boundary between
single-transition evidence and composed-chain evidence.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle`
  fails before the module and bundle exist.
- Green: the same focused test passes after adding the bundle validator.
- Regression: run the adjacent chain claim/language/transition-bundle tests,
  both chain evidence CLI modes, the existing top-level evidence registry CLI,
  and the full default suite before commit.

## After Action Report

Implemented in `evidence/chains/neighbor_delivery_chain_bundle.json` and
`autarkic_systems/chain_evidence_bundle.py`, with focused tests in
`tests/test_neighbor_delivery_chain_evidence_bundle.py`.

The focused red run failed because `autarkic_systems.chain_evidence_bundle`
was absent. The green implementation adds a composed-chain bundle validator
over seven subjects:

- `schema`;
- `chain-claim-example`;
- `chain-proof-certificate`;
- `chain-language`;
- `underlying-transition-bundles`;
- `source-statuses`; and
- `boundary`.

The bundle is stored under `evidence/chains/` so the top-level
`evidence/manifest.json` closed index remains limited to single-transition
evidence bundles.

The command now supports the checked-in default:

```sh
python -m autarkic_systems.chain_evidence_bundle
python -m autarkic_systems.chain_evidence_bundle --format json
```

Verification passed:

- focused red:
  `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle`
  failed before the module was added;
- focused green:
  `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle`
  passed 8 tests;
- adjacent chain/evidence stack passed 60 tests;
- actual chain evidence CLI text mode passed;
- actual chain evidence CLI JSON mode passed with `accepted: true`,
  `chain_claim_id: UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED`, and
  `result_count: 7`;
- the existing transition evidence registry JSON CLI still reported
  `accepted: true` and `bundle_count: 8`;
- `jq` parsed `evidence/chains/neighbor_delivery_chain_bundle.json`;
- `py_compile` passed for the new module and focused test;
- `git diff --check` passed; and
- `python -m unittest discover` passed 479 tests.
