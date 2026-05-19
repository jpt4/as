# ADR-0263: Fixed-Point Construction Cases

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0262 made the fixed-point construction blocker more concrete by adding a
finite bridge target between the checked diagonal instance and the direct
fixed-point target form. The aggregate formal-confidence target still names the
remaining blocker only as `fixed-point-construction`.

That blocker now has enough structure to be decomposed into proof cases without
claiming any proof. Doing so gives later work a fail-closed checklist for the
missing representability, graph-correctness, bridge-equality, and
fixed-point-equation steps.

## Decision

Add `claims/fixed_point_construction_cases.json` and
`autarkic_systems.fixed_point_construction_cases`.

The case map will record five open proof cases:

- diagonal instance closure;
- substitution representability proof;
- substitution graph correctness proof;
- bridge equality proof; and
- fixed-point equation lifting.

Each case remains `proof-case-open`, names its checked dependency subjects, and
preserves explicit non-claims. Aggregate formal-confidence validation will fail
closed over this case map with a new `fixed_point_construction_cases`
configuration field.

This is a proof-case map only. It does not prove substitution representability,
substitution graph correctness, bridge equality, a fixed-point equation, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the construction-case verifier
  and manifest do not exist, aggregate formal confidence lacks the new
  configuration field, and missing construction-case manifests are not rejected.
- The new verifier accepts the checked case map.
- Text and JSON output expose all five open cases, their required dependency
  subjects, observed dependency counts, future work, and no failed subjects.
- Overclaiming case statuses reject.
- Stale dependency lists reject.
- Formal-confidence validation reports `fixed-point construction cases
  accepted` on the healthy path and fails closed on missing construction-case
  manifests.
- The formal-confidence target remains blocked on `fixed-point-construction`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_construction_cases
  tests.test_formal_confidence_target`.
- Green: the same focused suite passes after implementation.
- Regression: run live fixed-point-construction-cases text/JSON, live
  formal-confidence text/JSON, live project-status summary, compileall,
  changed JSON parsing, `git diff --check`, adjacent fixed-point and
  substitution-graph focused tests, and the full default suite.

## After Action Report

Completed on 2026-05-19.

The red suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_construction_cases tests.test_formal_confidence_target
```

It reported the missing construction-case module and manifest, the missing
`fixed_point_construction_cases` formal-confidence configuration field, the
missing fail-closed behavior for absent construction cases, and the absent text
report acceptance line.

The implementation added the construction-case manifest and verifier, wired the
case map into aggregate formal-confidence validation, and preserved the
`fixed-point-construction` blocker. The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_construction_cases tests.test_formal_confidence_target
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.fixed_point_construction_cases --format json | jq -e '.accepted == true and .case_count == 5 and (.failed_subjects | length == 0)'
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.formal_confidence --format json | jq -e '.accepted == true and .target_count == 1 and (.failed_subjects | length == 0) and ([.targets[].status] == ["blocked"]) and ([.results[] | select(.subject | endswith("fixed_point_construction_cases")) | .accepted] == [true])'
python -m autarkic_systems.project_status --format summary
python -m unittest tests.test_fixed_point_construction_cases tests.test_fixed_point_equation_bridge tests.test_fixed_point_equation_candidate tests.test_fixed_point_obstruction tests.test_diagonal_construction tests.test_substitution_representability tests.test_substitution_graph_correctness_cases tests.test_formal_confidence_target
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_construction_cases.json claims/formal_confidence_targets.json >/dev/null
git diff --check
python -m unittest discover
```

Observed results:

- focused construction/formal-confidence suite: 33 tests passed;
- live construction-case text/JSON: accepted, five open cases, no failed
  subjects;
- live formal-confidence text/JSON: accepted, one blocked target,
  `fixed-point construction cases accepted`;
- live project-status summary: accepted, one blocked formal-confidence target,
  safe next slice `none`;
- adjacent fixed-point and substitution-graph suite: 106 tests passed;
- compileall, changed JSON parsing, and diff whitespace checks passed; and
- full default suite: 1,256 tests passed.

This slice improved the shape of the remaining proof work, but did not close
it. The next useful construction work is to discharge one of the open cases
with an actual proof artifact rather than adding more labels.
