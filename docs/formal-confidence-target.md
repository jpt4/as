# Formal Confidence Target

Status: first checked target boundary, 2026-05-18.

ADR-0224 adds `claims/formal_confidence_targets.json` and
`autarkic_systems/formal_confidence.py`. The target records what AS would need
before claiming Willard-style formal self-confidence, while preserving the
current truth: AS does not yet make that claim.

## Purpose

Current AS evidence is real but scoped. It validates Universal Cell transition
claims, transition-chain claims, network-sequence claims, object-language
surfaces, and local `predicate-result` proof certificates.

That surface is not yet an SJAS-level self-consistency result. A Willard-style
claim needs at least:

- an arithmetic or bounded-formula object language;
- an axiom basis;
- a deduction apparatus;
- proof-code encoding;
- substitution and self-reference machinery;
- an exact consistency notion; and
- a bridge back to the substrate claims AS can execute.

The formal-confidence target keeps those obligations explicit.

## Current Target

`AS-FORMAL-CONFIDENCE-TARGET-001` is deliberately `blocked`.

It names these Willard anchors as constraints:

- `W2011-D3.4-GENERIC-CONFIGURATION`;
- `W2011-D5.6-LEVEL-K-CONSISTENCY`;
- `W2011-D5.7-SELFCONSK`;
- `W2020-D3.2-SELF-JUSTIFYING-GENAC`;
- `W2020-D3.4-TYPE-NS-A-S-M`; and
- `W2020-T4.4-T4.5-LEM-BOUNDARY`.

It records the current configuration as local AS transition/chain/sequence
object languages plus local predicate-result proof certificates. It also
records the blockers: arithmetic object language, proof-code encoding,
self-reference substitution, consistency-level selection, and deduction
apparatus selection.

## Run

```sh
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.formal_confidence --format json
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- target IDs are unique;
- referenced Willard anchors exist;
- required Willard anchors are present;
- every required configuration field is present and non-blank;
- blocked targets name blockers; and
- each target names a next AS action.

ADR-0225 folds this validator into aggregate project status, so missing or
drifted formal-confidence targets now make the main status and inherited
handoff path reject instead of remaining invisible.

## Boundary

This is not a proof checker, not an arithmetic parser, and not a
self-consistency theorem. It is a fail-closed target boundary so later work can
build toward a real formal-confidence claim without confusing current green
substrate evidence for that claim.
