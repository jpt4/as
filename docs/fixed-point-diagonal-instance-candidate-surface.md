# Fixed-Point Diagonal Instance Candidate Surface

Status: finite candidate-surface evidence, not a fixed-point proof,
2026-05-20.

ADR-0270 adds
`claims/fixed_point_diagonal_instance_candidate_surface.json` and
`autarkic_systems.fixed_point_diagonal_instance_candidate_surface`. The
surface checks the first fixed-point construction proof case by naming the
current closed diagonal instance as the candidate surface carried forward by
later proof work.

## Purpose

ADR-0264 showed that the current diagonal instance is closed and
codebook-stable. ADR-0270 adds the next boundary: the construction case now
has a checked candidate surface instead of only a closure observation.

The verifier derives the current candidate surface and checks that:

- the first fixed-point construction case remains open;
- the construction case requires the candidate-surface dependency;
- the fixed-point target, diagonal construction, fixed-point equation bridge,
  diagonal-instance closure, and formal codebook dependencies remain accepted;
- the candidate is the current closed diagonal instance;
- the candidate code length and prefix remain current;
- the candidate round-trips through the checked codebook;
- the candidate preserves the fixed-point target skeleton;
- the candidate slot is `substitution_code(quote(seed), quote(seed))`; and
- the candidate agrees with the bridge and closure observations.

## Run

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_candidate_surface
python -m autarkic_systems.fixed_point_diagonal_instance_candidate_surface --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

## Boundary

This is not a substitution representability proof, not a substitution graph
correctness proof, not a bridge equality proof, not a fixed-point equation
proof, not an arithmetized proof predicate, and not a self-consistency theorem.
The formal-confidence target remains blocked on `fixed-point-construction`.
