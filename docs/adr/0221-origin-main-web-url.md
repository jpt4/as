# ADR-0221: Origin Main Web URL

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0218 through ADR-0220 made the fork side of the GitHub submission handoff
directly reviewable: the report now includes a submitted fork commit URL and a
fork `main` browser URL. The upstream project is still represented only by the
raw origin git remote URL and the tracking issue URL.

The handoff should also name the browser URL for upstream `origin/main`, so a
reviewer can move between the upstream project, the fork submission, the exact
commit, and the tracking issue without reconstructing any GitHub web URLs by
hand.

## Decision

Add a derived `origin_main_url` to `autarkic_systems.github_submission`, using
the same GitHub remote web URL normalization introduced by ADR-0219.

The JSON payload will include `origin_main.web_url`, and text output will
render `Origin main: ...`. Handoff output will inherit the expanded GitHub
submission payload and formatter output.

This does not contact GitHub APIs, change submission acceptance, change remote
refresh behavior, change handoff readiness, or change project-status,
vertical-demo, evidence, claim, proof, source-status, runtime, trace/SVG,
scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because submission JSON/text lacks an
  origin `main` web URL.
- JSON output includes `origin_main.web_url`.
- Text output renders `Origin main: ...`.
- SSH-normalized origin remotes produce the same canonical origin `main` web
  URL.
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
`origin_main.web_url`, submission text lacked `Origin main: ...`, and handoff
output did not inherit either surface.

The implementation adds a derived `origin_main_url` property to
`GitHubSubmissionStatus`, includes it in JSON under `origin_main.web_url`, and
renders it in text output as `Origin main: ...`. It reuses the ADR-0219 GitHub
remote web URL normalizer, so HTTPS and common SSH origin remotes resolve to
the same canonical upstream `main` browser URL.

Focused GitHub-submission and handoff tests passed 18 tests. Live
GitHub-submission text/JSON and handoff commands reported accepted status and
displayed the origin `main` web URL. `compileall`, `git diff --check`, and the
full default suite passed; the full suite ran 910 tests.
