# ADR-0034: Self Mailbox Unsupported Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0030 executes only the source-stable self-mailbox init-family commands.
It deliberately leaves `standard-signal`, `write-buf-zero`, and
`write-buf-one` unsupported because the PRC source boundary for those commands
is not yet stable enough for AS execution.

That unsupported boundary is currently executable behavior, but it is not yet
part of the named claim/proof-certificate surface. Leaving it unnamed weakens
the safety story: later command-execution work should be able to depend on a
checkable claim that unresolved self-mailbox commands are preserved rather than
silently executed.

## Decision

Promote the unsupported self-mailbox command boundary into the claim surface:

- add `self_mailbox_preserves_unsupported_command` in
  `autarkic_systems/transition_predicates.py`;
- add `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` to
  `claims/transition_claims.json`;
- add manifest-example certificate coverage;
- add the predicate to the transition-claim object language;
- add tests for predicate behavior, manifest evaluation, certificate coverage,
  and object-language validation.

This claim covers `standard-signal`, `write-buf-zero`, and `write-buf-one` when
they are present in `self_mailbox` on an otherwise processable stem cell. It
does not define their eventual semantics.

## Success Criteria

- Red tests fail before implementation because
  `self_mailbox_preserves_unsupported_command` is absent.
- The predicate accepts `self-mailbox-unsupported` results that preserve the
  entire cell.
- The predicate rejects unsupported-command results that clear or mutate the
  mailbox/cell.
- Manifest examples evaluate to their declared expectations.
- Proof certificates cover the new claim.
- The object-language predicate vocabulary names the new predicate.

## Consequences

- The unresolved command boundary becomes checkable instead of just prose.
- Later write-buffer or `standard-signal` work must intentionally replace or
  refine this boundary claim.
- Full command-buffer execution, neighbor delivery, and command semantics
  remain out of scope.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_self_mailbox_unsupported_claim` failed because
`self_mailbox_preserves_unsupported_command` was absent from
`autarkic_systems.transition_predicates`.

The green implementation added the predicate, the
`UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` manifest claim,
manifest-example proof certificate coverage, and the transition-language
predicate symbol.

Final verification is recorded in `LOG.md`.
