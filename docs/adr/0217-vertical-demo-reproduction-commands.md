# ADR-0217: Vertical Demo Reproduction Commands

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0216 made the vertical demo point to the concrete evidence trail behind the
current checked post-handoff signal-routing demonstration. That tells a reader
which artifacts matter, but the first-run digest still does not name the short
command sequence that reproduces the demonstration and its handoff status.

The repository already has the required commands: vertical demo, focused
network-sequence demo, project status, and handoff. The top-level digest should
surface those exact commands so the evidence trail is immediately runnable.

## Decision

Extend `autarkic_systems.vertical_demo` with `reproduction_commands`, an
ordered list of command records containing a short label and the exact command
string to run.

The text report will render those commands under a `Reproduce:` section. JSON
output and handoff output will inherit the same structured list.

This does not change runtime behavior, claims, proof rules, validation
authority, project-status schema, source-status decisions, registry schemas,
trace/SVG rendering, scheduler, topology, timing, or command semantics.

## Success Criteria

- Red tests fail before implementation because vertical demo JSON/text lacks
  `reproduction_commands`.
- JSON output lists exact commands for the vertical demo, network-sequence demo
  JSON, project-status summary, and refreshed handoff.
- Text output renders a `Reproduce:` section with the same commands.
- Handoff output inherits the expanded vertical demo digest.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_vertical_demo_digest`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent vertical-demo, network-sequence demo, and handoff
  tests, live vertical-demo text/JSON, live handoff with `--refresh-remotes`,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/vertical_demo.py`, with focused coverage in
`tests/test_vertical_demo_digest.py` and inherited handoff fixture coverage in
`tests/test_handoff_status.py`.

The red focused run failed as intended because vertical demo JSON/text lacked
`reproduction_commands`, text output lacked a `Reproduce:` section, and handoff
output did not inherit the command list.

The implementation adds a structured command list to the vertical demo digest,
renders the same list in text output, and lets handoff inherit the expanded
digest. The commands cover the vertical demo, focused network-sequence demo
JSON, compact project status, and refreshed handoff.

Focused vertical-demo tests passed 4 tests. Adjacent handoff, vertical-demo,
and network-sequence demo tests passed 25 tests. Live vertical-demo text/JSON
and handoff commands reported accepted status and carried the reproduction
command list. `compileall`, `git diff --check`, and the full default suite
passed; the full suite ran 907 tests.
