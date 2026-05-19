# ADR-0267: Fixed-Point Bridge Equality Alignment Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0263 decomposed the remaining fixed-point construction blocker into five
open proof cases. ADR-0264, ADR-0265, and ADR-0266 made the first three cases
depend on finite evidence surfaces. The fourth construction case,
`bridge-equality-proof`, still depends only on broad checked surfaces: the
fixed-point equation bridge, the substitution witness, and the substitution
graph correctness cases.

The bridge equality target in ADR-0262 already derives the concrete equality
surface:

```text
substitution_code(quote(seed), quote(seed)) = quote(diagonal_instance)
```

ADR-0260 also checks that the current formula-schema witness relation has a
closed schema instance of the same length as the bridge equation, and ADR-0265
and ADR-0266 tie the witness and graph-correctness routes back to the
fixed-point construction case. The fourth construction case should fail closed
over that finite alignment before any later proof attempt treats the bridge
equality as available.

## Decision

Add `claims/fixed_point_bridge_equality_alignment.json` and
`autarkic_systems.fixed_point_bridge_equality_alignment`.

The verifier will derive one bridge-equality alignment point and check that:

- the fixed-point construction case remains `proof-case-open`;
- the construction case requires the fixed-point equation bridge, substitution
  witness, substitution graph correctness cases, and this alignment surface;
- the fixed-point equation bridge, substitution-witness bridge, substitution
  graph correctness bridge, and formula-schema relation surfaces remain
  accepted;
- the bridge equation code length matches the formula-schema witness instance
  code length;
- the bridge left term length matches the substitution graph witness output
  minus the outer quotation wrapper;
- the bridge right term length matches the direct target's quoted diagonal
  slot;
- the witness output length matches the diagonal instance length; and
- the target, witness, and graph-correctness route identifiers agree.

Make the `bridge-equality-proof` construction case depend on this verifier
through a new `bridge_equality_alignment_path` field in
`claims/fixed_point_construction_cases.json`.

This is finite alignment evidence only. It does not prove bridge equality, the
fixed-point equation, an arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the bridge-equality alignment
  verifier and manifest do not exist, the construction-case manifest has no
  `bridge_equality_alignment_path`, and the fourth construction case does not
  depend on `bridge_equality_alignment`.
- The new verifier accepts the checked bridge-equality alignment domain.
- The verifier derives one alignment point from the current bridge, witness,
  graph-correctness, and formula-schema relation surfaces.
- Text and JSON output expose accepted status, alignment count, source-kind
  counts, length-alignment booleans, route-alignment booleans, and no failed
  subjects.
- Stale alignment counts reject.
- Stale bridge equation length facts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `bridge_equality_alignment` as an accepted dependency on the healthy
  path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_bridge_equality_alignment
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live bridge-equality-alignment text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

Completed on 2026-05-19.

The red suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_alignment tests.test_fixed_point_construction_cases
```

It reported the missing bridge-equality alignment module and manifest, the
missing `bridge_equality_alignment_path` field in the construction-case
manifest, the missing accepted `bridge_equality_alignment` result, and the old
three-dependency count for the fourth construction case.

The implementation added the bridge-equality alignment manifest and verifier,
wired the verifier into the `bridge-equality-proof` construction case, and
preserved that case as `proof-case-open`. The green and regression commands
were:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_alignment tests.test_fixed_point_construction_cases
python -m autarkic_systems.fixed_point_bridge_equality_alignment
python -m autarkic_systems.fixed_point_bridge_equality_alignment --format json | jq -e '.accepted == true and .alignment_count == 1 and (.failed_subjects | length == 0) and .alignments[0].observed_bridge_equation_code_length == 4815 and .alignments[0].observed_bridge_equation_matches_schema_instance == true and .alignments[0].observed_route_ids_match == true'
python -m autarkic_systems.fixed_point_construction_cases --format json | jq -e '.accepted == true and .case_count == 5 and (.failed_subjects | length == 0) and (.results[] | select(.subject == "bridge_equality_alignment") | .accepted) == true'
python -m autarkic_systems.formal_confidence --format json | jq -e '.accepted == true and .target_count == 1 and (.failed_subjects | length == 0) and ([.targets[].status] == ["blocked"])'
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_bridge_equality_alignment.json claims/fixed_point_construction_cases.json >/dev/null
git diff --check
python -m unittest tests.test_fixed_point_bridge_equality_alignment tests.test_fixed_point_construction_cases tests.test_fixed_point_substitution_graph_correctness_bridge tests.test_fixed_point_substitution_witness_bridge tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_equation_bridge tests.test_substitution_graph_formula_schema_relation tests.test_formal_confidence_target
python -m unittest discover
```

Observed results:

- focused bridge-equality-alignment/construction-cases suite: 22 tests passed;
- live bridge-equality-alignment text/JSON: accepted, one alignment point,
  4815-token bridge equation, schema-instance alignment, route alignment, and
  no failed subjects;
- live construction-cases JSON: accepted, fourth case now requires accepted
  `bridge_equality_alignment`;
- live formal-confidence JSON: accepted, one blocked target;
- live project-status summary: accepted, one blocked formal-confidence target,
  safe next slice `none`;
- compileall, changed JSON parsing, and diff whitespace checks passed;
- adjacent fixed-point bridge regression suite: 98 tests passed; and
- full default suite: 1,300 tests passed.

This slice proves only finite bridge/witness/graph/schema alignment facts for
the current bridge equality target. It does not prove bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
