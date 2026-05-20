# Substitution Graph Quotation-Term-Closure Frontier Status

ADR-0280 adds a compact status surface for the substitution graph correctness
`quotation-term-closure` proof case.

The checked manifest is
`claims/substitution_graph_quotation_term_closure_frontier_status.json`; the
validator is
`autarkic_systems.substitution_graph_quotation_term_closure_frontier_status`.

The surface loads:

- `claims/substitution_graph_correctness_cases.json`; and
- `claims/substitution_graph_quotation_term_closure.json`.

It requires the matching correctness case to remain `proof-case-open`, the
frontier to remain `blocked` by `quotation-term-closure`, and the existing
quotation-term-closure support validator to accept with no failed subjects.
The compact support facts preserve the current twelve closure subjects and the
formula-candidate / finite-evaluation source-kind split.

This surface is intentionally non-promotional. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.substitution_graph_quotation_term_closure_frontier_status
python -m autarkic_systems.substitution_graph_quotation_term_closure_frontier_status --format json
```
