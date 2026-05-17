# ADR-0077: Neighbor Delivery Recipient Chain

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0076 completed the integrated evidence bundle for a stem cell delivering a
completed neighbor-target command buffer to an output channel. ADR-0065 already
registers recipient-side init-family command-message consumption as a separate
evidence bundle.

Those two slices are individually checkable, but the repository still lacks a
small executable bridge proving that the delivered output tuple can be composed
into a recipient cell's upstream tuple and consumed by the existing recipient
logic. Without that bridge, the project can validate both sides while leaving
the handoff implicit.

The bridge should remain narrower than a multi-cell simulator. It should
compose one sender transition and one recipient transition, refuse to overwrite
recipient input/upstream state, and preserve the current source-status
boundaries for non-init delivered commands.

## Decision

Add a small transition-chain helper in
`autarkic_systems/transition_chains.py` for the neighbor delivery to recipient
consumption path.

The helper will:

- run `step_stem_cell` on the sender;
- require `stem-command-buffer-neighbor-delivered`;
- require the recipient's current direct input and upstream channels to be
  empty before the delivered tuple is installed;
- install the sender output tuple as the recipient upstream tuple;
- run the recipient through `step_fixed_cell` or `step_stem_cell`, depending
  on recipient role; and
- report whether the recipient consumed an init-family command message.

This ADR does not add new Universal Cell command semantics and does not execute
non-init recipient command-message inputs.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.transition_chains` is absent.
- A delivered `neighbor-b/proc-l-init` command buffer can be consumed by an
  empty fixed recipient, producing
  `recipient-init-command-message-processed`.
- A sender that does not produce neighbor delivery is rejected as a chain
  precondition failure.
- A recipient with existing input or upstream state is rejected before
  delivery is installed.
- A delivered non-init command token is reported as recipient-not-consumed
  rather than silently executed.
- Runtime single-cell behavior remains unchanged.

## Consequences

AS gains its first executable two-step command handoff without claiming a full
multi-cell simulator. This is a better integration artifact than another
single-transition bundle because it proves that already accepted delivery and
recipient-consumption surfaces can compose.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_recipient_chain` fails
  before the module is added.
- Green: the same focused test passes after adding the chain helper.
- Regression: run adjacent neighbor delivery and recipient command tests, then
  the full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/transition_chains.py`, with focused tests in
`tests/test_neighbor_delivery_recipient_chain.py`.

The focused red run failed because `autarkic_systems.transition_chains` was
absent. The green implementation adds `NeighborDeliveryRecipientChain` and
`execute_neighbor_delivery_recipient_chain`, which compose one sender
`step_stem_cell` call with one recipient `step_fixed_cell` or `step_stem_cell`
call.

The accepted path starts with the same `neighbor-b/proc-l-init` delivery used
by ADR-0076, installs the sender output tuple as recipient upstream state, and
then consumes it through the existing recipient init-family command-message
logic. The failure paths are explicit: sender-not-delivered,
recipient-not-ready, and recipient-not-consumed.

Runtime single-cell behavior remains unchanged. Delivered non-init commands
still end as recipient rejection, and the helper does not add a scheduler,
topology, non-init command execution, `standard-signal` command-token
execution, or write-buffer command-token execution.

Verification passed:

- focused red:
  `python -m unittest tests.test_neighbor_delivery_recipient_chain` failed
  before the module was added;
- focused green:
  `python -m unittest tests.test_neighbor_delivery_recipient_chain` passed 4
  tests;
- adjacent neighbor delivery/recipient command stack passed 32 tests;
- `py_compile` passed for the new module and test;
- `git diff --check` passed; and
- `python -m unittest discover` passed 454 tests.
