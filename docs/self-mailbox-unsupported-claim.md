# Self Mailbox Unsupported Claim

Status: named boundary claim and proof-certificate surface, 2026-05-17.

ADR-0034 promotes the ADR-0030 unsupported self-mailbox command boundary into
the transition-claim surface. The claim is
`UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` in
`claims/transition_claims.json`, checked by
`self_mailbox_preserves_unsupported_command` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers the self-mailbox commands whose execution remains unresolved:

- `standard-signal`;
- `write-buf-zero`;
- `write-buf-one`.

The predicate checks that a stem cell with empty input, empty output, empty
automail, and one of those unsupported `self_mailbox` commands reaches
`self-mailbox-unsupported` and preserves the entire cell unchanged.

This claim does not define the future semantics of those commands. It records
that AS currently refuses to execute them until the source boundary is resolved.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `manifest-example`
steps for the positive and negative manifest examples.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_unsupported_claim
```

The tests cover the predicate, manifest examples, proof certificate coverage,
and object-language predicate vocabulary.
