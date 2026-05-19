# ADR-0255: Formal Confidence Correctness Cases Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0254 decomposed the substitution graph correctness target into five open
proof cases. Those cases are checked by their own CLI, but aggregate
formal-confidence validation still does not fail closed over them.

If the case map disappears or drifts, formal-confidence validation should
reject rather than continue to report that the self-reference route is aligned.
This is not a proof of any case. It is an aggregate dependency check over the
proof-case map.

## Decision

Add a structured `substitution_graph_correctness_cases` configuration field
to `claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate the referenced
correctness-case surface.

The healthy path reports `substitution graph correctness cases accepted`.
Missing or invalid references fail closed as
`target-substitution-graph-correctness-cases`.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because the checked formal-confidence
  target has no `substitution_graph_correctness_cases` required configuration
  field, the report does not expose an accepted correctness-cases result, and
  missing correctness-case manifests do not reject formal-confidence
  validation.
- `claims/formal_confidence_targets.json` includes a structured
  `substitution_graph_correctness_cases` path.
- `autarkic_systems.formal_confidence` validates the referenced
  correctness-case surface with
  `autarkic_systems.substitution_graph_correctness_cases`.
- Healthy text and JSON reports expose
  `substitution graph correctness cases accepted`.
- Missing or invalid substitution graph correctness-case references fail
  closed as `target-substitution-graph-correctness-cases`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-confidence text/JSON, live
  substitution-graph-correctness-cases text/JSON, live project-status summary,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `autarkic_systems/formal_confidence.py`,
`claims/formal_confidence_targets.json`, and
`tests/test_formal_confidence_target.py`.

The red focused run failed before implementation because the aggregate target
did not require or validate a `substitution_graph_correctness_cases`
configuration field, healthy reports had no accepted correctness-cases result,
and a missing case-map reference did not reject formal-confidence validation.

The green implementation makes the checked case map a fail-closed dependency
of the formal-confidence target. Healthy text and JSON output now report
`substitution graph correctness cases accepted`; missing or invalid references
surface as `target-substitution-graph-correctness-cases`.

Focused formal-confidence and project-status tests passed 107 tests. The work
does not prove any correctness case and leaves `AS-FORMAL-CONFIDENCE-TARGET-001`
blocked on `fixed-point-construction`.
