# ADR-0228: Formal Substitution Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0226 added a checked syntax-only Type-NS arithmetic language. ADR-0227
added a first proof-code codebook and round-trip encoder/decoder over that
language. The formal-confidence target is still blocked on
self-reference/substitution, consistency-level selection, and
deduction-apparatus selection.

The next useful step is not a fixed-point theorem. It is a checked
substitution surface over the canonical nodes that the codebook already
encodes. Without capture-aware substitution, any later self-reference or
diagonalization claim would be ungrounded.

## Decision

Add a first capture-avoiding free-variable substitution module and checked
example manifest.

The implementation will compute free variables for the ADR-0227 canonical node
vocabulary, substitute a term for a free variable, respect quantifier and
sentence binders, reject substitutions that would capture a replacement
variable, and validate manifest examples against the formal codebook by
checking expected nodes and expected encoded outputs.

The formal-confidence target will be narrowed again: it will point to the
substitution examples and no longer list `self-reference-substitution` as a
blocker. It will remain blocked on a fixed-point self-reference construction,
consistency-level selection, and deduction-apparatus selection.

This does not implement a parser, evaluator, proof checker, tableaux/Hilbert
apparatus, fixed-point lemma, diagonal sentence, consistency theorem, runtime
behavior, command semantics, evidence bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the formal-substitution module
  and manifest do not exist.
- The substitution manifest references the checked formal codebook and known
  Willard anchors.
- Free-variable calculation respects term, formula, sentence, quantifier,
  bounded-quantifier, and proof-line shells.
- Substitution replaces free variable occurrences in terms, formulae, and proof
  lines.
- Substitution respects binders and rejects capture.
- Manifest examples validate expected nodes and expected encoded outputs.
- Text and JSON CLI modes expose the same validation surface.
- The formal-confidence target no longer lists
  `self-reference-substitution` as a blocker but remains blocked.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_substitution
  tests.test_formal_confidence_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-substitution text/JSON, live formal-confidence,
  live project-status summary, live handoff with `--refresh-remotes`,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `language/formal_substitution_examples.json` and
`autarkic_systems/formal_substitution.py`.

The red run failed as intended because the formal-substitution module and
example manifest did not exist and the formal-confidence target still listed
`self-reference-substitution` as a blocker. The green focused run passed 114
tests across `tests.test_formal_substitution`,
`tests.test_formal_confidence_target`, and `tests.test_project_status_report`.
Live formal-substitution text/JSON output reported four accepted examples with
no failed subjects; live formal-confidence output reported only the remaining
fixed-point self-reference, consistency-level, and deduction-apparatus
blockers; live project-status summary remained accepted. `compileall`, JSON
checks, `git diff --check`, and `python -m unittest discover` passed; the full
suite ran 966 tests.

The target now points at `language/formal_substitution_examples.json` and
remains blocked on fixed-point self-reference, consistency-level selection, and
deduction-apparatus selection. This ADR deliberately leaves parser/evaluator
semantics, fixed-point self-reference, deduction apparatus, and
self-consistency claims for later ADRs.
