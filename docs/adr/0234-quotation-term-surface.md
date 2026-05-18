# ADR-0234: Quotation Term Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0233 added a checked `token-numeral-sequence` object over quoted formal
code tokens. The remaining quotation blocker is now sharper: AS still has no
formal term node that represents such a checked sequence inside the arithmetic
codebook surface.

The next useful step is to add a small term-construction surface. This must not
pretend to solve diagonalization. A nested sequence term can represent a code
sequence syntactically, but it does not prove that the term is a fixed point
for its enclosing formula.

## Decision

Add sequence term constructors to the syntax/codebook surface and add
`language/formal_quotation_term_examples.json` plus
`autarkic_systems.formal_quotation_term`.

The new term shape is `nested-sequence-cons-term`: quoted token numerals are
wrapped as nested `sequence_cons` terms ending in `sequence_nil`. The validator
will depend on the ADR-0233 quotation sequence surface, round-trip constructed
terms through the formal codebook, and check token count plus endpoint numeral
depths.

The fixed-point target will reference the quotation-term examples and remove
`quotation-term-construction` from its remaining future-work list, while still
requiring a diagonal-lemma proof and fixed-point equation proof before any
self-consistency claim.

This does not implement an evaluator, pair/list arithmetic axioms, diagonal
lemma, fixed-point equation proof, arithmetized proof predicate,
self-consistency theorem, runtime behavior, command semantics, evidence
bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the quotation-term module and
  manifest do not exist, and the language/codebook have no sequence term
  constructors.
- The formal arithmetic language names `sequence_nil` and `sequence_cons` as
  coding term constructors.
- The formal codebook encodes and decodes `sequence_nil` and `sequence_cons`
  terms, including a checked example.
- The quotation-term validator builds nested sequence terms from checked token
  sequences and round-trips them through the codebook.
- The validator rejects empty token sequences, endpoint-depth mismatches, and
  non-`nested-sequence-cons-term` kind/status mismatches.
- Text and JSON CLI modes expose the same validation surface.
- The fixed-point target points at the quotation-term examples and remains
  blocked on diagonal/fixed-point proof work.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_quotation_term
  tests.test_formal_code_encoding tests.test_formal_arithmetic_language
  tests.test_fixed_point_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live quotation-term text/JSON, live fixed-point, live
  formal-confidence JSON, live project-status summary, live handoff with
  `--refresh-remotes`, compileall, JSON checks, `git diff --check`, and the
  full default suite.

## After Action Report

Implemented. The red focused run failed before implementation because
`autarkic_systems.formal_quotation_term` and
`language/formal_quotation_term_examples.json` were absent, the arithmetic
language/codebook had no `sequence_nil` or `sequence_cons` term constructors,
and the fixed-point manifest had no `quotation_term_examples_path` field.

The implementation added `sequence_nil` and `sequence_cons` to the arithmetic
language and formal codebook, extended codebook encode/decode round trips, and
added `language/formal_quotation_term_examples.json` plus
`autarkic_systems/formal_quotation_term.py`. The validator builds nested
sequence terms from token sequences, round-trips them through the codebook,
and rejects empty sequences, endpoint mismatches, and unknown term kinds. The
fixed-point target now references the quotation-term examples and leaves
diagonal/fixed-point proof work as the remaining blocker.

Focused green evidence:

```sh
python -m unittest tests.test_formal_quotation_term tests.test_formal_code_encoding tests.test_formal_arithmetic_language tests.test_fixed_point_target tests.test_project_status_report
# Ran 139 tests in 12.603s - OK
```

Live evidence:

```sh
python -m autarkic_systems.formal_quotation_term
# Formal quotation term: accepted; Example count: 2; Failed subjects: none
python -m autarkic_systems.formal_code --format json
# accepted true; example_count 5; sequence_cons/sequence_nil term tags present
python -m autarkic_systems.fixed_point
# quotation_term_examples_path accepted; quotation_term dependency accepted
python -m autarkic_systems.formal_confidence --format json
# accepted true; failed_subjects []
python -m autarkic_systems.project_status --format summary
# Autarkic Systems summary: accepted; Formal confidence: 1 target; blocked=1
```

Regression evidence:

```sh
python -m compileall autarkic_systems tests
jq -e . language/formal_arithmetic_language.json
jq -e . language/formal_codebook.json
jq -e . language/formal_quotation_term_examples.json
jq -e . claims/fixed_point_targets.json
git diff --check
python -m unittest discover
# Ran 1041 tests in 19.443s - OK
```

The remaining boundary is still the hard one: AS has a checked formal
quotation term surface, but it has not proved sequence arithmetic axioms, a
diagonal lemma, a fixed-point equation, an arithmetized proof predicate, or a
self-consistency theorem.
