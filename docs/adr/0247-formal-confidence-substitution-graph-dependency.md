# ADR-0247: Formal Confidence Substitution Graph Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0246 added the first checked substitution graph target for the future
`subst_code_graph(x,y,z)` delta0 formula. That target was validated by its own
CLI, but the aggregate formal-confidence target still did not fail closed over
it. The formal-confidence target could therefore remain accepted if
`claims/substitution_graph_targets.json` disappeared or drifted.

Because the current substitution route now depends on a named graph-formula
target as well as a witness, aggregate formal-confidence validation should make
that dependency explicit.

## Decision

Add a structured `substitution_graph` configuration field to
`claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate that referenced graph
target surface.

This keeps formal-confidence validation aligned with the current
representability frontier while preserving the blocker on real fixed-point
construction.

This does not construct a delta0 graph formula, prove formula correctness,
prove substitution representability, prove the diagonal lemma, prove a
fixed-point equation, implement an arithmetized proof predicate, claim
self-consistency, change runtime behavior, change command semantics, add an
evidence bundle, or alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the checked target has no
  `substitution_graph` required configuration field, the formal-confidence
  report does not expose an accepted substitution graph result, and missing
  substitution graph manifests do not reject formal-confidence validation.
- `claims/formal_confidence_targets.json` includes a structured
  `substitution_graph` path.
- `autarkic_systems.formal_confidence` validates the referenced graph target
  with `autarkic_systems.substitution_graph_target`.
- Healthy text and JSON reports expose `substitution graph target accepted`.
- Missing or invalid substitution graph references fail closed as
  `target-substitution-graph`.
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
`"substitution_graph": "claims/substitution_graph_targets.json"`. The
validator loads that manifest, runs the substitution-graph target validator,
reports `substitution graph target accepted` on the healthy path, and maps
missing or invalid references to `target-substitution-graph`.

Focused validation first failed for the missing field and missing report
surface, then passed after implementation. The formal-confidence target
remains deliberately blocked on `fixed-point-construction`.
