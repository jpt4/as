# ADR-0165: Standard-Signal Execution Readiness Boundary

Date: 2026-05-18

## Status

Accepted.

## Context

The `standard-signal` command-token source-status record has no live
resolution questions after ADR-0151. Its recipient surface is rejected, and
its self-target surfaces are preserved as unsupported. Project status still
shows the blocked runtime surfaces, but unlike the write-buffer source-status
record, it does not expose an explicit `execution_readiness` decision.

That omission leaves a small operator ambiguity: a record with no unresolved
questions can look ready for execution work even when the settled decision is
to keep the command-token execution boundary preserved as unsupported.

## Decision

Add an explicit `execution_readiness` object to
`sources/standard_signal_command_semantics_status.json`:

- decision `preserved-unsupported`;
- `execution_change_allowed: false`;
- no unresolved-question blockers; and
- a summary explaining that standard-signal command-token execution is not
  source-ready for implementation because the settled self-target decision is
  preservation under existing unsupported boundaries.

This ADR does not change Universal Cell runtime behavior, claim examples,
proof certificates, traces, SVGs, evidence bundles, or schema versions.

## Success Criteria

- Red tests fail before implementation because the standard-signal
  source-status record lacks `execution_readiness`.
- Source-status JSON exposes the `preserved-unsupported` readiness decision.
- Project-status JSON and text render the standard-signal readiness decision
  alongside the existing write-buffer readiness decision.
- Source-status frontier JSON and text render the same readiness decision.
- Project-status schema remains `15`; source-status frontier schema remains
  `2`.
- Runtime behavior remains unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_standard_signal_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli`
  fails before the source-status readiness field is added.
- Green: the same focused suite passes after updating the source-status record
  and expected text/JSON surfaces.
- Regression: run project-status JSON, source-status JSON, JSON parsing for
  touched files, `compileall`, `git diff --check`, and the full default suite
  before commit.

## After Action Report

ADR-0165 added an explicit `execution_readiness` object to
`sources/standard_signal_command_semantics_status.json` with decision
`preserved-unsupported`, `execution_change_allowed: false`, and no live
resolution-question blockers. The source-status frontier and aggregate
project-status reports now render that boundary beside the implemented
write-buffer readiness decision.

The red check was observed before implementation: the default suite failed
because the standard-signal source-status record lacked `execution_readiness`
and the project/source-status text and JSON expectations could not find the
standard-signal readiness boundary.

Focused verification passed after implementation:

```sh
python -m unittest tests.test_standard_signal_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 97 tests passed.

Machine-readable status checks accepted the same readiness boundary:

- `python -m autarkic_systems.project_status --format json` accepted schema
  `15`;
- `python -m autarkic_systems.source_status --format json` accepted schema
  `2`;
- both reports show `standard-signal` readiness as
  `preserved-unsupported`, with execution changes disallowed and no blockers.

Regression verification also passed:

- `jq empty sources/standard_signal_command_semantics_status.json`;
- `python -m compileall -q autarkic_systems tests`;
- `git diff --check`;
- `python -m unittest discover` ran 732 tests successfully.

This ADR did not change Universal Cell runtime behavior, transition claims,
proof certificates, traces, SVGs, evidence bundles, or schema versions.
