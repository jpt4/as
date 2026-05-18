# Formal Arithmetic Language

Status: first checked syntax-only language surface, 2026-05-18.

ADR-0226 adds `language/formal_arithmetic_language.json` and
`autarkic_systems/formal_arithmetic.py`. The language is the first AS
arithmetic-side artifact for the formal-confidence line of work.

## Purpose

ADR-0224 identified arithmetic syntax as one blocker on Willard-style formal
confidence. This slice removes only that blocker by naming a minimal checked
language surface:

- arithmetic terms with variables, `0`, successor, and non-profile addition
  and multiplication symbols;
- formulae with equality, less-than, connectives, unbounded quantifier names,
  and bounded quantifier names;
- the `delta0` bounded formula class with examples;
- `pi1` and `sigma1` sentence classes with examples; and
- placeholder-only proof objects that keep deduction-apparatus work blocked
  inside the arithmetic language itself.

The manifest is tagged as `Type-NS`, following the Willard 2020
Type-NS/S/A/M pressure. It does not assert total addition or multiplication,
and it does not implement an IS(A) system.

## Run

```sh
python -m autarkic_systems.formal_arithmetic
python -m autarkic_systems.formal_arithmetic --format json
```

The validator checks that:

- required syntax classes are present: terms, formulae, sentences, and
  proof_objects;
- required Willard anchors are present and known;
- the arithmetic profile is `Type-NS`;
- `delta0` exists and has examples;
- `pi1` and `sigma1` sentence classes exist and have examples; and
- proof objects are explicitly placeholder-only and name their blockers.

## Boundary

This is not a parser, evaluator, substitution engine, deduction apparatus,
theorem prover, or self-consistency claim. ADR-0227 adds the separate first
proof-code codebook over this syntax, while this document remains the
vocabulary surface that codebook targets.
