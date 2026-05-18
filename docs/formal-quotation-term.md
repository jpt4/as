# Formal Quotation Term

Status: checked quotation term surface, not a fixed-point proof, 2026-05-18.

ADR-0234 adds `language/formal_quotation_term_examples.json` and
`autarkic_systems/formal_quotation_term.py`. The surface converts checked
code-token sequences into nested `sequence_cons` / `sequence_nil` term nodes
that round-trip through `language/formal_codebook.json`.

## Purpose

ADR-0233 gave AS a checked sequence of quoted token numerals. The next missing
piece was a formal term shape for that sequence. This slice supplies that term
shape without claiming that the term satisfies a diagonal equation or that the
sequence constructors have arithmetic axioms beyond their syntax/codebook
representation.

## Current Surface

`as-formal-quotation-term-v1` references:

- `language/formal_codebook.json`;
- `language/formal_quotation_sequence_examples.json`;
- `claims/fixed_point_targets.json`; and
- the Willard generic-configuration and SelfCons(k) anchors.

It validates two examples, including the current fixed-point target expected
instance code `[41, 1, 22, 11, 1, 13, 12]`. Each example is checked for
non-empty tokens, token count, first-token numeral depth, last-token numeral
depth, accepted term kind/status, and codebook encode/decode round trip.

## Run

```sh
python -m autarkic_systems.formal_quotation_term
python -m autarkic_systems.formal_quotation_term --format json
python -m autarkic_systems.fixed_point
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the formal codebook remains accepted with sequence term tags;
- the quotation sequence dependency remains accepted;
- required Willard anchors are present and known;
- the term manifest references the codebook, sequence, and fixed-point
  manifests;
- every checked example builds a nested sequence term and round-trips it
  through the codebook; and
- empty token sequences, endpoint mismatches, and unknown term kinds reject.

## Boundary

This is not an arithmetic theory of sequences, not a diagonal lemma, not a
fixed-point equation proof, not an arithmetized proof predicate, and not a
self-consistency theorem. The fixed-point target now points at this term
surface but remains blocked on diagonal-lemma proof and fixed-point equation
proof.
