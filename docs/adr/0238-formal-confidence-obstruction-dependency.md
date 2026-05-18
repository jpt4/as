# ADR-0238: Formal Confidence Obstruction Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0237 added a checked fixed-point obstruction surface that explains why the
current naive direct quotation-substitution candidate cannot satisfy the
fixed-point equation. The formal-confidence target now mentions that
obstruction in prose, but the aggregate validator does not yet load or check
it.

That leaves a drift risk: the aggregate formal-confidence report could remain
accepted even if the obstruction manifest disappeared, became stale, or began
overclaiming.

## Decision

Add a structured `fixed_point_obstruction` configuration field to
`claims/formal_confidence_targets.json` and make the formal-confidence
validator load and validate that obstruction surface.

This keeps the aggregate formal-confidence path fail-closed over both sides of
the current fixed-point evidence: the naive candidate itself and the checked
reason that candidate cannot be the real construction.

The formal-confidence target remains blocked on fixed-point construction.

This does not implement a diagonal lemma, fixed-point equation proof,
arithmetized proof predicate, theorem prover, runtime behavior, command
semantics, evidence bundle, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because `fixed_point_obstruction` is
  not a required configuration field and missing obstruction manifests do not
  make formal-confidence validation fail.
- The formal-confidence manifest contains
  `fixed_point_obstruction: claims/fixed_point_obstructions.json`.
- `autarkic_systems.formal_confidence` validates that referenced obstruction
  surface and exposes an accepted result when it is healthy.
- Missing or invalid obstruction references make the formal-confidence report
  reject with a compact obstruction dependency failure subject.
- Text and JSON CLI modes expose the new validation result.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-confidence text/JSON, live project-status
  summary, live handoff with `--refresh-remotes`, compileall, JSON checks,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The formal-confidence manifest now carries a structured
`fixed_point_obstruction` configuration field, and
`autarkic_systems.formal_confidence` loads and validates that referenced
obstruction surface. Missing or invalid obstruction references reject the
aggregate formal-confidence report with `target-fixed-point-obstruction`,
while the checked repository target reports `fixed-point obstruction
accepted`.

The target remains blocked on `fixed-point-construction`; this ADR only made
the obstruction dependency fail closed. Focused validation passed 100 tests,
and live text/JSON formal-confidence reports exposed the new accepted
obstruction result.
