# ADR-0066: Evidence Bundle Registry

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0065 added the first transition evidence bundle. That bundle is useful, but
it currently has to be discovered by knowing its exact path under `evidence/`.
As AS adds more bundles, the project needs one registry that future agents can
load and validate to answer "which evidence paths exist, and are they still
green?".

## Decision

Add `evidence/manifest.json` as the project registry for transition evidence
bundles.

Extend `autarkic_systems/evidence_bundle.py` with registry loading and
validation. The registry validator will check:

- schema version and non-empty registry metadata;
- unique bundle IDs and paths;
- every registered bundle path exists and loads;
- each registry entry agrees with the loaded bundle's ID, claim ID, and
  expected status; and
- each registered bundle passes the ADR-0065 cross-layer validation.

This ADR does not add any new Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the registry loader is absent.
- `evidence/manifest.json` records the ADR-0065 recipient init evidence bundle.
- Tests prove the registry loads with the expected bundle entry.
- Tests prove the registry validates all registered bundles through the bundle
  validator.
- Tests reject duplicate bundle IDs and missing bundle paths.
- Runtime behavior remains unchanged.

## Consequences

Evidence bundles become an indexed project surface rather than isolated files.
Future bundle-producing ADRs should add entries to `evidence/manifest.json` and
keep the registry test green.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_registry` fails before
  registry loader support exists.
- Green: the same focused test passes after adding the registry artifact and
  validator.
- Regression: run ADR-0065 bundle tests, recipient source-status tests, and
  the full default suite before commit.

## After Action Report

Implemented in `evidence/manifest.json` and
`autarkic_systems/evidence_bundle.py`.

The focused red run failed because `load_evidence_bundle_registry` was absent
from `autarkic_systems.evidence_bundle`. The green implementation adds a
registry containing the ADR-0065 recipient init transition evidence bundle and
extends the bundle module with registry dataclasses, loading, duplicate
detection, missing-path detection, entry-to-bundle agreement checks, and
whole-bundle validation.

Runtime behavior remains unchanged. The registry is an index and
batch-validation surface over already recorded evidence bundles.
