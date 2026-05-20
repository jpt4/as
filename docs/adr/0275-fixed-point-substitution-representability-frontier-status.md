# ADR-0275: Fixed-Point Substitution Representability Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0263 split the fixed-point construction blocker into open proof cases.
The `substitution-representability-proof` case is now the narrowest frontier
where the current finite witness, substitution graph case map, equation bridge,
and witness bridge must be read together.

Those support surfaces are useful, but none of them closes the
representability proof. A compact status surface is needed so later work can
see the accepted support facts without treating the fixed-point construction
case as discharged.

## Decision

Add `claims/fixed_point_substitution_representability_frontier_status.json`
and `autarkic_systems.fixed_point_substitution_representability_frontier_status`.

The status verifier will load the current fixed-point construction case map,
the substitution representability target, the substitution graph correctness
case map, the fixed-point equation bridge, and the substitution witness bridge.
It will require the construction case with kind
`substitution-representability-proof` to remain `proof-case-open`, preserve the
frontier status as `blocked`, and preserve the blocker as
`substitution-representability-proof`.

The verifier is deliberately compact. It checks focused shape and status facts
from the existing support manifests rather than re-running every deep
derivation. In particular, it checks that the substitution witness bridge is
accepted at the compact status level, names one bridge point, preserves the
296-token witness output boundary, and carries explicit non-claims.

This status surface does not prove substitution representability, substitution
graph correctness, bridge equality, a fixed-point equation, an arithmetized
proof predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the new module and manifest do
  not exist.
- The checked-in manifest validates as accepted.
- The manifest points to the current fixed-point construction case map,
  substitution representability target, substitution graph correctness cases,
  fixed-point equation bridge, and substitution witness bridge.
- The construction case with kind `substitution-representability-proof` remains
  `proof-case-open`.
- The frontier remains `blocked` by `substitution-representability-proof`.
- The compact support layer reports five support surfaces and no failed
  subjects.
- The substitution witness bridge support is accepted, has one bridge point,
  preserves witness output length 296, and carries explicit non-claims.
- Proof-promotion statuses reject.
- Missing status non-claims reject.
- Stale dependency paths reject.
- A closed construction case rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_substitution_representability_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live text and JSON CLIs, parse the new JSON manifest with
  `jq`, compile `autarkic_systems` and `tests`, and run `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_substitution_representability_frontier_status
```

It reported the missing ADR-0275 module before any manifest or implementation
existed:

```text
ImportError: cannot import name 'fixed_point_substitution_representability_frontier_status' from 'autarkic_systems'
```

The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_substitution_representability_frontier_status
python -m autarkic_systems.fixed_point_substitution_representability_frontier_status
python -m autarkic_systems.fixed_point_substitution_representability_frontier_status --format json | jq -e '.accepted == true and .frontier_status == "blocked" and .frontier_blocked_by == "substitution-representability-proof" and .construction_case_kind == "substitution-representability-proof" and .construction_case_status == "proof-case-open" and .support_surface_count == 5 and (.failed_subjects | length == 0) and ((.support_surfaces[] | select(.subject == "substitution_witness_bridge") | .facts.expected_bridge_count) == 1) and ((.support_surfaces[] | select(.subject == "substitution_witness_bridge") | .facts.expected_witness_output_code_length) == 296)'
jq -e . claims/fixed_point_substitution_representability_frontier_status.json
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused frontier-status suite: 12 tests passed;
- live text CLI: accepted, blocked by
  `substitution-representability-proof`, construction case
  `AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY` remained
  `proof-case-open`, five support surfaces present, no failed subjects;
- live JSON CLI acceptance check: passed;
- manifest JSON parsing, compileall, and diff whitespace checks passed.

This slice adds a compact status handoff only. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
