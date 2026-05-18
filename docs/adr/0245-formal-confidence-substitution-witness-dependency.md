# ADR-0245: Formal Confidence Substitution Witness Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0244 added the first checked substitution-representability witness for the
current diagonal seed. That witness was validated by its own CLI, but the
aggregate formal-confidence target still did not fail closed over it. The
formal-confidence target could therefore remain accepted if
`claims/substitution_representability_targets.json` disappeared or drifted.

Because the current fixed-point route now passes through the checked
substitution graph witness, aggregate formal-confidence validation should make
that dependency explicit.

## Decision

Add a structured `substitution_representability` configuration field to
`claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate that referenced
substitution witness surface.

This keeps formal-confidence validation aligned with the current diagonal
route while preserving the blocker on real fixed-point construction.

This does not prove a delta0 substitution graph formula, prove substitution
representability, prove the diagonal lemma, prove a fixed-point equation,
implement an arithmetized proof predicate, claim self-consistency, change
runtime behavior, change command semantics, add an evidence bundle, or alter
GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the checked target has no
  `substitution_representability` required configuration field, the
  formal-confidence report does not expose an accepted substitution witness
  result, and missing substitution witness manifests do not reject
  formal-confidence validation.
- `claims/formal_confidence_targets.json` includes a structured
  `substitution_representability` path.
- `autarkic_systems.formal_confidence` validates the referenced witness target
  with `autarkic_systems.substitution_representability`.
- Healthy text and JSON reports expose `substitution representability
  accepted`.
- Missing or invalid substitution witness references fail closed as
  `target-substitution-representability`.
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
`"substitution_representability":
"claims/substitution_representability_targets.json"`. The validator loads
that manifest, runs the substitution-representability validator, reports
`substitution representability accepted` on the healthy path, and maps missing
or invalid references to `target-substitution-representability`.

Focused validation first failed for the missing field and missing report
surface, then passed after implementation. The formal-confidence target
remains deliberately blocked on `fixed-point-construction`.
