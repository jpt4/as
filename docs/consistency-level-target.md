# Consistency Level Target

Status: checked consistency-level target selection with complement dependency,
2026-05-18.

ADR-0229 adds `claims/consistency_level_targets.json` and
`autarkic_systems/consistency_level.py`. This selects the first consistency
notion for later formal-confidence work without claiming that AS proves it.

## Purpose

Willard-style formal confidence is sensitive to the exact consistency level.
ADR-0229 chooses Level-1 consistency as the first AS target notion and ties
that choice to the existing formal arithmetic language, codebook, and
substitution examples. ADR-0239 adds
`language/formal_complement_examples.json`, so the target now also validates a
checked `pi1`/`sigma1` complement surface.

The target currently records:

- Level-1 consistency as the selected notion;
- `pi1` as the statement class and `sigma1` as the negation class;
- Willard 2011 Definition 5.6 and Definition 5.7 as required anchors;
- the formal codebook as the proof-code source; and
- the formal substitution examples and complement examples as current
  proof-code support surfaces.

## Run

```sh
python -m autarkic_systems.consistency_level
python -m autarkic_systems.consistency_level --format json
python -m autarkic_systems.formal_complement
python -m autarkic_systems.formal_complement --format json
```

The validator checks that:

- the manifest references the checked language, codebook, substitution, and
  complement artifacts;
- required Willard anchors are present and known;
- the complement surface validates;
- `pi1` and `sigma1` sentence classes exist in both the language and codebook;
- the target status is `target-selected-not-claimed`; and
- the manifest does not claim proved consistency.

## Boundary

This is not a deduction apparatus, fixed-point construction, consistency proof,
or self-consistency theorem. It is the target selection needed before those
later claims can be made precise.
