# ADR-0239: Formal Complement Surface

Date: 2026-05-18

## Status

Accepted.

## Context

The Level-1 consistency target distinguishes `pi1` statement classes from
`sigma1` negation classes, but AS does not yet have a checked surface that
maps one class to the other. The AFS requirement matrix still names complement
relations as open proof-code work.

Without a checked complement surface, the consistency-level target can say
"pi1/sigma1" but cannot validate the code-level operation that later
consistency and self-consistency work will need.

## Decision

Add a small formal complement surface for sentence wrappers. It will validate
examples where a `pi1` sentence complements to a `sigma1` sentence with a
negated body, and a `sigma1` sentence complements to a `pi1` sentence with a
negated body.

The consistency-level target will reference and validate this complement
surface, so Level-1 consistency selection fails closed if the complement
examples disappear or drift.

This does not prove a complement theorem, simplify double negations, implement
deduction, construct a fixed point, prove consistency, claim self-consistency,
change runtime behavior, change command semantics, add an evidence bundle, or
alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.formal_complement` and
  `language/formal_complement_examples.json` do not exist, and the
  consistency-level manifest has no complement dependency.
- The complement manifest validates checked `pi1` to `sigma1` and `sigma1` to
  `pi1` examples against the formal arithmetic language and codebook.
- `autarkic_systems.formal_complement` exposes `complement_sentence`, text
  and JSON CLI validation, and rejection of non-sentence nodes, stale expected
  codes, unknown sentence classes, and overclaiming statuses.
- `claims/consistency_level_targets.json` references the complement examples,
  and `autarkic_systems.consistency_level` validates that dependency.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_complement
  tests.test_consistency_level_target tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-complement text/JSON, live consistency-level
  text/JSON, live project-status summary, live handoff with
  `--refresh-remotes`, compileall, JSON checks, `git diff --check`, and the
  full default suite.

## After Action Report

Implemented on 2026-05-18.

The new complement surface validates two checked examples:
`pi1-less-than-to-sigma1-not-less-than` and
`sigma1-not-less-than-to-pi1-double-not-less-than`. The helper
`complement_sentence` flips `pi1`/`sigma1` sentence wrappers and wraps the
body in formal `not`, with text/JSON CLI output and fail-closed checks for
stale expected codes, unknown sentence classes, and overclaiming statuses.

The consistency-level target now references
`language/formal_complement_examples.json` and validates the complement report
as a dependency. Focused validation passed 111 tests, and live
consistency-level output reports `OK complement: formal complement accepted`.
