# Formal Quotation

Status: checked code-token numeral quotation surface, 2026-05-18.

ADR-0232 adds `language/formal_quotation_examples.json` and
`autarkic_systems/formal_quotation.py`. The surface converts natural-number
formal code tokens into unary successor numerals in the existing formal term
language.

## Purpose

The fixed-point target needs quotation machinery before AS can attempt a real
diagonal construction. Full quotation is larger than this slice: AS still
needs sequence coding, a quotation term for whole formula codes, and a proof
that the resulting fixed-point equation holds.

This slice checks the smallest useful part:

- `0` quotes as `zero`;
- positive code tokens quote as repeated `successor` over `zero`;
- numeral nodes decode back to their natural numbers; and
- the current fixed-point target's expected instance code can be represented
  as a sequence of token numerals.

## Run

```sh
python -m autarkic_systems.formal_quotation
python -m autarkic_systems.formal_quotation --format json
python -m autarkic_systems.fixed_point
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- required Willard anchors are present and known;
- the formal codebook remains accepted;
- checked token examples have the expected numeral depth and encoded output;
- checked token sequences have the expected count and endpoint depths; and
- negative tokens and malformed expectations reject.

## Boundary

This is not pair/list/sequence coding, not a quotation term for complete
formula codes, not a diagonal lemma, and not a self-consistency theorem. The
fixed-point target remains blocked on sequence-level quotation construction,
diagonal-lemma proof, and fixed-point equation proof.
