import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import load_transition_claims
from autarkic_systems.proof_certificates import (
    CertificateStep,
    ClaimCertificate,
    load_proof_certificates,
    verify_claim_certificates,
)


MANIFEST = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")


class ProofCertificateTests(unittest.TestCase):
    def setUp(self):
        self.claims = load_transition_claims(MANIFEST)

    def test_certificate_manifest_accepts_current_claim_surface(self):
        certificates = load_proof_certificates(CERTIFICATES)

        results = verify_claim_certificates(self.claims, certificates)

        self.assertEqual(len(results), len(self.claims))
        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertTrue(
            any(
                step.rule == "predicate-result"
                for certificate in certificates
                for step in certificate.steps
            )
        )

    def test_predicate_result_rule_verifies_named_predicate(self):
        first_claim = self.claims[0]
        predicate_steps = tuple(
            CertificateStep(
                rule="predicate-result",
                example=example.name,
                expected=example.expected,
                predicate=first_claim.predicate,
            )
            for example in first_claim.examples
        )
        certificate = ClaimCertificate(
            claim_id=first_claim.claim_id,
            steps=predicate_steps,
        )

        results = verify_claim_certificates(
            self.claims,
            [certificate, *load_proof_certificates(CERTIFICATES)[1:]],
        )

        self.assertTrue(results[0].accepted, results[0].detail)
        self.assertIn("predicate-result", results[0].detail)

    def test_predicate_result_rule_requires_predicate_name(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="predicate-result",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("predicate", results[0].detail)

    def test_predicate_result_rule_rejects_mismatched_predicate_name(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="predicate-result",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
            predicate="not_the_claim_predicate",
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("predicate mismatch", results[0].detail)

    def test_missing_claim_certificate_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)

        results = verify_claim_certificates(self.claims, certificates[:-1])

        missing = results[-1]
        self.assertFalse(missing.accepted)
        self.assertIn("missing certificate", missing.detail)

    def test_unknown_claim_certificate_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        bad = ClaimCertificate(
            claim_id="UNKNOWN-CLAIM",
            steps=(CertificateStep(rule="manifest-example", example="none", expected=True),),
        )

        results = verify_claim_certificates(self.claims, [*certificates, bad])

        unknown = results[-1]
        self.assertEqual(unknown.claim_id, "UNKNOWN-CLAIM")
        self.assertFalse(unknown.accepted)
        self.assertIn("unknown claim", unknown.detail)

    def test_unknown_rule_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="not-a-rule",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("unknown certificate rule", results[0].detail)

    def test_mismatched_expected_result_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule=first.steps[0].rule,
            example=first.steps[0].example,
            expected=not first.steps[0].expected,
            predicate=first.steps[0].predicate,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("expectation mismatch", results[0].detail)

    def test_missing_example_coverage_is_rejected(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad = first.with_steps(first.steps[:1])

        results = verify_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("missing examples", results[0].detail)


if __name__ == "__main__":
    unittest.main()
