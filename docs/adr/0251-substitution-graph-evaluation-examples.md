# ADR-0251: Substitution Graph Evaluation Examples

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0250 added a concrete evaluator for the checked substitution graph formula
witness. That still left the evaluator exercised against only the diagonal
witness path.

The next useful step is to add a small finite set of extra graph examples:
one direct free-variable substitution, one nested `substitution_code` case, and
one no-occurrence case. This broadens executable coverage while preserving
that finite examples are not a formula correctness proof.

## Decision

Add `claims/substitution_graph_evaluation_examples.json` and
`autarkic_systems.substitution_graph_evaluation`.

The new surface validates three examples:

- `AS-SUBST-GRAPH-EVAL-N-EQ-ZERO`, substituting into `n = 0`;
- `AS-SUBST-GRAPH-EVAL-NESTED-SUBST-CODE`, substituting through nested
  `substitution_code(n,n) = n`; and
- `AS-SUBST-GRAPH-EVAL-NOT-FREE`, preserving a formula where `n` is not free.

Each example records the formula code, formula free variables, argument code,
relation truth, output code length/prefix, and output free variables. The
validator checks the formal language, codebook, and formula-candidate
dependencies before evaluating the examples.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.substitution_graph_evaluation` and
  `claims/substitution_graph_evaluation_examples.json` do not exist.
- The manifest records three finite examples with explicit non-claim status.
- The validator checks formal-language, codebook, and substitution graph
  formula dependencies.
- Healthy text and JSON reports expose three accepted examples, relation
  truth, and output lengths.
- Stale formula facts, stale output facts, false relation expectations, and
  proved-status overclaims fail closed with specific failure subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_evaluation`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-graph evaluation text/JSON, live
  substitution-graph formula text/JSON, live project-status summary,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest records three finite substitution graph examples as
`finite-evaluation-not-proof`. The validator loads the current formal
arithmetic language, formal codebook, and substitution graph formula candidate
surface, then evaluates each example by substituting the quoted argument code
into the formula at variable `n`.

Focused validation first failed because the module did not exist, then passed
12 tests after implementation. This adds finite executable pressure on the
substitution graph path while preserving all proof-level blockers.
