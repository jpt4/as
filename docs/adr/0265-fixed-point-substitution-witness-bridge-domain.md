# ADR-0265: Fixed-Point Substitution Witness Bridge Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0264 made the first fixed-point construction case depend on finite
diagonal-instance closure evidence. The second construction case,
`substitution-representability-proof`, still depends only on broad checked
surfaces: the substitution witness, substitution graph correctness cases, and
the fixed-point equation bridge.

That second case needs a finite bridge artifact tying those surfaces together
before any later work can honestly attempt a representability proof. The
current checked witness already states the self-application graph point, and
the bridge target already checks that the witness output matches the diagonal
instance. Those facts should be exposed as a first-class, fail-closed
construction-case dependency.

## Decision

Add `claims/fixed_point_substitution_witness_bridge.json` and
`autarkic_systems.fixed_point_substitution_witness_bridge`.

The verifier will derive one current substitution-witness bridge point and
check that:

- the witness, diagonal construction, fixed-point target, bridge target, and
  diagonal-instance closure name the same target route;
- the witness is a self-application witness whose formula code and argument
  code are the current diagonal seed code;
- the witness output is the current closed diagonal instance code;
- the fixed-point equation bridge observation agrees with that witness output;
- the diagonal-instance closure observation agrees with that bridge; and
- the substitution graph correctness case map remains accepted.

Make the `substitution-representability-proof` construction case depend on
this verifier through a new `substitution_witness_bridge_path` field in
`claims/fixed_point_construction_cases.json`.

This is finite alignment evidence only. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the witness-bridge verifier and
  manifest do not exist, the construction-case manifest has no
  `substitution_witness_bridge_path`, and the second construction case does
  not depend on `substitution_witness_bridge`.
- The new verifier accepts the checked witness-bridge domain.
- The verifier derives one bridge point from the current witness, closure, and
  bridge surfaces.
- Text and JSON output expose accepted status, bridge count, source-kind
  counts, alignment booleans, and no failed subjects.
- Stale bridge counts reject.
- Stale witness output length facts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `substitution_witness_bridge` as an accepted dependency on the
  healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_substitution_witness_bridge
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-witness-bridge text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

Completed on 2026-05-19.

The red suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_substitution_witness_bridge tests.test_fixed_point_construction_cases
```

It reported the missing substitution-witness bridge module and manifest, the
missing `substitution_witness_bridge_path` field in the construction-case
manifest, the missing accepted `substitution_witness_bridge` result, and the
old three-dependency count for the second construction case.

The implementation added the witness-bridge manifest and verifier, wired the
verifier into the `substitution-representability-proof` construction case, and
preserved that case as `proof-case-open`. The green and regression commands
were:

```sh
python -m unittest tests.test_fixed_point_substitution_witness_bridge tests.test_fixed_point_construction_cases
python -m autarkic_systems.fixed_point_substitution_witness_bridge
python -m autarkic_systems.fixed_point_substitution_witness_bridge --format json | jq -e '.accepted == true and .bridge_count == 1 and (.failed_subjects | length == 0) and .bridges[0].observed_witness_output_matches_diagonal_instance == true and .bridges[0].observed_correctness_cases_accepted == true'
python -m autarkic_systems.fixed_point_construction_cases --format json | jq -e '.accepted == true and .case_count == 5 and (.failed_subjects | length == 0) and (.results[] | select(.subject == "substitution_witness_bridge") | .accepted) == true'
python -m autarkic_systems.formal_confidence --format json | jq -e '.accepted == true and .target_count == 1 and (.failed_subjects | length == 0) and ([.targets[].status] == ["blocked"])'
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_substitution_witness_bridge.json claims/fixed_point_construction_cases.json >/dev/null
git diff --check
python -m unittest tests.test_fixed_point_substitution_witness_bridge tests.test_fixed_point_construction_cases tests.test_fixed_point_diagonal_instance_closure tests.test_fixed_point_equation_bridge tests.test_diagonal_construction tests.test_substitution_representability tests.test_substitution_graph_correctness_cases tests.test_formal_confidence_target
python -m unittest discover
```

Observed results:

- focused substitution-witness-bridge/construction-cases suite: 22 tests passed;
- live substitution-witness-bridge text/JSON: accepted, one bridge point, no
  failed subjects;
- live construction-cases JSON: accepted, second case now requires accepted
  `substitution_witness_bridge`;
- live formal-confidence JSON: accepted, one blocked target;
- live project-status summary: accepted, one blocked formal-confidence target,
  safe next slice `none`;
- compileall, changed JSON parsing, and diff whitespace checks passed;
- adjacent fixed-point construction suite: 103 tests passed; and
- full default suite: 1,278 tests passed.

This slice proves only finite witness/bridge/closure alignment facts for the
current substitution witness. It does not prove substitution representability,
substitution graph correctness, bridge equality, a fixed-point equation, an
arithmetized proof predicate, or self-consistency.
