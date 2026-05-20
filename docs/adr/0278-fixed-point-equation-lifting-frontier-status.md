# ADR-0278: Fixed-Point Equation Lifting Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0268 added finite alignment evidence for the
`fixed-point-equation-lifting` fixed-point construction case. That alignment
ties the selected `pi1` target context to the checked fixed-point equation
bridge, bridge-equality alignment, and codebook, but it deliberately leaves
the fixed-point equation proof open.

ADR-0273 summarized the aggregate fixed-point construction frontier, while
ADR-0275 and ADR-0276 added compact handoffs for narrower construction cases.
The fifth construction case now needs the same compact status surface: later
work should be able to see that the current support stack is accepted without
mistaking that fact for a fixed-point equation proof.

## Decision

Add `claims/fixed_point_equation_lifting_frontier_status.json` and
`autarkic_systems.fixed_point_equation_lifting_frontier_status`.

The verifier will load the current fixed-point construction case map and the
compact support surfaces for:

- the fixed-point target;
- the fixed-point equation bridge;
- the formal codebook; and
- the equation-lifting alignment.

It will require the construction case
`AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING`, with case kind
`fixed-point-equation-lifting`, to remain `proof-case-open`. The frontier must
remain `blocked` by `fixed-point-equation-lifting`. The support subjects must
match the construction-case required dependency subjects exactly, all support
surfaces must accept, and the compact facts must preserve the current
4528-token direct target form and 4815-token bridge equation.

This is a compact fixed-point equation lifting frontier/status surface only.
It does not prove substitution representability, substitution graph
correctness, bridge equality, a fixed-point equation, an arithmetized proof
predicate, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the equation-lifting
  frontier-status verifier and manifest do not exist.
- The new verifier accepts the checked-in equation-lifting frontier-status
  manifest.
- The manifest names the current construction-case map, fixed-point target,
  fixed-point equation bridge, formal codebook, and equation-lifting
  alignment.
- The construction case id is
  `AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING`, the case kind is
  `fixed-point-equation-lifting`, and the case remains `proof-case-open`.
- The frontier remains `blocked` by `fixed-point-equation-lifting`.
- The support surface order and construction-case required dependency
  subjects are exactly `fixed_point`, `fixed_point_equation_bridge`,
  `codebook`, and `equation_lifting_alignment`.
- All support surfaces accept, with no failed subjects.
- Compact facts expose one fixed-point target, one equation bridge, one
  codebook, one equation-lifting alignment, a 4528-token direct target form,
  and a 4815-token bridge equation.
- Text and JSON output expose accepted status, frontier status/blocker, the
  construction case id/kind/status, support surface count, support facts, and
  failed subjects.
- Proof-promotion frontier statuses reject.
- Missing or empty non-claims reject.
- Stale dependency paths reject.
- A closed equation-lifting construction case rejects.
- Construction-case support subject drift rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_equation_lifting_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run the focused suite together with `tests.test_suite_selection`,
  live equation-lifting-frontier-status text/JSON, changed JSON parsing, and
  `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_equation_lifting_frontier_status
```

It reported the missing
`autarkic_systems.fixed_point_equation_lifting_frontier_status` module before
any manifest or implementation existed:

```text
ImportError: cannot import name 'fixed_point_equation_lifting_frontier_status' from 'autarkic_systems'
```

The implementation added the compact equation-lifting frontier manifest,
verifier, CLI, documentation, and focused tests. The surface keeps the
`fixed-point-equation-lifting` construction case open, records four compact
support surfaces, checks the 4528-token direct target and 4815-token bridge
equation facts, and preserves the explicit non-claims.

During implementation, an early green attempt re-ran deeper fixed-point
validators from the status layer and was too heavy for the compact handoff
role. The final verifier follows the ADR-0275/0276 pattern: load the current
support manifests and check locked compact status/fact fields without
recomputing the deep derivation stack.

The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_equation_lifting_frontier_status
python -m unittest tests.test_suite_selection tests.test_fixed_point_equation_lifting_frontier_status
python -m autarkic_systems.fixed_point_equation_lifting_frontier_status
python -m autarkic_systems.fixed_point_equation_lifting_frontier_status --format json
jq -e . claims/fixed_point_equation_lifting_frontier_status.json tests/suite_manifest.json
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused equation-lifting-frontier-status suite: 14 tests passed;
- focused suite-selection plus equation-lifting-frontier-status suite: 19
  tests passed;
- live text CLI: accepted, blocked by `fixed-point-equation-lifting`,
  `AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING` remains `proof-case-open`,
  four support surfaces accepted, no failed subjects;
- live JSON CLI: accepted with direct target length 4528 and bridge equation
  length 4815;
- manifest JSON parsing, suite-manifest JSON parsing, compileall, and diff
  whitespace checks passed.

This slice is only a compact frontier handoff. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
