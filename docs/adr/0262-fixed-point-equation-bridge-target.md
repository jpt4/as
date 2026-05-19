# ADR-0262: Fixed-Point Equation Bridge Target

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0235 records that the naive direct quotation-substitution candidate is not
a fixed point. ADR-0237 records the length-growth obstruction for that naive
route. ADR-0242 then builds the real diagonal seed route using
`substitution_code(n,n)`, and ADR-0261 checks that the diagonal witness
composition is aligned with the substitution graph evidence.

The remaining fixed-point-construction blocker is still too coarse. The
current executable surfaces show that the checked diagonal instance has code
length 296 and that the direct target form with a quotation of that full
diagonal instance has code length 4528, but no manifest names the exact bridge
between those surfaces.

## Decision

Add `claims/fixed_point_equation_bridge_targets.json` and
`autarkic_systems.fixed_point_equation_bridge`.

The bridge target will compute:

- the diagonal instance
  `Phi(substitution_code(quote(seed), quote(seed)))`;
- the direct target form `Phi(quote(diagonal_instance))`; and
- the term equality target
  `substitution_code(quote(seed), quote(seed)) = quote(diagonal_instance)`.

The verifier checks that the diagonal instance is closed, that the direct
target form is closed, that both share the selected fixed-point target
skeleton, that the diagonal slot is the expected `substitution_code` term, that
the direct slot is the quotation of the diagonal instance code, and that the
existing substitution witness output still matches the diagonal instance code.

Make aggregate formal-confidence validation fail closed over this bridge target
with a new `fixed_point_equation_bridge` configuration field.

This is not a fixed-point equation proof. It names the finite equation target
whose proof is still missing before AS can discharge the
`fixed-point-construction` blocker.

## Success Criteria

- Red tests fail before implementation because the bridge verifier and
  manifest do not exist, aggregate formal confidence lacks the new
  configuration field, and missing bridge manifests are not rejected.
- The bridge verifier accepts the checked bridge target.
- Text and JSON output expose the diagonal instance length, direct target
  length, bridge equation length, slot-kind checks, skeleton match, witness
  match, and no failed subjects.
- Stale bridge length facts reject the verifier.
- Proved bridge statuses reject until a real fixed-point equation proof exists.
- Formal-confidence validation reports `fixed-point equation bridge accepted`
  on the healthy path and fails closed on missing bridge targets.
- The formal-confidence target remains blocked on `fixed-point-construction`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_equation_bridge
  tests.test_formal_confidence_target`.
- Green: the same focused suite passes after implementation.
- Regression: run live fixed-point-equation-bridge text/JSON, live
  formal-confidence text/JSON, live project-status summary, compileall,
  changed JSON parsing, `git diff --check`, adjacent fixed-point and
  substitution-graph focused tests, and the full default suite.

## After Action Report

- Red run: `python -m unittest tests.test_fixed_point_equation_bridge
  tests.test_formal_confidence_target` failed before implementation because the
  bridge verifier module did not exist, the formal-confidence configuration did
  not include `fixed_point_equation_bridge`, and missing bridge targets did not
  reject.
- Green run: the same focused suite passed 32 tests after implementation.
- Live verifier checks: text and JSON
  `autarkic_systems.fixed_point_equation_bridge` accepted 1 bridge target with
  no failed subjects, a 296-token diagonal instance, a 4528-token direct
  target form, and a 4815-token bridge equality.
- Aggregate checks: `autarkic_systems.formal_confidence` text/JSON accepted,
  reported `fixed-point equation bridge accepted`, and kept the
  `fixed-point-construction` blocker; `autarkic_systems.project_status
  --format summary` remained accepted.
- Regression checks: adjacent fixed-point, substitution-representability,
  diagonal-witness composition, and formal-confidence tests passed 92 tests;
  `python -m compileall autarkic_systems tests`, JSON parsing for the changed
  claim manifests, and `git diff --check` passed.
- Full suite: `python -m unittest discover` passed 1,244 tests in 781.718s.
