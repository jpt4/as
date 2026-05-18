# Consistency Level Target

Status: first checked consistency-level target selection, 2026-05-18.

ADR-0229 adds `claims/consistency_level_targets.json` and
`autarkic_systems/consistency_level.py`. This selects the first consistency
notion for later formal-confidence work without claiming that AS proves it.

## Purpose

Willard-style formal confidence is sensitive to the exact consistency level.
ADR-0229 chooses Level-1 consistency as the first AS target notion and ties
that choice to the existing formal arithmetic language, codebook, and
substitution examples.

The target currently records:

- Level-1 consistency as the selected notion;
- `pi1` as the statement class and `sigma1` as the negation class;
- Willard 2011 Definition 5.6 and Definition 5.7 as required anchors;
- the formal codebook as the proof-code source; and
- the formal substitution examples as the current substitution source.

## Run

```sh
python -m autarkic_systems.consistency_level
python -m autarkic_systems.consistency_level --format json
```

The validator checks that:

- the manifest references the checked language, codebook, and substitution
  artifacts;
- required Willard anchors are present and known;
- `pi1` and `sigma1` sentence classes exist in both the language and codebook;
- the target status is `target-selected-not-claimed`; and
- the manifest does not claim proved consistency.

## Boundary

This is not a deduction apparatus, fixed-point construction, consistency proof,
or self-consistency theorem. It is the target selection needed before those
later claims can be made precise.
