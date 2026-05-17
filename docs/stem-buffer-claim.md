# Stem Buffer Claim

Status: named transition claim for ADR-0022, 2026-05-17.

ADR-0023 promotes stem buffer accumulation from executable behavior to the AS
claim surface. The claim is `UC-STEM-BUFFER-ACCUMULATES` in
`claims/transition_claims.json`, checked by `stem_buffer_accumulates` in
`autarkic_systems/transition_predicates.py`.

## Claim Boundary

The claim covers:

- control-rail selection from one-hot stem input;
- matching one-hot input appending `1`;
- non-matching one-hot input appending `0`;
- full-buffer boundary preservation;
- malformed-input rejection and clearing.

The claim does not cover five-bit command interpretation, neighbor-target
delivery, dynamic reconfiguration, or any new schematic trace.

## Proof Surface

`claims/proof_certificates.json` covers the claim with `manifest-example`
steps. The current examples include positive control selection, positive
matching append, positive full-buffer boundary preservation, and negative wrong
bit append.

## Verification

Run:

```sh
python -m unittest tests.test_transition_predicates tests.test_claim_manifest tests.test_proof_certificates tests.test_object_language
```

The tests check the predicate directly, evaluate the claim examples against the
manifest, verify proof-certificate coverage, and ensure the object-language
predicate vocabulary names `stem_buffer_accumulates`.
