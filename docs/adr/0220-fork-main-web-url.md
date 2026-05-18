# ADR-0220: Fork Main Web URL

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0218 added a direct browser URL for the submitted fork commit, and
ADR-0219 normalized common GitHub remote forms before building that URL. The
handoff now points to the exact submitted commit, but the public fork landing
branch is still only represented by a raw git remote URL and a local
`fork/main` match line.

Reviewers should not have to reconstruct the browser URL for fork `main`.
The submission report should name the fork `main` web URL alongside the
submitted commit URL.

## Decision

Add a derived `fork_main_url` to `autarkic_systems.github_submission`, using
the same GitHub remote web URL normalization introduced by ADR-0219.

The JSON payload will include `fork_main.web_url`, and text output will render
`Fork main: ...`. Handoff output will inherit the expanded GitHub submission
payload and formatter output.

This does not contact GitHub APIs, change submission acceptance, change remote
refresh behavior, change handoff readiness, or change project-status,
vertical-demo, evidence, claim, proof, source-status, runtime, trace/SVG,
scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because submission JSON/text lacks a
  fork `main` web URL.
- JSON output includes `fork_main.web_url`.
- Text output renders `Fork main: ...`.
- SSH-normalized fork remotes produce the same canonical fork `main` web URL.
- Handoff output inherits the expanded submission surface.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_github_submission_status
  tests.test_handoff_status`.
- Green: the same focused suite passes after implementation.
- Regression: run live GitHub submission text/JSON, live handoff with
  `--refresh-remotes`, compileall, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented in `autarkic_systems/github_submission.py`, with focused coverage
in `tests/test_github_submission_status.py` and inherited handoff coverage in
`tests/test_handoff_status.py`.

The red focused run failed as intended because submission JSON lacked
`fork_main.web_url`, submission text lacked `Fork main: ...`, and handoff
output did not inherit either surface.

The implementation adds a derived `fork_main_url` property to
`GitHubSubmissionStatus`, includes it in JSON under `fork_main.web_url`, and
renders it in text output as `Fork main: ...`. It reuses the ADR-0219 GitHub
remote web URL normalizer, so HTTPS and common SSH fork remotes resolve to the
same canonical fork `main` browser URL.

Focused GitHub-submission and handoff tests passed 17 tests. Live
GitHub-submission text/JSON and handoff commands reported accepted status and
displayed the fork `main` web URL. `compileall`, `git diff --check`, and the
full default suite passed; the full suite ran 909 tests.
