# ADR-0232: Formal Quotation Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0231 selected a fixed-point target template and validated a placeholder
substitution instance. The target correctly remains blocked on fixed-point
construction because AS still lacks quotation machinery. The formal codebook
does, however, already have `zero` and `successor` term nodes, so AS can check
the first small part of quotation: representing natural-number code tokens as
formal unary numerals.

The next useful step is not a sequence quote, diagonal lemma, or fixed-point
equation. It is to add a checked numeral-quotation surface for individual
formal code tokens and wire the fixed-point target to that dependency.

## Decision

Add `language/formal_quotation_examples.json` and
`autarkic_systems.formal_quotation`. The quotation surface will:

- convert nonnegative natural-number code tokens to unary formal numerals;
- convert unary formal numerals back to natural numbers;
- validate checked token examples against expected depth and encoded output;
- validate that the current fixed-point target's expected instance code can be
  token-quoted as a sequence of numeral nodes; and
- reject negative tokens, malformed numerals, expected-depth mismatches, and
  sequence-count mismatches.

The fixed-point target will be narrowed: it will reference the quotation
examples, and its future work will replace broad quotation-term construction
with the more precise remaining sequence-level quotation construction.

This does not implement pair/list/sequence coding, a quotation term for whole
formula codes, a diagonal lemma, a fixed-point equation proof, arithmetized
proof predicates, self-consistency, runtime behavior, command semantics,
evidence bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the formal-quotation module and
  manifest do not exist.
- The quotation manifest references the formal codebook and fixed-point target
  manifest.
- Token quotation round-trips `0`, small code tokens, and the fixed-point
  target expected-instance token sequence.
- The validator rejects negative tokens, expected-depth mismatches, and
  sequence-count mismatches.
- Text and JSON CLI modes expose the same validation surface.
- The fixed-point target points at the quotation examples and remains blocked
  on sequence-level quotation plus diagonal/fixed-point proof work.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_quotation
  tests.test_fixed_point_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-quotation text/JSON, live fixed-point,
  live project-status summary, live handoff with `--refresh-remotes`,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `language/formal_quotation_examples.json` and
`autarkic_systems/formal_quotation.py`.

The red run failed as intended because the formal-quotation module and example
manifest did not exist, and the fixed-point target had no quotation dependency.
The green focused run passed 112 tests across
`tests.test_formal_quotation`, `tests.test_fixed_point_target`, and
`tests.test_project_status_report`.

Live text and JSON formal-quotation reports accepted three checked examples:
`0` as `zero`, token `13` as a unary successor numeral with matching code, and
the current fixed-point target instance token sequence. Live fixed-point output
accepted the new quotation dependency and narrowed future work to
sequence-level quotation, diagonal-lemma proof, and fixed-point equation proof.
Live project-status summary remained accepted. `compileall`, JSON validation,
`git diff --check`, and `python -m unittest discover` passed; the full default
suite ran 1015 tests.

The fixed-point target now references
`language/formal_quotation_examples.json`, but the remaining boundary is still
substantial: sequence quotation, full quotation terms, diagonalization, and
self-consistency claims remain for later ADRs.
