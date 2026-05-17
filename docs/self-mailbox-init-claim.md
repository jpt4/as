# Self Mailbox Init Claim

Status: named claim and proof-certificate surface, 2026-05-17.

ADR-0031 promotes the ADR-0030 self-mailbox init-command execution subset into
the transition-claim surface. The claim is
`UC-STEM-SELF-MAILBOX-INIT-COMMAND` in `claims/transition_claims.json`, checked
by `self_mailbox_executes_init_command` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers only supported init-family self-mailbox commands:

- `stem-init`;
- `wire-r-init`;
- `wire-l-init`;
- `proc-r-init`;
- `proc-l-init`.

The predicate checks that a stem cell with empty input, empty output, empty
automail, and a supported `self_mailbox` command reaches
`self-mailbox-processed`, reconfigures to the expected role and memory, clears
the self mailbox, clears input/output/automail, and clears control/buffer
state.

The claim does not cover `standard-signal`, `write-buf-zero`,
`write-buf-one`, neighbor delivery, or full command-buffer decoding.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `manifest-example`
steps for the positive and negative manifest examples.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_init_claim
```

The tests cover the predicate, manifest examples, proof certificate coverage,
and object-language predicate vocabulary.
