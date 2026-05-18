# ADR-0133: Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0011 introduced the first AS proof-certificate checker with a single
`manifest-example` clause. That rule is useful, but it keeps the predicate name
implicit: the certificate names a claim example, while the verifier looks up
the claim's predicate from `claims/transition_claims.json`.

ADR-0010 named `predicate-result` as a candidate future certificate clause. AS
now has enough stable transition predicates and certificate coverage to add the
first such clause without changing the claim manifest contract or pretending to
be a general theorem prover.

## Decision

Add a `predicate-result` certificate rule.

Each `predicate-result` step names:

- the manifest example;
- the expected boolean result; and
- the exact predicate checker expected to evaluate that example.

The verifier will reject a `predicate-result` step when its `predicate` field is
missing, malformed, or different from the claim's predicate. It will still run
the predicate checker against the manifest example and require the observed
boolean to match the manifest and certificate expectations.

The certificate manifest will use `predicate-result` for the first fixed-output
claim, leaving the remaining claims on `manifest-example` until later ADRs
promote them.

## Success Criteria

- Red tests fail before implementation because `predicate-result` is an
  unknown rule, parsed certificate steps do not carry predicate names, and the
  manifest does not yet use the new clause.
- The proof-certificate manifest includes at least one `predicate-result` step.
- A matching `predicate-result` step verifies successfully.
- Missing or mismatched `predicate` metadata rejects the owning certificate.
- Full repository tests remain green.

## Consequences

The proof-object layer becomes slightly less implicit: at least one certificate
now says which predicate was evaluated, not only which example was checked.

This remains a local proof-certificate validator over current executable
examples. It is not Proflog, LeanTAP, or an SJAS self-justification result.

## Test Plan

- Red: update proof-certificate tests to require a manifest
  `predicate-result` step and to reject missing or mismatched predicate fields.
- Green: extend `autarkic_systems.proof_certificates` to parse and verify the
  new rule, and update the first certificate in
  `claims/proof_certificates.json` to use it.
- Regression: run focused proof-certificate tests, JSON formatting,
  `py_compile`, `git diff --check`, and the full default test suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/proof_certificates.py` by adding parsed
optional predicate metadata to certificate steps and validating the new
`predicate-result` rule against the owning claim's predicate. The verifier
still evaluates the predicate against the manifest example and rejects missing
predicate names, mismatched predicate names, expectation mismatches, and
predicate result name mismatches.

The first fixed-output preservation certificate in
`claims/proof_certificates.json` now uses `predicate-result`. The transition
object-language manifest now lists both `manifest-example` and
`predicate-result` as proof-object rules, with matching validator support.

The red proof-certificate run executed 9 tests and failed because the manifest
had no `predicate-result` step and `CertificateStep` could not carry predicate
metadata. The red object-language run executed 7 tests and failed because the
certificate manifest used `predicate-result` while the language still allowed
only `manifest-example`.

Verification passed: adjacent proof-certificate and object-language tests ran
16 tests; JSON formatting, `py_compile`, and `git diff --check` passed; and
`python -m unittest discover` passed 603 tests.
