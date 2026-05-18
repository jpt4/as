# ADR-0193: Refresh Remotes Before Handoff

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0192 reports the local freshness of `fork/main` evidence, but the operator
still has to run `git fetch` manually when they want fresh remote-tracking
refs. The end-of-month handoff command should be able to perform that refresh
explicitly before reporting, while still keeping the default command local and
non-networking.

The refresh should update the same refs the submission command inspects:
`refs/remotes/fork/main` and `refs/remotes/origin/main`.

## Decision

Add a `--refresh-remotes` option to GitHub submission and handoff commands. When
requested, the submission command will fetch fork `main` into
`refs/remotes/fork/main` and origin `main` into `refs/remotes/origin/main`
before building the status report. Refresh results will be carried in text and
JSON, and a failed requested refresh will make submission and handoff status
not accepted.

## Success Criteria

- Red tests fail before implementation because `--refresh-remotes` is not
  accepted and submission payloads have no refresh result.
- GitHub submission status accepts a `refresh_remotes` option.
- Refresh runs explicit fetch commands for fork and origin remote-tracking
  refs before reading `HEAD`, remotes, divergence, or freshness.
- JSON output includes requested/accepted refresh results.
- Text output renders refresh state when refresh is requested.
- Handoff accepts `--refresh-remotes` and passes it to submission status.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status
  tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run `python -m autarkic_systems.github_submission
  --refresh-remotes`, `python -m autarkic_systems.handoff --refresh-remotes`,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_github_submission_status tests.test_handoff_status`
run failed because `--refresh-remotes` was not accepted, submission status did
not accept `refresh_remotes`, handoff did not accept a submission runner, and
the payload had no `remote_refresh` field.

The implementation added explicit refresh support to
`autarkic_systems/github_submission.py`: when requested, it fetches fork `main`
into `refs/remotes/fork/main` and origin `main` into
`refs/remotes/origin/main` before building the status report. Refresh results
are included in text and JSON. A requested refresh failure makes submission
status `refresh-failed`, which also makes handoff not ready. The implementation
also added `--refresh-remotes` to `autarkic_systems/handoff.py` and threads the
same option into the submission report.

The focused GitHub-submission and handoff suites passed with 14 tests. Live
`github_submission --refresh-remotes` and `handoff --refresh-remotes` runs both
reported `Remote refresh: accepted (fork/main, origin/main)` before this ADR was
committed. `compileall`, `git diff --check`, and the full default suite also
passed; the full suite ran 805 tests.
