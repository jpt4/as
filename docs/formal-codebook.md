# Formal Codebook

Status: first checked proof-code encoding surface, 2026-05-18.

ADR-0227 adds `language/formal_codebook.json` and
`autarkic_systems/formal_code.py`. The codebook is the first AS proof-code
encoding artifact for the formal-confidence path.

## Purpose

ADR-0226 gave AS a checked syntax-only arithmetic language. ADR-0227 adds a
deterministic code surface for that syntax so later self-reference and
deduction work can target concrete codes instead of vague labels.

The codebook currently covers:

- variables and arithmetic terms;
- equality, less-than, connectives, and bounded/unbounded quantifier nodes;
- `pi1` and `sigma1` sentence wrappers; and
- placeholder proof-line shells with line numbers, rule codes, formula codes,
  and premise references.

Codes are tagged natural-number prefix sequences. They are intentionally easy
to inspect and round-trip before any attempt to build fixed-point
self-reference or prove consistency over them. ADR-0228 adds the separate
substitution surface over these nodes.

## Run

```sh
python -m autarkic_systems.formal_code
python -m autarkic_systems.formal_code --format json
```

The validator checks that:

- the codebook points at the checked formal arithmetic language;
- required Willard anchors are present and known;
- term, formula, sentence, and proof-line tags are present;
- tag values are unique positive integers;
- checked examples encode to their expected code sequences; and
- checked examples decode back to their canonical nodes.

## Boundary

This is not a parser, evaluator, deduction apparatus, proof checker,
fixed-point self-reference construction, or self-consistency theorem. It is the
smallest inspected proof-code surface that the substitution layer targets.
