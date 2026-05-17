# ADR-0059: Multi-Command Recipient Input Policy

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0058 left `standard-signal` command-token execution blocked and moved the
recipient command-message frontier to multiple simultaneous command-message
inputs. AS already consumes exactly one init-family command-message input, and
the ADR-0054 rejection claim already treats conflicting command-message inputs
as a rejected boundary.

The remaining question is whether AS should try to prioritize, sequence, or
reject multiple command-message tokens when more than one input channel carries
a command token in the same activation.

## Decision

Add a structured multi-command recipient input policy status artifact:

- `sources/multi_command_recipient_input_policy_status.json`;
- an explicit `reject-multiple-recipient-command-message-inputs` decision;
- proof that existing fixed direct, fixed upstream, and stem direct conflict
  behavior already rejects and clears active command input;
- an added claim-manifest example for an all-init command conflict;
- source-status frontier updates that make a multi-command rejection trace the
  next safe slice.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/multi_command_recipient_input_policy_status.json` is absent.
- The artifact records that the accepted command-message input cardinality is
  exactly one.
- The artifact records that two or more command-message tokens are rejected,
  not prioritized or sequenced.
- Runtime tests prove fixed direct, fixed upstream, and stem direct conflicts
  already match the policy.
- The recipient non-init rejection claim manifest includes an all-init conflict
  example, with certificate coverage.
- Existing source-status frontiers move away from selecting the policy and
  toward a schematic-linked multi-command rejection trace.

## Consequences

AS avoids inventing a command priority rule not present in the current sources.
The next visible slice is a trace showing multiple command-message input
rejection, using the already-claimed rejection boundary.

## After Action Report

The green implementation added
`sources/multi_command_recipient_input_policy_status.json`,
`docs/multi-command-recipient-input-policy-status.md`, and tests proving the
existing fixed direct, fixed upstream, and stem direct reject-and-clear
behavior.

Runtime behavior was intentionally unchanged. The
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` claim manifest gained a fixed
all-init conflict example with proof-certificate coverage. Recipient and stem
source-status frontiers now point to a schematic-linked multi-command rejection
trace as the next safe slice.
