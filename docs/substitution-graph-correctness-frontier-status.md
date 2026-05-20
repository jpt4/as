# Substitution Graph Correctness Frontier Status

ADR-0274 adds a compact status surface for the substitution graph correctness
proof-case stack.

The checked manifest is
`claims/substitution_graph_correctness_frontier_status.json`; the validator is
`autarkic_systems.substitution_graph_correctness_frontier_status`.

The surface loads `claims/substitution_graph_correctness_cases.json`, observes
the five open correctness proof cases, and summarizes the support subjects
already named there:

- correctness target;
- formal codebook;
- quotation term support;
- formal substitution support;
- formula candidate support;
- substitution representability support;
- codebook roundtrip;
- quotation term closure;
- meta-substitution semantics;
- formula schema relation; and
- diagonal witness composition.

It reports per-case support and requires all five correctness cases to remain
`proof-case-open`. The aggregate frontier remains `blocked` by
`substitution-graph-correctness`.

ADR-0284 adds a second compact rollup over the five per-case frontier status
surfaces added in ADR-0279 through ADR-0283. The aggregate manifest now names
these case-status paths:

- `claims/substitution_graph_codebook_roundtrip_frontier_status.json`;
- `claims/substitution_graph_quotation_term_closure_frontier_status.json`;
- `claims/substitution_graph_meta_substitution_semantics_frontier_status.json`;
- `claims/substitution_graph_formula_schema_relation_frontier_status.json`;
  and
- `claims/substitution_graph_diagonal_witness_composition_frontier_status.json`.

The aggregate verifier runs those existing per-case validators and reports a
`case_status_rollup`. Each compact case status must be accepted, remain
`blocked`, use its own case kind as blocker, and report `proof-case-open`.

This surface is intentionally non-promotional. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, or self-consistency.

Run:

```sh
python -m autarkic_systems.substitution_graph_correctness_frontier_status
python -m autarkic_systems.substitution_graph_correctness_frontier_status --format json
```
