# Substitution Graph Target

Status: checked delta0 graph-formula target, not a constructed formula,
2026-05-18.

ADR-0246 adds `claims/substitution_graph_targets.json` and
`autarkic_systems/substitution_graph_target.py`. It records the first checked
target boundary for a future formula representing the `substitution_code`
graph. ADR-0247 makes this target a structured dependency of the aggregate
formal-confidence target, so formal-confidence validation fails closed if this
surface drifts.

## Purpose

The substitution-representability witness checks one graph point:
`subst_code(seed, seed)` yields the closed quoted seed instance. A
representability proof needs a formal formula, not only that graph point.

This surface names the obligation without claiming it has been met:

- relation target `subst_code_graph`;
- formula class `delta0`;
- graph variables `x`, `y`, and `z`;
- required formal-language features for bounded graph work;
- the ADR-0244 witness tuple as the first concrete graph point; and
- explicit future work before diagonal representability can be claimed.

## Current Target

`AS-SUBSTITUTION-GRAPH-DELTA0-TARGET` is
`graph-formula-target-not-constructed`.

The target uses graph variables:

```text
formula_code -> x
argument_code -> y
output_code -> z
```

It is tethered to witness
`AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS`.

The checked witness formula and argument code are both:

```text
[41, 1, 22, 11, 1, 18, 11, 4, 11, 4]
```

The checked witness output is closed, has code length `296`, and begins:

```text
[41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13]
```

## Run

```sh
python -m autarkic_systems.substitution_graph_target
python -m autarkic_systems.substitution_graph_target --format json
```

The validator checks that:

- the formal arithmetic language, formal codebook, and substitution witness
  dependencies remain accepted;
- required Willard anchors are present and known;
- target IDs are unique;
- the target preserves `graph-formula-target-not-constructed`;
- the relation name is `subst_code_graph`;
- the formula class is `delta0`;
- graph variables are known formal-language variables;
- required language features are present; and
- the checked witness tuple still matches the target.

## Boundary

This is not a delta0 substitution graph formula, not a formula correctness
proof, not a substitution representability proof, not a diagonal lemma, not a
fixed-point equation proof, and not a self-consistency theorem. The next AS
step is to construct an actual formula schema for `subst_code_graph(x,y,z)`
and then prove that it accepts this checked witness.
