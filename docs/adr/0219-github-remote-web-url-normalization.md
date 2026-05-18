# ADR-0219: GitHub Remote Web URL Normalization

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0218 added a direct fork commit URL to GitHub submission and handoff
reports. The first implementation works for the current HTTPS fork remote by
stripping `.git` and appending `/commit/<HEAD>`.

That is enough for the current checkout, but it is not robust for common
GitHub SSH remote forms such as `git@github.com:owner/repo.git` or
`ssh://git@github.com/owner/repo.git`. Those remotes are normal developer
configurations, and the handoff report should still point reviewers at a web
commit URL when the local remote is SSH.

## Decision

Normalize known GitHub remote URL forms into canonical web URLs before building
the submitted fork commit URL.

The normalization will support:

- `https://github.com/owner/repo.git`;
- `https://github.com/owner/repo`;
- `git@github.com:owner/repo.git`; and
- `ssh://git@github.com/owner/repo.git`.

Unrecognized remote URL forms will fall back to the existing `.git` stripping
behavior, so the report remains best-effort instead of rejecting an otherwise
accepted fork submission.

This does not contact GitHub APIs, change submission acceptance, change remote
refresh behavior, change handoff readiness, or change project-status,
vertical-demo, evidence, claim, proof, source-status, runtime, trace/SVG,
scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because SSH-style fork remotes produce
  non-web `fork_commit_url` values.
- HTTPS fork remotes keep the existing canonical commit URL.
- SCP-like SSH remotes produce `https://github.com/owner/repo/commit/<HEAD>`.
- `ssh://` GitHub remotes produce the same canonical web commit URL.
- Handoff output continues to inherit the submission commit URL.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status`.
- Green: the same focused suite passes after implementation.
- Regression: run handoff tests, live GitHub submission text/JSON, live
  handoff with `--refresh-remotes`, compileall, `git diff --check`, and the
  full default suite.

## After Action Report

Implemented in `autarkic_systems/github_submission.py`, with focused coverage
in `tests/test_github_submission_status.py` and inherited handoff coverage in
`tests/test_handoff_status.py`.

The red focused run failed as intended because SCP-like
`git@github.com:owner/repo.git` and
`ssh://git@github.com/owner/repo.git` fork remotes produced non-web
`fork_commit_url` values.

The implementation adds GitHub remote web URL normalization before constructing
the submitted fork commit URL. HTTPS remotes, SCP-like SSH remotes, and
`ssh://` GitHub remotes all resolve to `https://github.com/owner/repo`; unknown
remote forms keep the existing best-effort `.git` stripping fallback. Handoff
inherits the normalized commit URL through the existing GitHub submission
formatter and payload.

Focused GitHub-submission tests passed 10 tests. Adjacent GitHub-submission and
handoff tests passed 17 tests. Live GitHub-submission text/JSON and handoff
commands reported accepted status and retained the web fork commit URL.
`compileall`, `git diff --check`, and the full default suite passed; the full
suite ran 909 tests.
