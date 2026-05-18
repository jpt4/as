# ADR-0240: Formal Confidence Consistency Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0229 selected Level-1 consistency as the first AS formal-confidence target
notion. ADR-0239 then made that consistency-level target validate a checked
`pi1`/`sigma1` complement surface.

The aggregate formal-confidence validator still treated the consistency-level
target as prose inside `consistency_notion`. That left a weak link: the
formal-confidence report could remain accepted even if
`claims/consistency_level_targets.json` disappeared or stopped validating its
formal arithmetic, codebook, substitution, complement, or Willard dependencies.

## Decision

Add a structured `consistency_level_target` configuration field to
`claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate that referenced
consistency-level target.

This keeps the aggregate target boundary fail-closed over the selected
consistency notion and the complement surface beneath it.

This does not prove a consistency theorem, construct a fixed point, prove a
fixed-point equation, implement an arithmetized proof predicate, claim
self-consistency, change runtime behavior, change command semantics, add an
evidence bundle, or alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the checked target has no
  `consistency_level_target` required configuration field, the formal-confidence
  report does not expose an accepted consistency-level dependency result, and
  missing consistency-level manifests do not reject formal-confidence
  validation.
- `claims/formal_confidence_targets.json` includes a structured
  `consistency_level_target` path.
- `autarkic_systems.formal_confidence` validates the referenced
  consistency-level target with `autarkic_systems.consistency_level`.
- Healthy text and JSON reports expose `consistency-level target accepted`.
- Missing or invalid consistency-level target references fail closed as
  `target-consistency-level-target`.
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
`"consistency_level_target": "claims/consistency_level_targets.json"`. The
validator loads that manifest, runs the consistency-level validator, reports
`consistency-level target accepted` on the healthy path, and maps missing or
invalid references to `target-consistency-level-target`.

Focused validation first failed for the missing field and missing report
surface, then passed 101 tests after implementation. The formal-confidence
target remains deliberately blocked on `fixed-point-construction`; this ADR
only strengthens the dependency boundary around the selected consistency
notion.
