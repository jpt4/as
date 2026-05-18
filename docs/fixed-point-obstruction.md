# Fixed-Point Obstruction

Status: checked naive length obstruction, not a fixed-point proof,
2026-05-18.

ADR-0237 adds `claims/fixed_point_obstructions.json` and
`autarkic_systems/fixed_point_obstruction.py`. The surface validates why the
ADR-0235 direct quotation-substitution candidate cannot close the fixed-point
equation for the current template.

## Purpose

ADR-0235 showed that the naive candidate is not fixed. ADR-0237 records the
structural reason: direct quotation-term embedding makes the encoded candidate
strictly longer than the input code sequence.

For the current template, the checked length equation is:

```text
candidate_length = context_length + 1 + 2 * input_length + token_sum
```

The current context length is `5`. Since input tokens are natural numbers, the
candidate is always at least `6` tokens longer than the input before the
additional `input_length + token_sum` growth. Therefore this direct
quotation-substitution operation cannot satisfy `candidate_code = input_code`.

## Current Surface

`as-fixed-point-obstruction-v1` references:

- `claims/fixed_point_equation_candidates.json`;
- `language/formal_codebook.json`; and
- the Willard generic-configuration and SelfCons(k) anchors.

It validates
`AS-FIXED-POINT-SELFCONS1-NAIVE-LENGTH-OBSTRUCTION` as
`obstruction-observed`.

For the current input code `[41, 1, 22, 11, 1, 13, 12]`, it checks:

- input length: `7`;
- input token sum: `101`;
- quotation-term code length: `116`;
- candidate code length: `121`; and
- minimum growth delta: `6`.

## Run

```sh
python -m autarkic_systems.fixed_point_obstruction
python -m autarkic_systems.fixed_point_obstruction --format json
python -m autarkic_systems.fixed_point_equation
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the fixed-point equation candidate dependency remains accepted;
- the formal codebook dependency remains accepted;
- required Willard anchors are present and known;
- the selected template has one free occurrence of the code variable;
- the checked context length, observed input length, input token sum, and
  candidate length remain current;
- the quotation-term length formula matches the actual encoder; and
- the naive candidate is impossible by strict length growth.

## Boundary

This is not a diagonal lemma, not arithmetic sequence axioms, not a
fixed-point equation proof, not an arithmetized proof predicate, and not a
self-consistency theorem. It is a precise obstruction showing why the next
construction must stop using direct quotation-term embedding as the whole
fixed-point mechanism.
