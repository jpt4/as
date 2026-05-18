# ADR-0253: Formal Confidence Substitution Graph Correctness Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0252 added a checked target for the next theorem: the current
`substitution_code(x,y) = z` formula schema must be proved correct for the
substitution graph before the diagonal route can rely on it. That target is
validated by its own CLI, but the aggregate formal-confidence target still
does not fail closed over it.

If the correctness target disappears or drifts, formal-confidence validation
should reject rather than keep reporting the route as aligned. This is not a
proof of the target; it is an aggregate dependency check over the proof
obligation.

## Decision

Add a structured `substitution_graph_correctness` configuration field to
`claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate the referenced
correctness target surface.

The healthy path reports `substitution graph correctness target accepted`.
Missing or invalid references fail closed as
`target-substitution-graph-correctness`.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because the checked formal-confidence
  target has no `substitution_graph_correctness` required configuration field,
  the report does not expose an accepted correctness-target result, and missing
  correctness manifests do not reject formal-confidence validation.
- `claims/formal_confidence_targets.json` includes a structured
  `substitution_graph_correctness` path.
- `autarkic_systems.formal_confidence` validates the referenced correctness
  target surface with `autarkic_systems.substitution_graph_correctness`.
- Healthy text and JSON reports expose
  `substitution graph correctness target accepted`.
- Missing or invalid substitution graph correctness references fail closed as
  `target-substitution-graph-correctness`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-confidence text/JSON, live substitution-graph
  correctness text/JSON, live project-status summary, compileall, JSON checks,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The formal-confidence target now carries
`"substitution_graph_correctness":
"claims/substitution_graph_correctness_targets.json"`. The validator loads
that manifest, runs the substitution-graph correctness validator, reports
`substitution graph correctness target accepted` on the healthy path, and maps
missing or invalid references to
`target-substitution-graph-correctness`.

Focused validation first failed for the missing field and missing report
surface, then passed after implementation. The formal-confidence target
remains deliberately blocked on `fixed-point-construction`.
