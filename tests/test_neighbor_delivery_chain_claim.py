import unittest
from pathlib import Path

from autarkic_systems.chain_claims import (
    evaluate_chain_claim_examples,
    load_transition_chain_claims,
    verify_chain_claim_certificates,
)
from autarkic_systems.proof_certificates import CertificateStep, load_proof_certificates
from autarkic_systems.transition_chain_predicates import (
    neighbor_delivery_consumed_by_recipient,
    neighbor_delivery_rejected_by_recipient,
)
from autarkic_systems.transition_chains import (
    execute_neighbor_delivery_recipient_chain,
)
from autarkic_systems.universal_cell import Cell


CLAIMS = Path("claims/transition_chain_claims.json")
CERTIFICATES = Path("claims/transition_chain_proof_certificates.json")
CONSUMED_CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED"
REJECTED_CLAIM_ID = "UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED"


class NeighborDeliveryChainClaimTests(unittest.TestCase):
    def setUp(self):
        self.claims = load_transition_chain_claims(CLAIMS)
        self.claim_by_id = {claim.claim_id: claim for claim in self.claims}
        self.claim = self.claim_by_id[CONSUMED_CLAIM_ID]
        self.rejection_claim = self.claim_by_id[REJECTED_CLAIM_ID]

    def test_chain_claim_manifest_names_neighbor_delivery_consumption(self):
        self.assertEqual(len(self.claims), 2)
        self.assertEqual(self.claim.claim_id, CONSUMED_CLAIM_ID)
        self.assertEqual(
            self.claim.predicate,
            "neighbor_delivery_consumed_by_recipient",
        )
        self.assertIn("neighbor delivery", self.claim.description)

        examples = {example.name: example for example in self.claim.examples}
        self.assertEqual(
            set(examples),
            {
                "neighbor b proc left delivery consumed by empty recipient",
                "neighbor c write buffer delivery consumed by recipient append",
                "neighbor c write buffer zero delivery consumed by recipient append",
                "self write buffer completion is not neighbor delivery",
                "recipient pending upstream blocks delivered command",
                "neighbor c standard signal delivery remains unconsumed",
            },
        )
        self.assertTrue(
            examples[
                "neighbor b proc left delivery consumed by empty recipient"
            ].expected
        )
        self.assertFalse(
            examples["neighbor c standard signal delivery remains unconsumed"].expected
        )
        self.assertTrue(
            examples[
                "neighbor c write buffer delivery consumed by recipient append"
            ].expected
        )
        self.assertTrue(
            examples[
                "neighbor c write buffer zero delivery consumed by recipient append"
            ].expected
        )

    def test_chain_claim_manifest_names_neighbor_delivery_rejection(self):
        self.assertEqual(self.rejection_claim.claim_id, REJECTED_CLAIM_ID)
        self.assertEqual(
            self.rejection_claim.predicate,
            "neighbor_delivery_rejected_by_recipient",
        )
        self.assertIn("rejects", self.rejection_claim.description)

        examples = {example.name: example for example in self.rejection_claim.examples}
        self.assertEqual(
            set(examples),
            {
                "neighbor c standard signal delivery rejected by recipient",
                "neighbor b proc left delivery is consumed not rejected",
                "self write buffer completion is not neighbor rejection",
            },
        )
        self.assertTrue(
            examples[
                "neighbor c standard signal delivery rejected by recipient"
            ].expected
        )
        self.assertFalse(
            examples[
                "neighbor b proc left delivery is consumed not rejected"
            ].expected
        )

    def test_chain_claim_examples_evaluate_against_chain_helper(self):
        evaluations = evaluate_chain_claim_examples(self.claims)

        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

        observed = {evaluation.example_name: evaluation.observed for evaluation in evaluations}
        self.assertTrue(
            observed["neighbor b proc left delivery consumed by empty recipient"]
        )
        self.assertFalse(observed["self write buffer completion is not neighbor delivery"])
        self.assertFalse(observed["recipient pending upstream blocks delivered command"])
        self.assertFalse(observed["neighbor c standard signal delivery remains unconsumed"])
        self.assertTrue(
            observed[
                "neighbor c write buffer delivery consumed by recipient append"
            ]
        )
        self.assertTrue(
            observed[
                "neighbor c write buffer zero delivery consumed by recipient append"
            ]
        )
        self.assertTrue(
            observed["neighbor c standard signal delivery rejected by recipient"]
        )
        self.assertFalse(
            observed["neighbor b proc left delivery is consumed not rejected"]
        )
        self.assertFalse(
            observed["self write buffer completion is not neighbor rejection"]
        )

    def test_chain_proof_certificates_cover_manifest_examples(self):
        certificates = load_proof_certificates(CERTIFICATES)

        results = verify_chain_claim_certificates(self.claims, certificates)

        self.assertEqual(len(results), len(self.claims))
        self.assertTrue(all(result.accepted for result in results), results)
        detail_by_claim = {result.claim_id: result.detail for result in results}
        self.assertIn(
            "verified 6 certificate steps: 6 predicate-result steps",
            detail_by_claim[CONSUMED_CLAIM_ID],
        )
        self.assertIn(
            "verified 3 certificate steps: 3 predicate-result steps",
            detail_by_claim[REJECTED_CLAIM_ID],
        )
        self.assertFalse(
            any(
                step.rule == "manifest-example"
                for certificate in certificates
                for step in certificate.steps
            )
        )

    def test_consumed_chain_certificate_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates[CONSUMED_CLAIM_ID]

        self.assertEqual(len(certificate.steps), 6)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"neighbor_delivery_consumed_by_recipient"},
        )

    def test_rejected_chain_certificate_uses_explicit_predicate_result_steps(self):
        certificates = {
            certificate.claim_id: certificate
            for certificate in load_proof_certificates(CERTIFICATES)
        }

        certificate = certificates[REJECTED_CLAIM_ID]

        self.assertEqual(len(certificate.steps), 3)
        self.assertTrue(
            all(step.rule == "predicate-result" for step in certificate.steps)
        )
        self.assertEqual(
            {step.predicate for step in certificate.steps},
            {"neighbor_delivery_rejected_by_recipient"},
        )

    def test_chain_predicate_result_steps_require_predicate_metadata(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="predicate-result",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_chain_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("lacks predicate", results[0].detail)

    def test_chain_predicate_result_steps_reject_mismatched_predicate_metadata(self):
        certificates = load_proof_certificates(CERTIFICATES)
        first = certificates[0]
        bad_step = CertificateStep(
            rule="predicate-result",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
            predicate="not_the_chain_predicate",
        )
        bad = first.with_steps((bad_step, *first.steps[1:]))

        results = verify_chain_claim_certificates(self.claims, [bad, *certificates[1:]])

        self.assertFalse(results[0].accepted)
        self.assertIn("predicate mismatch", results[0].detail)

    def test_predicate_accepts_consumed_neighbor_delivery_chain(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)
        predicate = neighbor_delivery_consumed_by_recipient(chain)

        self.assertTrue(predicate.holds, predicate.detail)
        self.assertEqual(predicate.name, "neighbor_delivery_consumed_by_recipient")

    def test_predicate_accepts_write_buffer_delivered_token(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)
        predicate = neighbor_delivery_consumed_by_recipient(chain)

        self.assertTrue(predicate.holds, predicate.detail)

    def test_rejection_predicate_accepts_delivered_standard_signal_rejection(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 0, 0),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)
        predicate = neighbor_delivery_rejected_by_recipient(chain)

        self.assertTrue(predicate.holds, predicate.detail)
        self.assertEqual(predicate.name, "neighbor_delivery_rejected_by_recipient")

    def test_rejection_predicate_rejects_consumed_init_delivery(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        chain = execute_neighbor_delivery_recipient_chain(sender, recipient)
        predicate = neighbor_delivery_rejected_by_recipient(chain)

        self.assertFalse(predicate.holds)
        self.assertIn("recipient-not-consumed", predicate.detail)


if __name__ == "__main__":
    unittest.main()
