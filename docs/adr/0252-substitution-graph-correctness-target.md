# ADR-0252: Substitution Graph Correctness Target

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0246 named the `substitution_code` graph formula target, ADR-0248 added a
syntactic delta0 formula schema for that graph, ADR-0250 evaluated the concrete
witness instance, and ADR-0251 added finite evaluation examples. These artifacts
are useful pressure against drift, but they still do not name the theorem that
must be proved before the diagonal construction can honestly depend on this
surface.

The next useful step is not to claim the theorem. It is to make the theorem
boundary executable and auditable: the project should have a checked target that
ties the graph target, formula candidate, and finite examples together while
keeping the proof obligation explicitly open.

## Decision

Add `claims/substitution_graph_correctness_targets.json` and
`autarkic_systems.substitution_graph_correctness`.

The new surface records one target,
`AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET`, which binds:

- graph target `AS-SUBSTITUTION-GRAPH-DELTA0-TARGET`;
- formula candidate `AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA`;
- relation `subst_code_graph`;
- formula class `delta0`; and
- the three finite examples from ADR-0251.

The target status is `correctness-proof-not-constructed`. The validator checks
the formal language, codebook, graph target, formula candidate, and finite
evaluation dependencies. It verifies that every named finite example exists and
currently evaluates true. It rejects any status that claims formula correctness,
substitution representability, the diagonal lemma, fixed-point equation
correctness, or self-consistency.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.substitution_graph_correctness` and
  `claims/substitution_graph_correctness_targets.json` do not exist.
- The manifest records the correctness target with explicit dependency paths.
- The validator accepts the checked-in target only when the graph target,
  formula candidate, and finite evaluation examples all validate.
- Healthy text and JSON reports expose the proof boundary, formula candidate,
  finite example count, and remaining future work.
- Unknown formula candidates, missing finite examples, missing non-claims, and
  proved-status overclaims fail closed with specific failure subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_correctness_target`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-graph correctness text/JSON, live
  substitution-graph evaluation text/JSON, live project-status summary,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest records
`AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET` as
`correctness-proof-not-constructed`. The validator loads the formal arithmetic
language, formal codebook, substitution graph target, substitution graph
formula candidate, and finite evaluation examples, then checks that the
formula still targets the graph target and that all three finite examples are
present and evaluate true.

Focused validation first failed because the module did not exist, then passed
12 tests after implementation. This names the exact next proof target without
claiming formula correctness, substitution representability, the diagonal
lemma, a fixed-point equation proof, or self-consistency.
