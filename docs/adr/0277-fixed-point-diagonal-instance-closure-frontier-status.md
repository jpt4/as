# ADR-0277: Fixed-Point Diagonal Instance Closure Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0263 split the fixed-point construction blocker into five open proof
cases. ADR-0270 then made the first case,
`diagonal-instance-closure`, depend on the checked diagonal-instance candidate
surface. ADR-0273 summarizes the aggregate fixed-point construction frontier,
while ADR-0275 and ADR-0276 give compact case-level handoffs for later
construction cases.

The first case needs the same compact handoff treatment. The current support
surfaces are useful and accepted as finite evidence, but they do not close the
case or promote the fixed-point construction frontier. A small status surface
should let later agents see that the fixed-point target, diagonal construction,
equation bridge, diagonal-instance closure, and candidate surface still line
up while the case remains open.

## Decision

Add
`claims/fixed_point_diagonal_instance_closure_frontier_status.json` and
`autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status`.

The verifier will load the current fixed-point construction case map and the
five support manifests required by the `diagonal-instance-closure` case:

- fixed-point target;
- diagonal construction;
- fixed-point equation bridge;
- diagonal-instance closure; and
- diagonal-instance candidate surface.

It will require the construction case
`AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE` with kind
`diagonal-instance-closure` to remain `proof-case-open`, keep
`frontier_status` as `blocked`, keep `frontier_blocked_by` as
`diagonal-instance-closure`, preserve the exact support-subject list, preserve
the expected support paths, require explicit non-claims, and report no failed
support subjects.

This is a compact frontier/status handoff only. It does not prove
substitution representability, substitution graph correctness, bridge
equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the diagonal-instance-closure
  frontier-status verifier and manifest do not exist.
- The checked-in manifest validates as accepted.
- The manifest names the current construction-case map, fixed-point target,
  diagonal construction, fixed-point equation bridge, diagonal-instance
  closure, and diagonal-instance candidate surface.
- The `diagonal-instance-closure` construction case remains
  `proof-case-open`.
- The surface reports `frontier_status` as `blocked` and
  `frontier_blocked_by` as `diagonal-instance-closure`.
- The support surface list exactly matches the current construction-case
  dependency subjects.
- All support surfaces accept and report no failed subjects.
- Compact support facts preserve one fixed-point target, one diagonal
  construction, one bridge target, one closure point, one candidate surface,
  and the 296-token diagonal-instance length.
- Proof-promotion frontier statuses reject.
- Missing or empty status non-claims reject.
- Stale dependency paths reject.
- A closed construction case rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_diagonal_instance_closure_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run the focused suite with `tests.test_suite_selection`, run live
  text and JSON CLIs, parse changed JSON manifests, compile the changed Python
  surface, and run `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure_frontier_status
```

It reported the missing ADR-0277 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'fixed_point_diagonal_instance_closure_frontier_status' from 'autarkic_systems'
```

The implementation added the compact diagonal-instance-closure frontier
manifest, verifier, CLI, documentation, focused tests, and
`extended-fixed-point` suite enrollment. The surface keeps the
`diagonal-instance-closure` construction case open, records five accepted
support surfaces, checks support failed-subject emptiness, preserves the
296-token diagonal-instance length and one diagonal candidate, and preserves
the explicit non-claims.

The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_diagonal_instance_closure_frontier_status
python -m unittest tests.test_suite_selection tests.test_fixed_point_diagonal_instance_closure_frontier_status
python -m autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status
python -m autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status --format json | jq -e '.accepted == true and .frontier_status == "blocked" and .frontier_blocked_by == "diagonal-instance-closure" and .construction_case.case_id == "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE" and .construction_case.case_kind == "diagonal-instance-closure" and .construction_case.status == "proof-case-open" and .support_surface_count == 5 and (.failed_subjects | length == 0) and .support_facts.diagonal_instance_closure.diagonal_instance_code_length == 296 and .support_facts.diagonal_instance_candidate_surface.candidate_count == 1'
jq -e . claims/fixed_point_diagonal_instance_closure_frontier_status.json tests/suite_manifest.json >/dev/null
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused diagonal-instance-closure frontier-status suite: 14 tests passed;
- focused suite-selector plus frontier-status suite: 19 tests passed;
- live text CLI: accepted, blocked by `diagonal-instance-closure`,
  `AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE` remains
  `proof-case-open`, five support surfaces accepted, no failed subjects;
- live JSON CLI acceptance check: passed;
- manifest JSON parsing, compileall, and diff whitespace checks passed.

This slice is only a compact frontier handoff. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
