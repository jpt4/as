# ADR-0190: GitHub Submission Status

Date: 2026-05-18

## Status

Accepted.

## Context

The project goal includes submitting work to the GitHub project. The canonical
upstream repository currently rejects direct pushes from this workspace, so the
working submission path has been: push the ADR branch to the fork, fast-forward
local `main`, attempt upstream `main`, push fork `main`, and report the result
on upstream issue #1.

That process is recorded in issue comments and shell history, but the
repository does not yet have a cheap local command that reports the current
submission evidence. Operators should not have to reconstruct whether the
current `HEAD` is visible on the fork from raw git commands.

## Decision

Add a GitHub submission status command that inspects local git evidence for the
current branch, current commit, origin and fork remote URLs, fork `main`
matching state, and local `HEAD` versus `origin/main` divergence. The command
will render text and JSON without contacting GitHub APIs, so it remains a local
handoff aid rather than a network-dependent submission authority.

## Success Criteria

- Red tests fail before implementation because the submission status module and
  CLI do not exist.
- `build_github_submission_status` accepts an injectable command runner for
  deterministic tests.
- JSON status includes current branch, `HEAD`, remote URLs, fork-main match
  state, origin-main ahead/behind counts, and tracking issue URL.
- Text status reports the fork submission state and upstream divergence in a
  compact operator-readable form.
- The live command reports the current fork `main` matches `HEAD`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status`.
- Green: the same focused suite passes after implementation.
- Regression: run `python -m autarkic_systems.github_submission`,
  `python -m autarkic_systems.github_submission --format json`, `python -m
  compileall -q autarkic_systems tests`, `git diff --check`, and the full
  default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_github_submission_status` run failed because
`autarkic_systems.github_submission` did not exist.

The implementation added `autarkic_systems/github_submission.py` with a local
git-backed text/JSON command, deterministic fake-runner test seams, fork-main
match detection, origin-main divergence counts, remote URL reporting, and the
upstream tracking issue URL. The command does not contact GitHub APIs; it
reports local git evidence about whether the current `HEAD` is visible on
`fork/main`.

The focused test suite passed with 5 tests. Live text and JSON runs reported
the current `HEAD` as submitted to fork `main` before this ADR was committed.
Project-status summary, submission-status JSON, `compileall`, `git diff
--check`, and the full default suite also passed; the full suite ran 796 tests.
