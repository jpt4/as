# Formal Complement Surface

Status: checked sentence-complement surface, not a complement theorem,
2026-05-18.

ADR-0239 adds `language/formal_complement_examples.json` and
`autarkic_systems/formal_complement.py`. The surface validates a small
codebook-round-trippable relation between the `pi1` statement class and the
`sigma1` negation class used by the Level-1 consistency target.

## Purpose

ADR-0229 selected Level-1 consistency over `pi1` statements and `sigma1`
negation classes. That selection needs an inspectable code-level complement
operation before later consistency and self-consistency work can become
precise.

The current complement surface is deliberately small:

- a `pi1` sentence complements to a `sigma1` sentence with a negated body; and
- a `sigma1` sentence complements to a `pi1` sentence with a negated body.

It does not simplify double negations or prove that this is a complete
arithmetized complement theorem.

## Current Surface

`as-formal-complement-v1` references:

- `language/formal_arithmetic_language.json`;
- `language/formal_codebook.json`; and
- the Willard Level(k), SelfCons(k), and excluded-middle boundary anchors.

It validates two examples:

- `pi1-less-than-to-sigma1-not-less-than`; and
- `sigma1-not-less-than-to-pi1-double-not-less-than`.

## Run

```sh
python -m autarkic_systems.formal_complement
python -m autarkic_systems.formal_complement --format json
python -m autarkic_systems.consistency_level
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the formal arithmetic language and codebook dependencies remain accepted;
- required Willard anchors are present and known;
- example IDs are unique;
- only `pi1` and `sigma1` sentence wrappers are complemented;
- expected source and complement codes match the current codebook; and
- overclaiming complement-theorem statuses reject.

## Boundary

This is not a complement theorem, not double-negation simplification, not a
deduction apparatus, not a consistency proof, and not a self-consistency
theorem. It is the checked syntax/code surface that later theorem work can
target.
