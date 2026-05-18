# ADR-0224: Formal Confidence Target

Date: 2026-05-18

## Status

Accepted.

## Context

AS now has checked transition, chain, and network-sequence evidence, explicit
object languages for those substrate-facing claims, and a proof-certificate
surface using `predicate-result` rules. That is useful, but it is not yet a
Willard-style self-confidence claim.

AFS-R4 requires AS to state the exact self-confidence claim and its limits.
The current repo names Willard anchors at definition/theorem granularity, but
does not yet carry a checked target that says which Willard configuration
fields are satisfied, which are merely candidates, and which remain blocking.

Without that target, future agents can accidentally treat green substrate
evidence as an SJAS-level self-consistency result.

## Decision

Add a machine-readable formal-confidence target manifest under `claims/`,
plus a small validator/CLI that checks the target against the Willard anchor
map.

The first target will be explicitly `blocked`: current AS can validate
substrate claims and local predicate-result proof certificates, but it lacks an
arithmetic object language, proof-code encoding, self-reference/substitution
machinery, and a selected Willard consistency level.

This does not implement arithmetic syntax, proof-code encoding, self-reference,
a tableaux or Hilbert apparatus, a new substrate transition, runtime behavior,
command semantics, evidence-bundle acceptance, project-status aggregation, or
GitHub submission behavior.

## Success Criteria

- Red tests fail before implementation because the formal-confidence module,
  manifest, and CLI do not exist.
- The checked-in target references existing Willard anchors, including the
  generic-configuration, consistency-level, self-reference, GenAC, and excluded
  middle boundary anchors.
- The target records every required configuration field: language, bounded
  formula class, axiom basis, deduction method, proof-code encoding,
  consistency notion, self-reference, and substrate bridge.
- The accepted target is explicitly blocked and names non-empty blockers.
- Unknown Willard anchor IDs, missing configuration fields, and blocked targets
  without blockers reject.
- Text and JSON CLI modes expose the same target and validation results.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target`.
- Green: the same focused suite passes after implementation.
- Regression: run the live formal-confidence CLI in text and JSON modes,
  compileall, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `claims/formal_confidence_targets.json` and
`autarkic_systems/formal_confidence.py`, with focused coverage in
`tests/test_formal_confidence_target.py`.

The red focused run failed as intended because
`autarkic_systems.formal_confidence`, the formal-confidence target manifest,
and the CLI surface did not exist.

The implementation adds `AS-FORMAL-CONFIDENCE-TARGET-001` as an explicitly
blocked target. It ties the target to Willard generic-configuration,
consistency-level, self-reference, GenAC, Type-NS/S/A/M, and
excluded-middle-boundary anchors while recording the current AS configuration
as local transition/chain/sequence object languages plus local
predicate-result proof certificates. The validator rejects unknown Willard
anchors, missing configuration fields, and blocked targets without blockers.

Focused formal-confidence tests passed 11 tests. Live text and JSON CLI output
reported one accepted blocked target with no failed subjects. `compileall`,
`git diff --check`, and the full default suite passed; the full suite ran 922
tests.
