# ADR-0054: Recipient Non-Init Command Rejection Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0053 records that recipient-side `standard-signal`, write-buffer, and
multi-command inputs remain blocked by source-status evidence. The current
runtime already rejects those inputs. As with earlier unsupported command
frontiers, that rejection boundary should become a named transition claim
before later work depends on it.

## Decision

Add a named predicate and claim for recipient non-init command-message
rejection:

- predicate: `recipient_non_init_command_message_rejected`;
- claim ID: `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`;
- proof rule: existing `manifest-example`;
- object-language predicate-symbol entry.

The predicate covers single `standard-signal`, `write-buf-zero`, and
`write-buf-one` command-message inputs, fixed-cell upstream non-init
command-message inputs, and multiple simultaneous command-message input
conflicts. It requires `rejected-input`, cleared consumed input, preserved
role/memory, no output creation, and source-specific upstream handling.

## Success Criteria

- Red tests fail before implementation because the predicate, manifest claim,
  proof certificate, and language symbol are absent.
- The predicate accepts fixed direct non-init command-message rejection.
- The predicate accepts fixed upstream non-init command-message rejection.
- The predicate accepts stem multi-command conflict rejection while preserving
  control and buffer state.
- The predicate rejects wrong status, changed role/memory, uncleared input, and
  wrong upstream handling.
- The predicate ignores init-family command-message inputs and ordinary binary
  standard-signal inputs.
- Claim manifest examples include both accepted and rejected cases.
- Proof certificates cover the new claim.
- The transition-claim object language names the new predicate symbol.

## Consequences

- The non-init recipient command frontier becomes explicit evidence rather than
  an informal side effect of runtime tests.
- Later work can add traces or revisit execution semantics without losing the
  current boundary.
- Actual non-init command execution remains blocked by ADR-0053.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_non_init_command_rejection_claim`
failed because `recipient_non_init_command_message_rejected` was absent from
`autarkic_systems.transition_predicates`.

The green implementation added the predicate, claim manifest examples, proof
certificate entry, object-language predicate symbol, and source-status updates
that move the next slice to a schematic-linked rejection trace.

Final verification is recorded in `LOG.md`.
