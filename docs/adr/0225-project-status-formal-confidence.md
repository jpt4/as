# ADR-0225: Project Status Formal Confidence

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0224 added a checked formal-confidence target that marks the current
Willard-style self-consistency claim as explicitly blocked. That target is
useful only if the main operator status path also checks it. Otherwise handoff
can remain green while the formal-confidence target manifest is missing,
malformed, or drifted.

Project status already aggregates evidence, claim/proof/language surfaces,
proof-rule audit, source-status frontier, and the vertical demo/handoff path
inherits that status. The formal-confidence boundary should be part of the same
fail-closed aggregate report.

## Decision

Fold `autarkic_systems.formal_confidence` into
`autarkic_systems.project_status`.

Project status will validate `claims/formal_confidence_targets.json` against
`sources/willard_definition_map.json`, include the formal-confidence payload in
JSON, render a concise text line and failure line, add CLI overrides for both
paths, and include the target count/status mix in summary mode.

This does not change the formal-confidence target itself, implement arithmetic
syntax, implement proof-code encoding, implement self-reference, change
runtime behavior, command semantics, evidence bundles, GitHub submission, or
handoff submission logic.

## Success Criteria

- Red tests fail before implementation because project status lacks
  `formal_confidence`, schema version `22`, text/summary lines, CLI override
  options, and structured failure handling.
- Project status JSON includes `formal_confidence` with accepted state,
  target count, failed subjects, and target status mix.
- Project status text renders `Formal confidence: accepted (1 target;
  blocked=1)`.
- Summary mode renders the same target status mix.
- Missing formal-confidence target manifests make project status rejected
  without a traceback.
- CLI accepts `--formal-confidence-targets` and `--willard-map`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live project-status text/summary/JSON, live handoff with
  `--refresh-remotes`, compileall, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py`, with focused coverage in
`tests/test_project_status_report.py` and inherited handoff coverage in
`tests/test_handoff_status.py`.

The red focused run failed as intended because project status still reported
schema version `21`, lacked a `formal_confidence` JSON section, did not render
formal-confidence text or summary lines, lacked CLI overrides for the target
and Willard map paths, and did not accept a
`formal_confidence_targets_path` override for structured missing-manifest
failure tests.

The implementation validates `claims/formal_confidence_targets.json` against
`sources/willard_definition_map.json`, includes `formal_confidence` in
project-status JSON with target status counts, requires that validation for
aggregate acceptance, renders `Formal confidence:` and failure lines in text
output, adds the formal-confidence line to summary output, and exposes
`--formal-confidence-targets` / `--willard-map`.

Focused project-status and handoff tests passed 94 tests. Live project-status
text output rendered `Formal confidence: accepted (1 target; blocked=1)`;
live summary and refreshed handoff inherited `Formal confidence: 1 target;
blocked=1`; live project-status JSON reported schema version `22`.
`compileall`, `git diff --check`, and the full default suite passed; the full
suite ran 924 tests.
