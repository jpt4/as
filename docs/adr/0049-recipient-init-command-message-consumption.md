# ADR-0049: Recipient Init Command-Message Consumption

Date: 2026-05-17

Status: Accepted

## Context

ADR-0044 through ADR-0047 made neighbor-target command-buffer delivery
executable, claimed, traced, and rendered. ADR-0048 then restored and reviewed
the PRC source witnesses for what recipient cells should do with delivered
command-message tokens on input channels.

Those witnesses allow one narrow executable slice. The formal model routes
input-channel special messages on wire, proc, and stem cells through
`process-special-message`. The restored legacy sources agree that
`stem-init`, `wire-r-init`, `wire-l-init`, `proc-r-init`, and `proc-l-init`
are special messages with role/memory initialization behavior. They do not
resolve `standard-signal` command-message input divergence, write-buffer input
semantics, or simultaneous multi-command input conflict policy.

## Decision

Implement recipient-side input-channel consumption for single init-family
command messages only:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

The implementation uses the same role/memory target map as the existing
self-mailbox init-family behavior, but gives recipient input-channel
consumption its own transition status:
`recipient-init-command-message-processed`.

The slice deliberately preserves the existing boundaries for:

- `standard-signal` command-message inputs;
- `write-buf-zero` and `write-buf-one` command-message inputs;
- multiple simultaneous command-message inputs;
- occupied-output blocking in the current AS transition probe.

## Success Criteria

- Red tests fail before implementation because input-channel init-family
  command messages are still rejected and the transition language lacks the new
  recipient status.
- A fixed wire/proc cell consumes one init-family command-message input and
  reconfigures to the target role and memory.
- A fixed cell with empty input consumes a pulled upstream init-family
  command-message token.
- A stem cell consumes one init-family command-message input and clears input,
  output, automail, self-mailbox, control, and buffer state.
- `stem-init` command-message input resets the recipient cell to canonical stem
  state while remaining distinct from the older fixed-cell `si` shorthand
  status.
- Unsupported `standard-signal` and write-buffer command-message inputs remain
  rejected and cleared.
- Multiple simultaneous command-message inputs remain rejected and cleared.
- The transition-claim object language names the new transition status.

## Consequences

- Delivered neighbor-target init commands now have an executable recipient
  behavior instead of stopping at output-channel representation.
- The next honest promotion step is a named transition claim and proof
  certificate for this recipient init-family command-message subset.
- Full recipient command-message consumption remains blocked until AS resolves
  standard-signal, write-buffer, and multi-command conflict semantics.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_init_command_messages tests.test_command_channel_tokens tests.test_neighbor_command_buffer_delivery tests.test_recipient_command_consumption_source_status tests.test_stem_command_execution_source_status`
failed with ten failures and one error because input-channel init-family
command messages were still rejected, the transition language lacked
`recipient-init-command-message-processed`, and the source-status artifacts
still pointed to implementation as the next step.

The green implementation adds recipient input-channel init-family
command-message consumption to fixed and stem cells, updates the transition
language status vocabulary, records ADR-0049 in the recipient source-status
artifact, and moves the stem command execution next slice to claim promotion.

Final verification is recorded in `LOG.md`.
