# ADR-0045: Neighbor Command Buffer Delivery Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0044 implements the first neighbor-target command-buffer delivery behavior:
completed `neighbor-a`, `neighbor-b`, and `neighbor-c` buffers place the decoded
command token on output channels 0, 1, and 2 respectively. That behavior is now
covered by direct transition tests, but it is not yet part of the named
transition-claim and proof-certificate surface.

The next useful step is to make the new delivery semantics durable before
adding schematic traces or recipient-side consumption. The claim must remain
delivery-only: recipient cells still reject command-message inputs.

## Decision

Promote neighbor command-buffer delivery into the claim surface:

- add `stem_command_buffer_delivers_neighbor_command` in
  `autarkic_systems/transition_predicates.py`;
- add `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` to
  `claims/transition_claims.json`;
- add manifest-example proof certificate coverage;
- add the predicate to the transition-claim object language;
- add tests for all three neighbor targets, wrong-channel rejection, uncleared
  transient-state rejection, manifest examples, certificate coverage, and
  object-language validation.

The claim covers delivery of decoded command tokens to output channels only. It
does not claim that any neighbor consumes or executes the delivered token.

## Success Criteria

- Red tests fail before implementation because
  `stem_command_buffer_delivers_neighbor_command` is absent.
- The predicate accepts completed neighbor A, B, and C command buffers when the
  decoded command token appears on the corresponding output channel.
- The predicate rejects wrong output channels, wrong statuses, or uncleared
  command state.
- The predicate ignores self-target command buffers as outside its
  precondition.
- Manifest examples evaluate to their declared expectations.
- Proof certificates cover the new claim.
- The object-language predicate vocabulary names the new predicate.

## Consequences

- ADR-0044 delivery behavior becomes part of the checkable transition-claim
  surface.
- The next schematic slice can depend on a named neighbor-delivery claim rather
  than direct transition tests alone.
- Recipient-side command-message consumption remains out of scope.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_neighbor_command_buffer_delivery_claim` failed
because `stem_command_buffer_delivers_neighbor_command` was absent from
`autarkic_systems.transition_predicates`.

The green implementation added the predicate, the
`UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` manifest claim,
manifest-example proof certificate coverage, and the transition-language
predicate symbol. The predicate accepts neighbor A/B/C delivery, rejects wrong
channels and uncleared command state, and treats self-target completed buffers
as outside its precondition.

Final verification is recorded in `LOG.md`.
