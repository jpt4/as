# Fixed-Point Equation Candidate

Status: checked naive candidate, not a fixed-point proof, 2026-05-18.

ADR-0235 adds `claims/fixed_point_equation_candidates.json` and
`autarkic_systems/fixed_point_equation.py`. The surface constructs the naive
candidate obtained by substituting the checked quotation term into the current
fixed-point target template, encodes it, and records whether that code matches
the originally quoted target instance code.

ADR-0236 makes this surface a structured dependency of
`autarkic_systems.formal_confidence`, so the aggregate formal-confidence
target now fails closed if the candidate manifest is missing, invalid, or
overclaims.

ADR-0237 adds `claims/fixed_point_obstructions.json`, recording that this
naive direct quotation-substitution scheme is length-obstructed: for the
current template, quoted-sequence embedding strictly increases encoded length.
ADR-0238 makes that obstruction a checked aggregate formal-confidence
dependency alongside the candidate itself.

ADR-0262 adds a separate fixed-point equation bridge target for the real
diagonal-substitution route. It records the finite equality still needed
between `substitution_code(quote(seed), quote(seed))` and the quotation of the
checked diagonal instance, without claiming that the equality is proved.

## Purpose

ADR-0234 gave AS a formal quotation-term surface. The next risk is
overclaiming: a quotation term is not automatically a diagonal fixed point.

This surface makes that boundary executable. It checks the naive substitution
candidate and records the current truth: the candidate is not fixed. Its code
has length `121`, begins with `[41, 1, 22, 11, 1, 17]`, and differs from the
original expected target instance code `[41, 1, 22, 11, 1, 13, 12]`.

## Current Surface

`as-fixed-point-equation-candidate-v1` references:

- `claims/fixed_point_targets.json`;
- `language/formal_quotation_term_examples.json`;
- `language/formal_codebook.json`; and
- the Willard generic-configuration, SelfCons(k), and GenAC anchors.

It validates
`AS-FIXED-POINT-SELFCONS1-NAIVE-QUOTE-CANDIDATE` as
`candidate-not-fixed`.

## Run

```sh
python -m autarkic_systems.fixed_point_equation
python -m autarkic_systems.fixed_point_equation --format json
python -m autarkic_systems.fixed_point_equation_bridge
python -m autarkic_systems.fixed_point_equation_bridge --format json
python -m autarkic_systems.fixed_point_obstruction
python -m autarkic_systems.fixed_point_obstruction --format json
python -m autarkic_systems.fixed_point
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.formal_confidence --format json
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- fixed-point target, quotation-term, and codebook dependencies remain
  accepted;
- required Willard anchors are present and known;
- the naive candidate can be constructed and encoded;
- expected original code, candidate length, and candidate prefix are current;
- the candidate does not satisfy the fixed-point code equation; and
- proved-equation statuses reject.

The obstruction validator separately checks that the current direct quotation
scheme cannot be fixed by this operation because its encoded output is always
strictly longer than its input code.

## Boundary

This is not a diagonal lemma, not a fixed-point equation proof, not arithmetic
sequence axioms, not an arithmetized proof predicate, and not a
self-consistency theorem. It is a guardrail showing that the current naive
substitution does not close the fixed-point construction blocker.
