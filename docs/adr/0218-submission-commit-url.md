# ADR-0218: Submission Commit URL

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0215 made the handoff report require accepted GitHub submission evidence,
and ADR-0217 made the vertical demo reproducible from exact commands. The
submission surface now proves that `fork/main` matches `HEAD`, but the text
and JSON report still stop at raw remote URLs and commit hashes.

That is enough for automation, but it is mildly hostile to a reviewer. The
handoff should include a direct fork commit URL for the submitted `HEAD`, so a
reader can open the exact submitted code without reconstructing the URL by
hand.

## Decision

Extend `autarkic_systems.github_submission` with a derived
`fork_commit_url`, built from the fork remote URL and current `HEAD`.

The URL will be included in JSON under the `head` object and rendered in text
as `Fork commit: ...`. Handoff output will inherit the expanded GitHub
submission payload and text.

This does not contact GitHub APIs, change submission acceptance, change remote
refresh behavior, change handoff readiness, or change project-status,
vertical-demo, evidence, claim, proof, source-status, runtime, trace/SVG,
scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because submission JSON/text lacks the
  fork commit URL.
- JSON output includes `head.fork_commit_url` for the current submitted commit.
- Text output renders `Fork commit: ...`.
- Handoff output inherits the expanded submission surface.
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

The red focused run failed as intended because submission JSON lacked
`head.fork_commit_url`, submission text lacked `Fork commit: ...`, and handoff
output did not inherit either surface.

The implementation adds a derived `fork_commit_url` property to
`GitHubSubmissionStatus`, includes it in JSON under `head.fork_commit_url`, and
renders it in text output as `Fork commit: ...`. Handoff output inherits the
expanded GitHub submission payload and formatter output. The change does not
contact GitHub APIs and does not alter acceptance or remote-refresh behavior.

Focused GitHub-submission and handoff tests passed 15 tests. Live
GitHub-submission text/JSON and handoff commands reported accepted status and
displayed the fork commit URL. `compileall`, `git diff --check`, and the full
default suite passed; the full suite ran 907 tests.
