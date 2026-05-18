# ADR-0191: End-Of-Month Handoff Status

Date: 2026-05-18

## Status

Accepted.

## Context

The project now has two compact operator commands:

- `python -m autarkic_systems.project_status --format summary` reports the
  accepted evidence surface and blocked frontier.
- `python -m autarkic_systems.github_submission` reports whether the current
  `HEAD` is visible on fork `main` and how far it is from upstream `origin/main`.

Those commands answer the two halves of the active end-of-month objective:
continue useful project work, and make sure code is submitted to the GitHub
project. A reviewer still has to run both commands and mentally combine the
result.

## Decision

Add an end-of-month handoff command that reuses the project-status and
GitHub-submission reports and renders them as one local text or JSON status.
The handoff command will be accepted only when the project status is accepted
and the current `HEAD` is visible on fork `main`.

## Success Criteria

- Red tests fail before implementation because the handoff module and CLI do
  not exist.
- `build_handoff_status` accepts injectable project and submission builders for
  deterministic tests.
- Text output includes a top-level handoff state, the compact project-status
  summary, and the GitHub submission status.
- JSON output includes accepted state, project-status summary text, project
  status payload, and GitHub submission payload.
- The live command runs locally without GitHub API access.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run `python -m autarkic_systems.handoff`,
  `python -m autarkic_systems.handoff --format json`, `python -m compileall -q
  autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_handoff_status` run failed because
`autarkic_systems.handoff` did not exist.

The implementation added `autarkic_systems/handoff.py`, a thin composition
layer over the existing project-status and GitHub-submission reports. It
provides text and JSON output, accepts injectable project and submission
builders for deterministic tests, and marks the handoff `ready` only when the
project status is accepted and the current `HEAD` is visible on fork `main`.

The focused handoff suite passed with 5 tests. Live text and JSON handoff runs
accepted the current project status and GitHub submission state before this ADR
was committed. Handoff text/JSON, `compileall`, `git diff --check`, and the
full default suite also passed; the full suite ran 801 tests.
