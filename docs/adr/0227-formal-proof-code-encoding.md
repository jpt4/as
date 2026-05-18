# ADR-0227: Formal Proof-Code Encoding

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0226 added a checked syntax-only Type-NS arithmetic language and narrowed
the formal-confidence target so arithmetic syntax is no longer absent. The
target is still blocked on proof-code encoding, self-reference substitution,
consistency-level selection, and deduction-apparatus selection.

The next useful step is to make proof-code encoding concrete without jumping
ahead to a proof checker or self-consistency theorem. Willard-style
self-reference eventually needs syntax and proof objects to be encoded in a
form that can be inspected, round-tripped, and later related to arithmetic.

## Decision

Add a first AS formal codebook and encoder/decoder for the ADR-0226 arithmetic
language surface.

The codebook will define deterministic tagged natural-number prefix codes for
terms, formulae, `pi1`/`sigma1` sentence wrappers, and placeholder proof-line
objects. The implementation will load and validate the codebook, encode a
small canonical node vocabulary, decode code sequences back into canonical
nodes, and round-trip checked examples from the manifest.

The formal-confidence target will be narrowed again: it will point to the
codebook and no longer list `proof-code-encoding` as a blocker. It will remain
blocked on self-reference/substitution, consistency-level selection, and
deduction-apparatus selection.

This does not implement a parser, evaluator, substitution engine, proof
checker, tableaux/Hilbert apparatus, arithmetized self-reference bridge,
consistency theorem, runtime behavior, command semantics, evidence bundles, or
GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the formal-code module and
  codebook do not exist.
- The codebook references the checked formal arithmetic language and known
  Willard anchors.
- The codebook names term, formula, sentence, and proof-line tags as positive
  unique natural-number codes.
- The encoder deterministically encodes variables, successor terms,
  bounded formulae, `pi1`/`sigma1` sentences, and placeholder proof lines.
- The decoder round-trips the checked examples and rejects trailing tokens.
- Duplicate tag codes, unknown variables, and mismatched manifest example
  codes reject.
- Text and JSON CLI modes expose the same validation surface.
- The formal-confidence target no longer lists `proof-code-encoding` as a
  blocker but remains blocked.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_code_encoding
  tests.test_formal_confidence_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-code text/JSON, live formal-confidence, live
  project-status summary, live handoff with `--refresh-remotes`, compileall,
  JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `language/formal_codebook.json` and
`autarkic_systems/formal_code.py`.

The red run failed as intended because the formal-code module and codebook did
not exist and the formal-confidence target still listed `proof-code-encoding`
as a blocker. The green focused run passed 113 tests across
`tests.test_formal_code_encoding`, `tests.test_formal_confidence_target`, and
`tests.test_project_status_report`.
Live formal-code text/JSON output reported four accepted round-trip examples
with no failed subjects; live formal-confidence output reported only the
remaining self-reference/substitution, consistency-level, and
deduction-apparatus blockers; live project-status summary remained accepted.
`compileall`, JSON checks, `git diff --check`, and `python -m unittest
discover` passed; the full suite ran 950 tests.

The target now points at `language/formal_codebook.json` and remains blocked on
self-reference substitution, consistency-level selection, and
deduction-apparatus selection. This ADR deliberately leaves parser/evaluator
semantics, substitution, deduction apparatus, arithmetized self-reference, and
self-consistency claims for later ADRs.
