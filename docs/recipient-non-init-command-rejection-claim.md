# Recipient Non-Init Command Rejection Claim

Status: named claim and proof-certificate surface, 2026-05-17.

ADR-0054 promotes the current recipient non-init command-message rejection
boundary into the transition-claim surface. The claim is
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` in
`claims/transition_claims.json`, checked by
`recipient_non_init_command_message_rejected` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers recipient input cases that ADR-0053 keeps blocked:

- single `standard-signal` command-message input;
- single `write-buf-zero` or `write-buf-one` command-message input;
- fixed-cell upstream non-init command-message input;
- multiple simultaneous command-message input conflicts.

The predicate checks that the transition returns `rejected-input`, clears the
consumed input, preserves role and memory, creates no output, preserves
automail, self-mailbox, control, and buffer state, and handles upstream
according to the source of the rejected command.

The claim does not execute the blocked commands. It names the current
rejection boundary so later traces or semantic revisions have a stable
reference point.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `manifest-example`
steps for a fixed upstream `standard-signal` rejection, a stem multi-command
conflict rejection, and a negative changed-role example.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_rejection_claim
```

The tests cover predicate behavior, inactive preconditions, manifest examples,
proof certificate coverage, and object-language predicate vocabulary.
