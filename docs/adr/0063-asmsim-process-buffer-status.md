# ADR-0063: ASMSIM Process-Buffer Status

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0062 reviewed `practice/legacy/guile-asmsim.scm` and found that it
strengthens the command-semantics blocker rather than resolving
`standard-signal` or write-buffer command-token execution.

The local PRC source tree also contains `practice/asmsim.scm`, a newer
Universal Cell abstract state machine simulator. Its stem `process-buffer`
section is relevant to the same frontier, but the source itself contains
warnings: the process-buffer section says it needs documentation, and the
auxiliary definitions say to confirm the message-list codes. AS needs that
evidence captured before anyone treats this simulator as canonical command
execution authority.

## Decision

Add `sources/asmsim_process_buffer_status.json` and a human-facing note that
record the process-buffer evidence in `practice/asmsim.scm`.

This ADR will record:

- the `qs18` process-buffer branch set;
- the explicit "need documentation here" and "XXX CONFIRM MSGLIST CODES"
  source warnings;
- the `id+msg?`, `id+10b5?`, `id+11b5?`, `tar+0b4?`, `tar+sic?`,
  `id+nop?`, and `tar+nop?` predicate families;
- the `msg-list` placeholder and absence of named `standard-signal`,
  `write-buf-zero`, and `write-buf-one` command tokens;
- cross-links from standard-signal, write-buffer, and stem command
  source-status artifacts.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/asmsim_process_buffer_status.json` is absent.
- The source-status artifact records the relevant local witness path and loci.
- Tests verify that the source contains the process-buffer documentation and
  message-code warning comments.
- Tests verify that the source records process-buffer predicate families rather
  than the formal named command table.
- Tests verify that the existing standard-signal, write-buffer, and stem
  command source-status files reference this ADR-0063 evidence.
- Runtime behavior remains unchanged.

## Consequences

`practice/asmsim.scm` is useful implementation evidence, but its own comments
mark the process-buffer command-code layer as unsettled. AS should keep
`standard-signal` and write-buffer command execution blocked until a later ADR
resolves the formal named command table, legacy simulator divergences, and
ASMSIM's incomplete message-code documentation.

## Test Plan

- Red: `python -m unittest tests.test_asmsim_process_buffer_status` fails
  because the source-status artifact is absent.
- Green: the same focused test passes after adding the artifact and
  cross-links.
- Regression: run adjacent command source-status tests and the full default
  suite before commit.

## After Action Report

Implemented in `sources/asmsim_process_buffer_status.json` and
`docs/asmsim-process-buffer-status.md`.

The focused red run failed because
`sources/asmsim_process_buffer_status.json` was absent. The green
implementation records `practice/asmsim.scm` as process-buffer evidence, but
not execution authority: it contains explicit documentation and message-code
confirmation warnings, uses process-buffer code-shape predicates, and contains
a literal `msg-list` placeholder rather than the formal named command table.

Existing standard-signal, write-buffer, and stem command source-status
artifacts now cross-link this evidence. Runtime behavior remains unchanged.
