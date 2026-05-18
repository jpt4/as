# ADR-0243: Formal Confidence Diagonal Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0242 added the first checked diagonal seed surface, but the aggregate
formal-confidence target still did not validate it. The formal-confidence
manifest could therefore remain accepted even if
`claims/diagonal_construction_targets.json` disappeared or drifted.

Because the current fixed-point frontier has moved from direct quotation
self-embedding toward the substitution-code diagonal seed, the aggregate
formal-confidence boundary should fail closed over that seed.

## Decision

Add a structured `diagonal_construction` configuration field to
`claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate that referenced
diagonal-construction target.

This keeps formal-confidence validation aligned with the current fixed-point
frontier while preserving the blocker on real fixed-point construction.

This does not prove substitution representability, prove the diagonal lemma,
prove a fixed-point equation, implement an arithmetized proof predicate, claim
self-consistency, change runtime behavior, change command semantics, add an
evidence bundle, or alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the checked target has no
  `diagonal_construction` required configuration field, the formal-confidence
  report does not expose an accepted diagonal result, and missing diagonal
  manifests do not reject formal-confidence validation.
- `claims/formal_confidence_targets.json` includes a structured
  `diagonal_construction` path.
- `autarkic_systems.formal_confidence` validates the referenced
  diagonal-construction target with `autarkic_systems.diagonal_construction`.
- Healthy text and JSON reports expose `diagonal construction accepted`.
- Missing or invalid diagonal-construction references fail closed as
  `target-diagonal-construction`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-confidence text/JSON, live project-status
  summary, compileall, JSON checks, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented on 2026-05-18.

The formal-confidence target now carries
`"diagonal_construction": "claims/diagonal_construction_targets.json"`. The
validator loads that manifest, runs the diagonal-construction validator,
reports `diagonal construction accepted` on the healthy path, and maps missing
or invalid references to `target-diagonal-construction`.

Focused validation first failed for the missing field and missing report
surface, then passed 102 tests after implementation. The formal-confidence
target remains deliberately blocked on `fixed-point-construction`.
