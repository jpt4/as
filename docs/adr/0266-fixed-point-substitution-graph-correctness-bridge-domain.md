# ADR-0266: Fixed-Point Substitution Graph Correctness Bridge Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0263 decomposed the remaining fixed-point construction blocker into five
open proof cases. ADR-0264 and ADR-0265 made the first two cases depend on
finite evidence surfaces. The third construction case,
`substitution-graph-correctness-proof`, still depends only on the broad
substitution graph correctness target and its case map.

ADR-0257 through ADR-0261 already added finite evidence for all five
substitution graph correctness cases: codebook roundtrip, quotation-term
closure, meta-substitution semantics, formula-schema relation, and
diagonal-witness composition. The fixed-point construction case should fail
closed over that coverage before any later proof attempt treats the
correctness target as usable.

## Decision

Add `claims/fixed_point_substitution_graph_correctness_bridge.json` and
`autarkic_systems.fixed_point_substitution_graph_correctness_bridge`.

The verifier will derive one graph-correctness bridge point and check that:

- the fixed-point construction case remains `proof-case-open`;
- the construction case requires the graph correctness target, the graph
  correctness case map, and this bridge surface;
- the graph correctness target and case map remain accepted;
- all five graph correctness case kinds are present;
- the finite codebook-roundtrip, quotation-term-closure,
  meta-substitution-semantics, formula-schema-relation, and
  diagonal-witness-composition dependencies remain accepted; and
- the diagonal-witness composition links the current fixed-point target to the
  current substitution graph correctness target.

Make the `substitution-graph-correctness-proof` construction case depend on
this verifier through a new `substitution_graph_correctness_bridge_path` field
in `claims/fixed_point_construction_cases.json`.

This is finite dependency-coverage evidence only. It does not prove
substitution graph correctness, bridge equality, a fixed-point equation, an
arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the graph-correctness bridge
  verifier and manifest do not exist, the construction-case manifest has no
  `substitution_graph_correctness_bridge_path`, and the third construction case
  does not depend on `substitution_graph_correctness_bridge`.
- The new verifier accepts the checked graph-correctness bridge domain.
- The verifier derives one bridge point from the current construction-case and
  substitution graph correctness surfaces.
- Text and JSON output expose accepted status, bridge count, source-kind
  counts, correctness-case count, finite-dependency count, alignment booleans,
  and no failed subjects.
- Stale bridge counts reject.
- Stale correctness-case counts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `substitution_graph_correctness_bridge` as an accepted dependency on
  the healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_substitution_graph_correctness_bridge
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live graph-correctness-bridge text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

Completed on 2026-05-19.

The red suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_substitution_graph_correctness_bridge tests.test_fixed_point_construction_cases
```

It reported the missing graph-correctness bridge module, the missing
`substitution_graph_correctness_bridge_path` field in the construction-case
manifest, the missing accepted `substitution_graph_correctness_bridge` result,
and the old two-dependency count for the third construction case.

The implementation added the graph-correctness bridge manifest and verifier,
wired the verifier into the `substitution-graph-correctness-proof`
construction case, and preserved that case as `proof-case-open`. The green and
regression commands were:

```sh
python -m unittest tests.test_fixed_point_substitution_graph_correctness_bridge tests.test_fixed_point_construction_cases
python -m autarkic_systems.fixed_point_substitution_graph_correctness_bridge
python -m autarkic_systems.fixed_point_substitution_graph_correctness_bridge --format json | jq -e '.accepted == true and .bridge_count == 1 and (.failed_subjects | length == 0) and .bridges[0].observed_correctness_case_count == 5 and .bridges[0].observed_all_finite_dependencies_accepted == true and .bridges[0].observed_diagonal_composition_links_target == true'
python -m autarkic_systems.fixed_point_construction_cases --format json | jq -e '.accepted == true and .case_count == 5 and (.failed_subjects | length == 0) and (.results[] | select(.subject == "substitution_graph_correctness_bridge") | .accepted) == true'
python -m autarkic_systems.formal_confidence --format json | jq -e '.accepted == true and .target_count == 1 and (.failed_subjects | length == 0) and ([.targets[].status] == ["blocked"])'
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_substitution_graph_correctness_bridge.json claims/fixed_point_construction_cases.json >/dev/null
git diff --check
python -m unittest tests.test_fixed_point_substitution_graph_correctness_bridge tests.test_fixed_point_construction_cases tests.test_substitution_graph_correctness_cases tests.test_substitution_graph_codebook_roundtrip tests.test_substitution_graph_quotation_term_closure tests.test_substitution_graph_meta_substitution_semantics tests.test_substitution_graph_formula_schema_relation tests.test_substitution_graph_diagonal_witness_composition tests.test_formal_confidence_target
python -m unittest discover
```

Observed results:

- focused graph-correctness-bridge/construction-cases suite: 22 tests passed;
- live graph-correctness-bridge text/JSON: accepted, one bridge point, five
  correctness cases, five accepted finite dependencies, linked diagonal
  composition, and no failed subjects;
- live construction-cases JSON: accepted, third case now requires accepted
  `substitution_graph_correctness_bridge`;
- live formal-confidence JSON: accepted, one blocked target;
- live project-status summary: accepted, one blocked formal-confidence target,
  safe next slice `none`;
- compileall, changed JSON parsing, and diff whitespace checks passed;
- adjacent fixed-point graph-correctness suite: 106 tests passed; and
- full default suite: 1,289 tests passed.

This slice proves only finite dependency coverage and target alignment for the
current substitution graph correctness case. It does not prove substitution
graph correctness, bridge equality, a fixed-point equation, an arithmetized
proof predicate, or self-consistency.
