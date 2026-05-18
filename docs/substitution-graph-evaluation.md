# Substitution Graph Evaluation Examples

Status: finite examples, not a formula correctness proof, 2026-05-18.

ADR-0251 adds `claims/substitution_graph_evaluation_examples.json` and
`autarkic_systems/substitution_graph_evaluation.py`. It records three concrete
substitution graph examples over the current formal codebook.

## Purpose

The formula schema and diagonal witness evaluator check one important graph
point. A correctness proof needs more than examples, but finite examples are
useful guardrails: they show that the current evaluator handles direct
substitution, nested `substitution_code` terms, and no-occurrence preservation.

The checked examples are:

- `AS-SUBST-GRAPH-EVAL-N-EQ-ZERO`;
- `AS-SUBST-GRAPH-EVAL-NESTED-SUBST-CODE`; and
- `AS-SUBST-GRAPH-EVAL-NOT-FREE`.

## Run

```sh
python -m autarkic_systems.substitution_graph_evaluation
python -m autarkic_systems.substitution_graph_evaluation --format json
```

The validator checks that:

- the formal arithmetic language, formal codebook, and substitution graph
  formula dependencies remain accepted;
- example IDs are unique;
- each example preserves `finite-evaluation-not-proof`;
- required future work and non-claims are explicit;
- formula code and free-variable facts match the manifest;
- the finite relation truth matches the manifest; and
- output code length, prefix, and free-variable facts match the manifest.

## Boundary

This is not a formula correctness proof, not a substitution representability
proof, not a diagonal lemma, not a fixed-point equation proof, and not a
self-consistency theorem. It is finite evaluator coverage for the proof route.
