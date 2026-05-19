# Fixed-Point Substitution Witness Bridge

Status: finite witness-alignment evidence, not a representability proof,
2026-05-19.

ADR-0265 adds `claims/fixed_point_substitution_witness_bridge.json` and
`autarkic_systems/fixed_point_substitution_witness_bridge.py`. The surface
checks the second fixed-point construction proof case against the current
substitution witness, graph correctness cases, fixed-point equation bridge,
and diagonal-instance closure.

## Purpose

ADR-0263 made `substitution-representability-proof` the second open
construction case. ADR-0265 narrows that case from broad dependency names to a
finite checked witness-bridge point.

The verifier derives the current witness bridge and checks that:

- the witness, diagonal construction, target, bridge, and closure name the
  same route;
- the witness is a self-application witness over the current diagonal seed;
- the witness output is the current closed diagonal instance;
- the fixed-point equation bridge observation agrees with the witness output;
- the diagonal-instance closure observation agrees with the bridge; and
- the substitution graph correctness case map remains accepted.

## Run

```sh
python -m autarkic_systems.fixed_point_substitution_witness_bridge
python -m autarkic_systems.fixed_point_substitution_witness_bridge --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the fixed-point target, diagonal construction, substitution witness,
  substitution graph correctness cases, fixed-point equation bridge,
  diagonal-instance closure, and formal codebook dependencies remain accepted;
- exactly one witness-bridge point is derived;
- the witness formula and argument codes are the same current seed code;
- the witness output has the current diagonal-instance length;
- the witness output, bridge observation, and closure observation agree; and
- future work and non-claims remain explicit.

## Boundary

This is not a substitution representability proof, not a substitution graph
correctness proof, not a bridge equality proof, not a fixed-point equation
proof, not an arithmetized proof predicate, and not a self-consistency theorem.
The formal-confidence target remains blocked on `fixed-point-construction`.
