# ADR-0295: Source Status Frontier Closure Summary

Date: 2026-05-21

## Status

Accepted.

## Context

ADR-0171 closed the active `standard-signal` source-review safe-next request by
recording a dated source snapshot that found no new command-token execution
evidence. The focused source-status frontier therefore now renders
`Safe next slice: none` while still reporting `standard-signal` as blocked and
preserved unsupported.

That combination is correct but too implicit for automation. A consumer can
see that the aggregate safe-next string is empty, but it cannot easily
distinguish intentional closure of the safe-next queue from missing,
malformed, or rejected source-status input. The same consumer must also scan
per-source readiness entries to learn that write-buffer command surfaces are
implemented while the remaining `standard-signal` execution boundary is
preserved unsupported pending new source evidence.

## Decision

Add a compact `closure_summary` object under the focused
`autarkic_systems.source_status` report's `frontier` field. The summary is
derived only from the already-built focused frontier payload:

- The focused source-status schema version will bump from `3` to `4`.
- `safe_next_slice_state` is `closed` only when the focused report is accepted
  and the aggregate `safe_next_slice` is empty.
- `remaining_blocked_commands` comes from the accepted frontier's blocked
  command list.
- `preserved_unsupported_commands` comes from accepted per-source
  `execution_readiness.decision == "preserved-unsupported"` entries.
- `implemented_commands` comes from accepted per-source
  `execution_readiness.decision == "implemented"` entries.
- `execution_change_allowed` is true only when an accepted readiness entry
  allows execution changes.
- `reason` is a concise stable string explaining the closed current state:
  `standard-signal requires new source evidence`.

Rejected focused reports must fail closed. Missing, malformed, or
schema-invalid source-status input will not claim closed or implemented state;
the summary will report an unknown state with empty derived command lists.

Text output will add one concise closure line after the existing execution
readiness section. It must not remove or rewrite the existing source-status
details, latest source-review section, safe-next line, missing/invalid path
diagnostics, source-status records, command semantics, project-status schema,
runtime behavior, claims, proofs, traces, SVGs, evidence bundles, vertical
demo, GitHub submission, or suite-selection behavior.

## Success Criteria

- Red tests fail before implementation because focused JSON lacks
  `frontier.closure_summary`.
- Red tests fail before implementation because focused text lacks a concise
  closure line.
- Red tests fail before implementation because the focused schema version is
  still `3`.
- Checked-in default focused source-status report remains accepted.
- Focused source-status JSON reports schema version `4`.
- JSON exposes `frontier.closure_summary.safe_next_slice_state == "closed"`
  for the checked-in accepted frontier with empty aggregate safe-next slice.
- JSON distinguishes the closed queue from rejected missing or invalid
  source-status input by using an unknown closure state with no implemented
  command claims on rejected reports.
- The default summary reports remaining blocked command
  `standard-signal`, preserved unsupported command `standard-signal`,
  implemented commands `write-buf-zero` and `write-buf-one`,
  `execution_change_allowed: false`, and reason
  `standard-signal requires new source evidence`.
- Text output includes a concise closure/readiness line without changing
  existing source-status detail sections.

## Test Plan

- Red:
  `python -m unittest tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_default_report_exposes_closure_summary tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_text_report_renders_closure_summary_line tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_rejected_report_does_not_claim_closed_closure_summary`.
- Red schema:
  `python -m unittest tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_default_report_accepts_checked_in_source_status_frontier`.
- Green:
  `python -m unittest tests.test_source_status_frontier_cli tests.test_suite_selection`.
- Live JSON assertion:
  `python -m autarkic_systems.source_status --format json`.
- Assert the live focused report is accepted and reports closed safe-next
  state, `standard-signal` remaining blocked and preserved unsupported,
  `write-buf-zero` / `write-buf-one` implemented, execution changes not
  allowed, and reason `standard-signal requires new source evidence`.
- Run `python -m compileall autarkic_systems tests`.
- Run `git diff --check`.
- Run the fast suite if runtime permits.

## After Action Report

The focused closure red run was:

```sh
python -m unittest tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_default_report_exposes_closure_summary tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_text_report_renders_closure_summary_line tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_rejected_report_does_not_claim_closed_closure_summary
```

It failed in the expected places: accepted and rejected JSON checks raised
`KeyError: 'closure_summary'`, and formatted text did not contain the
`Closure summary:` line. The red run executed 3 tests in 0.010s.

A follow-up schema red check was:

```sh
python -m unittest tests.test_source_status_frontier_cli.SourceStatusFrontierCliTests.test_default_report_accepts_checked_in_source_status_frontier
```

It failed because `SOURCE_STATUS_SCHEMA_VERSION` was still `3` instead of `4`.
The red run executed 1 test in 0.004s.

The implementation stayed in `autarkic_systems.source_status`. It adds a
derived `frontier.closure_summary` object to the focused report, bumps the
focused source-status schema to `4`, and renders a compact text line after the
existing execution-readiness section. The summary is derived from the accepted
frontier's existing blocked-command, safe-next, and readiness fields. Missing
or schema-invalid source-status input reports unknown closure state with empty
derived command lists, so rejected reports do not claim closed or implemented
state.

The exact focused closure tests then passed:

```text
Ran 3 tests in 0.019s
OK
```

Focused verification passed:

```sh
python -m unittest tests.test_source_status_frontier_cli tests.test_suite_selection
```

Observed result:

```text
Ran 24 tests in 1.990s
OK
```

The live JSON assertion ran the real module command through subprocess:

```sh
python -m autarkic_systems.source_status --format json
```

It confirmed accepted focused status, schema version `4`, closed safe-next
state, remaining blocked command `standard-signal`, preserved unsupported
command `standard-signal`, implemented commands `write-buf-zero` and
`write-buf-one`, execution changes disallowed, and reason
`standard-signal requires new source evidence`.

Additional verification passed:

```sh
python -m compileall autarkic_systems tests
git diff --check
```

The fast suite also passed:

```sh
python -m autarkic_systems.test_suite_selection --suite fast
```

Observed result:

```text
Ran 1179 tests in 263.869s
OK
manifest: as-test-suite-selection-v1 suite: fast module_count: 129
```

This remains a focused reporting change only. It does not add or edit
source-status JSON records, change project-status schema or acceptance
semantics, change runtime behavior, promote `standard-signal` execution, alter
write-buffer command semantics, or touch GitHub submission, vertical-demo, or
suite-selection source files.
