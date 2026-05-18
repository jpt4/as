# ADR-0229: Consistency Level Target

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0226 added a checked Type-NS arithmetic language. ADR-0227 added the first
proof-code codebook. ADR-0228 added capture-avoiding substitution examples.
The formal-confidence target is still blocked on fixed-point self-reference,
consistency-level selection, and deduction-apparatus selection.

The next useful step is not to claim consistency. It is to select the exact
consistency notion future work must target. Willard 2011 Definition 5.6 frames
Level(k) consistency through the absence of proofs of both a Pi_k sentence and
its Sigma_k negation, while Definition 5.7 uses SelfCons_k. AS now has enough
syntax/code/substitution scaffolding to choose a target level without
pretending to prove it.

## Decision

Add a checked consistency-level target manifest and validator selecting
Level-1 consistency as the first AS formal-confidence target notion.

The target will reference the formal arithmetic language, codebook, and
substitution examples; require `pi1` and `sigma1` sentence classes; require
Willard Level(k) and SelfCons_k anchors; and mark the target as
`target-selected-not-claimed`.

The formal-confidence target will be narrowed again: it will point to the
consistency-level target and no longer list `consistency-level-selection` as a
blocker. It will remain blocked on fixed-point self-reference and
deduction-apparatus selection.

This does not implement a proof checker, deduction apparatus, fixed-point
sentence, consistency theorem, runtime behavior, command semantics, evidence
bundles, or GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because the consistency-level module and
  manifest do not exist.
- The manifest references the checked formal arithmetic language, formal
  codebook, substitution examples, and known Willard anchors.
- The manifest selects Level-1 consistency with `pi1` statement class and
  `sigma1` negation class.
- The validator rejects unknown Willard anchors, missing sentence classes, and
  targets that claim proved consistency.
- Text and JSON CLI modes expose the same validation surface.
- The formal-confidence target no longer lists
  `consistency-level-selection` as a blocker but remains blocked.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_consistency_level_target
  tests.test_formal_confidence_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live consistency-level text/JSON, live formal-confidence,
  live project-status summary, live handoff with `--refresh-remotes`,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `claims/consistency_level_targets.json` and
`autarkic_systems/consistency_level.py`.

The red run failed as intended because the consistency-level module and target
manifest did not exist and the formal-confidence target still listed
`consistency-level-selection` as a blocker. The green focused run passed 109
tests across `tests.test_consistency_level_target`,
`tests.test_formal_confidence_target`, and
`tests.test_project_status_report`.

Live text and JSON consistency-level reports accepted the Level-1 target with
no failed subjects. Live formal-confidence output removed
`consistency-level-selection` from the blocker list, and live project-status
summary remained accepted. `compileall`, JSON validation, `git diff --check`,
and `python -m unittest discover` passed; the full default suite ran 977 tests.

The target now points at `claims/consistency_level_targets.json` and remains
blocked on fixed-point self-reference and deduction-apparatus selection. This
ADR deliberately leaves proof checking, deduction-apparatus selection,
fixed-point self-reference, and consistency claims for later ADRs.
