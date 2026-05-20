# ADR-0276: Fixed-Point Bridge Equality Frontier Status

Date: 2026-05-20

## Status

Accepted.

## Context

ADR-0267 and ADR-0269 added finite support surfaces for the
`bridge-equality-proof` fixed-point construction case. ADR-0273 then summarized
the whole fixed-point construction frontier, but its aggregate blocker remains
`fixed-point-construction`.

The fourth construction case now needs its own compact frontier/status surface.
That surface should make the current bridge-equality proof case auditable
without promoting it: the alignment and evaluation surfaces are accepted, the
expected bridge equation and output lengths remain checked, and the case still
requires a proof before it can close.

## Decision

Add `claims/fixed_point_bridge_equality_frontier_status.json` and
`autarkic_systems.fixed_point_bridge_equality_frontier_status`.

The verifier will load the current construction-case map and compact support
manifests for:

- the fixed-point equation bridge;
- the substitution representability target;
- the substitution graph correctness cases;
- bridge equality alignment; and
- bridge equality evaluation.

It will require the construction case with case kind `bridge-equality-proof` to
remain `proof-case-open`, keep `frontier_status` as `blocked`, keep
`frontier_blocked_by` as `bridge-equality-proof`, and expose the alignment and
evaluation acceptance facts at manifest level. The expected bridge equation
length is 4815, and the evaluation output length is 296.

This is a compact bridge-equality frontier/status surface only. It does not
prove substitution representability, substitution graph correctness, bridge
equality, a fixed-point equation, an arithmetized proof predicate, or
self-consistency.

## Success Criteria

- Red tests fail before implementation because the bridge-equality
  frontier-status verifier and manifest do not exist.
- The new verifier accepts the checked-in bridge-equality frontier-status
  manifest.
- The manifest names the current construction-case map, fixed-point equation
  bridge, substitution representability target, substitution graph correctness
  cases, bridge equality alignment, and bridge equality evaluation.
- The bridge-equality construction case remains `proof-case-open`.
- The surface reports `frontier_status` as `blocked` and
  `frontier_blocked_by` as `bridge-equality-proof`.
- Bridge equality alignment and evaluation support facts accept, with a
  4815-token bridge equation and a 296-token evaluation output.
- Text and JSON output expose accepted status, frontier status/blocker, the
  construction case id/kind/status, support surface count, and failed subjects.
- Proof-promotion frontier statuses reject.
- Missing or empty non-claims reject.
- Stale dependency paths reject.
- A closed bridge-equality construction case rejects.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_bridge_equality_frontier_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live bridge-equality-frontier-status text/JSON, compileall,
  changed JSON parsing, and `git diff --check`.

## After Action Report

The red focused suite failed before implementation as expected:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_frontier_status
```

It reported the missing
`autarkic_systems.fixed_point_bridge_equality_frontier_status` module before
any manifest or implementation existed:

```text
ImportError: cannot import name 'fixed_point_bridge_equality_frontier_status' from 'autarkic_systems'
```

The implementation added the compact bridge-equality frontier manifest,
verifier, CLI, documentation, and focused tests. The surface keeps the
`bridge-equality-proof` construction case open, records five compact support
surfaces, checks the 4815-token bridge equation and 296-token evaluation
output facts, and preserves the explicit non-claims.

The green and regression commands were:

```sh
python -m unittest tests.test_fixed_point_bridge_equality_frontier_status
python -m autarkic_systems.fixed_point_bridge_equality_frontier_status
python -m autarkic_systems.fixed_point_bridge_equality_frontier_status --format json | jq -e '.accepted == true and .frontier_status == "blocked" and .frontier_blocked_by == "bridge-equality-proof" and .construction_case.case_kind == "bridge-equality-proof" and .construction_case.status == "proof-case-open" and .support_surface_count == 5 and (.failed_subjects | length == 0) and .support_facts.bridge_equality_alignment.bridge_equation_code_length == 4815 and .support_facts.bridge_equality_evaluation.evaluation_output_code_length == 296'
jq -e . claims/fixed_point_bridge_equality_frontier_status.json
python -m compileall autarkic_systems tests
git diff --check
```

Observed results:

- focused bridge-equality-frontier-status suite: 13 tests passed;
- live text CLI: accepted, blocked by `bridge-equality-proof`,
  `AS-FIXED-POINT-CONSTRUCTION-BRIDGE-EQUALITY` remains
  `proof-case-open`, five support surfaces accepted, no failed subjects;
- live JSON CLI acceptance check: passed;
- manifest JSON parsing, compileall, and diff whitespace checks passed.

This slice is only a compact frontier handoff. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
