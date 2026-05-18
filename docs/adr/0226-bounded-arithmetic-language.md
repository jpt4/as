# ADR-0226: Bounded Arithmetic Language

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0224 made the first formal-confidence target explicit and blocked it on
arithmetic syntax, proof-code encoding, self-reference substitution,
consistency-level selection, and deduction-apparatus selection. ADR-0225 made
that target part of aggregate project status. The next honest step is to start
removing those blockers one at a time.

Willard anchors already identify the relevant pressure: bounded formula
classes, Level(k) consistency, SelfCons_k, GenAC configurations, and Type-NS/S/A/M
classification. AS should not jump straight to proof-code or self-consistency
without first naming the arithmetic syntax classes it intends to manipulate.

## Decision

Add a minimal checked formal-arithmetic language manifest and validator.

The first manifest will name arithmetic terms, formulae, sentences, and
proof-object placeholders; it will explicitly include a `delta0` bounded
formula class, `pi1` and `sigma1` sentence classes, and a Type-NS arithmetic
profile. The validator will check required syntax classes, required
configuration fields, referenced Willard anchors, and non-empty examples.

The formal-confidence target will be narrowed: it will point to the new
arithmetic language artifact and remove `arithmetic-object-language` from the
blocker list, while staying `blocked` on proof-code encoding,
self-reference/substitution, consistency-level selection, and
deduction-apparatus selection.

This does not implement a parser, evaluator, proof-code encoder, substitution
engine, tableaux/Hilbert apparatus, self-consistency theorem, runtime behavior,
command semantics, evidence bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the formal-arithmetic module,
  manifest, and CLI do not exist.
- The manifest references known Willard anchors for generic configuration,
  Level(k), SelfCons_k, Type-NS/S/A/M, and excluded-middle boundary.
- The manifest names required syntax classes: terms, formulae, sentences, and
  proof_objects.
- The manifest records Type-NS as the current arithmetic profile and `delta0`
  as the first bounded formula class.
- Unknown Willard anchors, missing syntax classes, and missing bounded formula
  examples reject.
- Text and JSON CLI modes expose the same language validation surface.
- The formal-confidence target no longer lists
  `arithmetic-object-language` as a blocker but remains blocked.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_arithmetic_language
  tests.test_formal_confidence_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-arithmetic text/JSON, live formal-confidence,
  live project-status summary/JSON, live handoff with `--refresh-remotes`,
  compileall, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `language/formal_arithmetic_language.json` and
`autarkic_systems/formal_arithmetic.py`.

The red run failed as intended because the formal-arithmetic module and
manifest did not exist and the formal-confidence target still listed
`arithmetic-object-language` as a blocker. The green focused run passed 109
tests across `tests.test_formal_arithmetic_language`,
`tests.test_formal_confidence_target`, and `tests.test_project_status_report`.
Live formal-arithmetic text/JSON output reported accepted Type-NS `delta0`
syntax with no failed subjects; live formal-confidence output reported only
the remaining proof-code, self-reference/substitution, consistency-level, and
deduction-apparatus blockers; live project-status summary and refreshed
handoff remained accepted. `compileall`, JSON checks, `git diff --check`, and
`python -m unittest discover` passed; the full suite ran 935 tests.

The target now points at `language/formal_arithmetic_language.json`, records
`delta0`, and remains blocked on proof-code encoding, self-reference
substitution, consistency-level selection, and deduction-apparatus selection.
This ADR deliberately leaves parser/evaluator semantics, proof-code,
substitution, deduction apparatus, and self-consistency claims for later ADRs.
