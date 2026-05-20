# ADR-0270: Fixed-Point Diagonal Instance Candidate Surface

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0264 made the first fixed-point construction case depend on finite
diagonal-instance closure evidence. That surface proves only that the current
diagonal instance is closed, codebook-stable, target-skeleton aligned, and
bridge-aligned. ADR-0269 later added finite bridge-equality evaluation evidence
for a later proof case, but the first construction case still lacks a
first-class artifact naming the closed diagonal instance as the current
fixed-point candidate surface.

The next useful step is to distinguish "the diagonal instance is closed" from
"the diagonal instance is the checked candidate surface carried forward by the
fixed-point construction map." That distinction keeps the first case honest:
the project can identify the candidate surface used by later proof work without
claiming the fixed-point equation or any proof-level bridge equality.

## Decision

Add `claims/fixed_point_diagonal_instance_candidate_surface.json` and
`autarkic_systems.fixed_point_diagonal_instance_candidate_surface`.

The verifier will derive one candidate surface from the current construction
case map, fixed-point target, diagonal construction, fixed-point equation
bridge, diagonal-instance closure surface, and codebook. It will check that:

- the `diagonal-instance-closure` construction case remains
  `proof-case-open`;
- that construction case requires the candidate-surface dependency;
- the fixed-point target, diagonal construction, fixed-point equation bridge,
  diagonal-instance closure surface, and codebook remain accepted;
- the candidate source is the current closed diagonal instance;
- the candidate code length and prefix remain current;
- the candidate round-trips through the checked codebook;
- the candidate preserves the fixed-point target skeleton and places
  `substitution_code(quote(seed), quote(seed))` in the target slot;
- the candidate agrees with the fixed-point equation bridge observation and
  the diagonal-instance closure observation; and
- all future work and non-claims remain explicit.

Make the `diagonal-instance-closure` construction case depend on this verifier
through a new `diagonal_instance_candidate_surface_path` field in
`claims/fixed_point_construction_cases.json`.

This is finite candidate-surface evidence only. It does not prove bridge
equality, the fixed-point equation, an arithmetized proof predicate, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the candidate-surface verifier
  and manifest do not exist, the construction-case manifest has no
  `diagonal_instance_candidate_surface_path`, and the first construction case
  does not depend on `diagonal_instance_candidate_surface`.
- The new verifier accepts the checked diagonal-instance candidate surface.
- The verifier derives one candidate surface from the current target,
  construction, bridge, closure, construction-case, and codebook surfaces.
- Text and JSON output expose accepted status, candidate count, source-kind
  counts, candidate booleans, construction-case booleans, and no failed
  subjects.
- Stale candidate counts reject.
- Stale candidate length facts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `diagonal_instance_candidate_surface` as an accepted dependency on
  the healthy path.
- The construction case remains `proof-case-open`.
- Formal confidence remains blocked on `fixed-point-construction`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_diagonal_instance_candidate_surface
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live diagonal-instance-candidate-surface text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

Completed on 2026-05-20.

The red suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_candidate_surface tests.test_fixed_point_construction_cases
```

It reported the missing candidate-surface module, the missing
`diagonal_instance_candidate_surface_path` field in the construction-case
manifest, the old four-dependency count for the first construction case, and
the old aggregate validator accepting a missing candidate-surface path.

The implementation added the candidate-surface manifest and verifier, wired the
verifier into the `diagonal-instance-closure` construction case, and preserved
that case as `proof-case-open`. The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_candidate_surface
python -m unittest tests.test_fixed_point_construction_cases
python -m autarkic_systems.fixed_point_diagonal_instance_candidate_surface
python -m autarkic_systems.fixed_point_diagonal_instance_candidate_surface --format json | jq -e '.accepted == true and .candidate_count == 1 and (.failed_subjects | length == 0) and .candidates[0].observed_construction_case_is_open == true and .candidates[0].observed_construction_case_requires_candidate == true and .candidates[0].observed_candidate_source_is_closed_instance == true'
python -m autarkic_systems.fixed_point_construction_cases --format json | jq -e '.accepted == true and .case_count == 5 and (.failed_subjects | length == 0) and (.results[] | select(.subject == "diagonal_instance_candidate_surface") | .accepted) == true and (.cases[] | select(.case_kind == "diagonal-instance-closure") | .status) == "proof-case-open" and (.cases[] | select(.case_kind == "diagonal-instance-closure") | .observed_dependency_count) == 5'
python -m autarkic_systems.formal_confidence --format json | jq -e '.accepted == true and .target_count == 1 and (.failed_subjects | length == 0) and ([.targets[].status] == ["blocked"]) and (.targets[0].blocked_by | index("fixed-point-construction"))'
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
jq -e . claims/fixed_point_diagonal_instance_candidate_surface.json claims/fixed_point_construction_cases.json >/dev/null
git diff --check
python -m unittest discover
```

Observed results:

- red focused suite: 14 tests ran, failed with 4 failures and 2 errors;
- candidate-surface focused suite: 12 tests passed;
- construction-case focused suite: 13 tests passed;
- live candidate-surface text/JSON: accepted, one candidate surface, no failed
  subjects, construction case open, candidate dependency present;
- live construction-cases JSON: accepted, first case now requires accepted
  `diagonal_instance_candidate_surface`;
- live formal-confidence JSON: accepted, one blocked target still blocked by
  `fixed-point-construction`;
- live project-status summary: accepted, one blocked formal-confidence target,
  safe next slice `none`;
- compileall, changed JSON parsing, and diff whitespace checks passed; and
- full default suite: 1,338 tests passed.

This slice names the current closed diagonal instance as the finite
fixed-point candidate surface for the first construction case. It does not
prove substitution representability, substitution graph correctness, bridge
equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.
