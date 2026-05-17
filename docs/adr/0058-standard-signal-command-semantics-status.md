# ADR-0058: Standard-Signal Command Semantics Status

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0057 kept write-buffer command execution blocked and moved the next source
frontier to `standard-signal`. AS already implements ordinary standard-signal
routing and stem buffer accumulation, but `standard-signal` as a command token
is a different question.

The formal command table names `standard-signal` as command offset 0 for each
target range. The legacy sketches, however, treat standard signals primarily
as binary input patterns, exclude `standard-signal` from the special-message
sets, or map command-buffer cases differently.

## Decision

Add a structured standard-signal command semantics status artifact:

- `sources/standard_signal_command_semantics_status.json`;
- formal-model anchors for command-table placement and ordinary
  standard-signal processing;
- RAA, SEMSIM, and FSMSIM legacy witnesses for standard/special-message
  classification;
- an explicit
  `do-not-implement-standard-signal-command-execution-yet` decision;
- updates to recipient and stem source-status frontiers.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/standard_signal_command_semantics_status.json` is absent.
- The artifact records that the formal command table includes
  `standard-signal` at command offset 0.
- The artifact records that ordinary standard-signal processing is already a
  binary-input behavior, not command-token execution.
- The artifact records that legacy special-message sets exclude
  `standard-signal`.
- The artifact records RAA's divergent command-buffer placement for
  `standard-signal`.
- The artifact blocks command-token execution for recipient command messages,
  self-mailbox commands, and self-target command-buffer commands.
- Existing source-status frontiers move away from `standard-signal` execution
  and toward multi-command conflict policy.

## Consequences

AS keeps ordinary standard-signal routing/buffering separate from
`standard-signal` command-token execution. The next non-init recipient frontier
is multi-command conflict policy.

## After Action Report

The green implementation added
`sources/standard_signal_command_semantics_status.json`, the human-facing
`docs/standard-signal-command-semantics-status.md` note, and tests proving the
formal command-table anchor, ordinary binary-input standard-signal anchor, RAA
command-offset divergence, and SEMSIM/FSMSIM special-message exclusion.

Runtime behavior was intentionally unchanged. Recipient and stem source-status
frontiers moved to multi-command recipient input conflict policy, with
`standard-signal` command-token execution revisitable only if a later source
resolves the command-token, binary-input, recipient-surface, and
self-target-surface boundaries. ADR-0059 later selected that multi-command
policy and moved the frontier to a rejection trace.
