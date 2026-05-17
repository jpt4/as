# ADR-0031: Self Mailbox Init Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0030 added the first self-mailbox execution behavior:
`step_stem_cell` processes `stem-init`, `wire-r-init`, `wire-l-init`,
`proc-r-init`, and `proc-l-init` when they are present in `self_mailbox`.

The behavior is now stable enough to join the named transition-claim surface.
Keeping it only as raw transition behavior would make the proof-certificate and
object-language layers lag behind the executable substrate.

## Decision

Promote the self-mailbox init subset into the claim surface:

- add `self_mailbox_executes_init_command` in
  `autarkic_systems/transition_predicates.py`;
- add `UC-STEM-SELF-MAILBOX-INIT-COMMAND` to
  `claims/transition_claims.json`;
- add a manifest-example certificate for the new claim in
  `claims/proof_certificates.json`;
- add the predicate to the transition-claim object language;
- add tests for the predicate, manifest examples, certificate coverage, and
  object-language validation.

This claim covers init-family self-mailbox commands only. It does not certify
`standard-signal`, write-buffer commands, neighbor delivery, or full
command-buffer decoding.

## Success Criteria

- Red tests fail before implementation because
  `self_mailbox_executes_init_command` is absent.
- The predicate accepts valid init-family mailbox processing.
- The predicate rejects wrong target role/memory and uncleared self mailbox.
- Manifest examples evaluate to their declared expectations.
- Proof certificates cover the new claim.
- The object-language predicate vocabulary names the new predicate.

## Consequences

- The new execution subset now has the same claim/certificate discipline as
  prior stable transition subsets.
- Unsupported mailbox commands remain outside the claim.
- Later full command-buffer work can depend on this named slice.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_mailbox_init_claim` failed
because `self_mailbox_executes_init_command` was absent from
`autarkic_systems.transition_predicates`.

The green implementation added the predicate, the
`UC-STEM-SELF-MAILBOX-INIT-COMMAND` manifest claim, manifest-example proof
certificate coverage, and the transition-language predicate symbol. It also
refined the ADR-0028 manifest-loader test so omitted `self_mailbox` fields are
still checked for defaulting while explicit mailbox examples are allowed.

Final verification is recorded in `LOG.md`.
