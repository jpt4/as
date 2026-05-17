# ADR-0084: Chain Evidence Registry

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0081 through ADR-0083 created the first composed-chain evidence bundle,
chain trace, and chain SVG. The bundle is deliberately separate from the
top-level single-transition evidence registry, but there is still no registry
for discovering chain evidence bundles as a collection.

If more chain bundles are added later, a loose `evidence/chains/` directory
would repeat the same problem ADR-0066 fixed for single-transition bundles:
agents could miss a bundle file, validate only one artifact, or accidentally
leave an unregistered chain bundle beside the manifest.

## Decision

Add a chain evidence registry:

- `evidence/chains/manifest.json`;
- registry loader/validator/report support in
  `autarkic_systems/chain_evidence_bundle.py`; and
- `tests/test_chain_evidence_bundle_registry.py`.

The registry will list transition-chain evidence bundles only. It will not
merge chain bundles into `evidence/manifest.json`, which remains a closed
single-transition evidence index.

The existing chain bundle CLI will keep its single-bundle default, and will
gain `--registry evidence/chains/manifest.json` for batch validation.

## Success Criteria

- Red tests fail before implementation because the chain registry loader,
  report functions, CLI flag, and manifest are absent.
- The registry records the neighbor delivery recipient chain evidence bundle.
- Registry validation checks schema, duplicate IDs/paths, missing bundle paths,
  bundle entry agreement, full bundle validation, and closed-index completeness
  over sibling `*_bundle.json` files in `evidence/chains/`.
- The CLI can validate the checked-in registry in text and JSON modes.
- Existing single-bundle chain evidence validation, top-level transition
  evidence registry validation, and the full suite remain green.

## Consequences

Chain evidence becomes discoverable without weakening the boundary between
single-transition evidence and composed-chain evidence. Future chain bundles
must be registered explicitly before the registry will accept the directory.

## Test Plan

- Red: `python -m unittest tests.test_chain_evidence_bundle_registry` fails
  before the registry functions and manifest exist.
- Green: the same focused test passes after adding registry support.
- Regression: run the chain evidence bundle tests, both chain registry CLI
  modes, the existing top-level transition evidence registry CLI, `jq`,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented in `evidence/chains/manifest.json` and
`autarkic_systems/chain_evidence_bundle.py`, with focused tests in
`tests/test_chain_evidence_bundle_registry.py`.

The focused red run failed because the chain registry loader/report functions
were absent from `autarkic_systems.chain_evidence_bundle`.

The green implementation adds a chain-specific registry model with:

- schema and metadata validation;
- duplicate bundle ID/path rejection;
- missing bundle path rejection;
- registry-entry agreement against loaded chain bundles;
- full cross-layer validation for every registered chain bundle;
- closed-index completeness over sibling `*_bundle.json` files in
  `evidence/chains/`;
- text and JSON registry reports; and
- `python -m autarkic_systems.chain_evidence_bundle --registry
  evidence/chains/manifest.json`.

The existing single-bundle CLI default remains unchanged. The top-level
`evidence/manifest.json` remains the closed single-transition evidence
registry.

Verification passed:

- focused red:
  `python -m unittest tests.test_chain_evidence_bundle_registry` failed before
  registry support was added;
- focused green:
  `python -m unittest tests.test_chain_evidence_bundle_registry` passed 10
  tests;
- adjacent chain registry/bundle tests passed 18 tests;
- `python -m autarkic_systems.chain_evidence_bundle --registry
  evidence/chains/manifest.json` passed in text mode;
- `python -m autarkic_systems.chain_evidence_bundle --registry
  evidence/chains/manifest.json --format json` reported `accepted: true` and
  `bundle_count: 1`;
- the existing single-bundle chain evidence JSON CLI still reported
  `accepted: true` and `result_count: 9`;
- the existing transition evidence registry JSON CLI still reported
  `accepted: true` and `bundle_count: 8`;
- `jq` parsed `evidence/chains/manifest.json`;
- `py_compile` passed for the touched module and focused test;
- `git diff --check` passed; and
- `python -m unittest discover` passed 502 tests.
