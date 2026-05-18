# ADR-0167: Recipient Write-Buffer Readiness Question

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0161 implements write-buffer append execution for direct self-mailbox and
completed self-target command-buffer surfaces. ADR-0163 keeps delivered
recipient `write-buf-zero` and `write-buf-one` command-message inputs under
the recipient non-init rejection boundary, and ADR-0166 makes that recipient
surface the active safe-next frontier.

The source-status payload still has a misleading gap: project status shows
write-buffer readiness as broadly `implemented`, while the same source-status
record still lists `recipient-command-message` as a blocked runtime surface.
That can make the active recipient frontier look like a documentation afterthought
instead of a live source-resolution question.

The local source evidence is not empty. The formal model routes
input-channel special messages through `process-special-message`; RAA and
FSMSIM route write-buffer special messages to append behavior; SEMSIM still
diverges by clearing the buffer after append. AS therefore needs an explicit
recipient command-message surface question before changing recipient runtime
behavior.

## Decision

Add `recipient-command-message-surface` as a live write-buffer source-status
resolution question, with evidence summarizing the formal/RAA/FSMSIM append
pressure and the SEMSIM clearing divergence. Change write-buffer
`execution_readiness` from broad `implemented` to
`self-target-implemented-recipient-blocked`, with execution changes disallowed
until that recipient surface is resolved.

This ADR does not change Universal Cell runtime behavior, claims, proof
certificates, traces, SVGs, evidence bundles, or schema versions.

## Success Criteria

- Red tests fail before implementation because write-buffer source status has
  no live recipient command-message resolution question and still reports
  broad implemented readiness.
- Write-buffer source status records `recipient-command-message-surface` as
  a live required resolution question with matching evidence.
- Project-status and source-status frontier JSON/text show the live recipient
  write-buffer question and the blocked write-buffer readiness gate.
- Project-status schema remains `15`; source-status frontier schema remains
  `2`.
- Runtime behavior remains unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli`
  fails before the source-status record is updated.
- Green: the same focused suite passes after updating the source-status
  record and expected text/JSON surfaces.
- Regression: run project-status JSON, source-status JSON, JSON parsing for
  touched source-status files, `compileall`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

ADR-0167 added `recipient-command-message-surface` as a live write-buffer
source-status question. The question records that the formal model and
RAA/FSMSIM witnesses route input-channel write-buffer special messages toward
append behavior, while AS still has checked recipient rejection coverage and
SEMSIM still diverges on post-append buffer clearing.

The red focused run was observed before implementation:

```sh
python -m unittest tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 99 tests ran with 8 failures because write-buffer source status lacked
the recipient question and still reported broad `implemented` readiness.

Focused verification passed after implementation:

```sh
python -m unittest tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli
```

Result: 99 tests passed.

Machine-readable status checks accepted the new live question:

- `python -m autarkic_systems.project_status --format json` accepted schema
  `15` and reported write-buffer required question
  `recipient-command-message-surface`;
- `python -m autarkic_systems.source_status --format json` accepted schema
  `2` and reported the same question;
- both reports show write-buffer readiness as
  `self-target-implemented-recipient-blocked`, with execution changes
  disallowed and the recipient question named as the blocker.

Regression verification also passed:

- `jq empty sources/write_buffer_command_semantics_status.json`;
- `python -m compileall -q autarkic_systems tests`;
- `git diff --check`;
- `python -m unittest discover` ran 732 tests successfully.

This ADR did not change Universal Cell runtime behavior, transition claims,
proof certificates, traces, SVGs, evidence bundles, or schema versions.
