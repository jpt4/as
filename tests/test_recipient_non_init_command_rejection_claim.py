import unittest
from pathlib import Path

from autarkic_systems.claim_manifest import (
    evaluate_claim_examples,
    load_transition_claims,
)
from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_claim_surface,
)
from autarkic_systems.proof_certificates import (
    load_proof_certificates,
    verify_claim_certificates,
)
from autarkic_systems.transition_predicates import (
    recipient_non_init_command_message_rejected,
)
from autarkic_systems.universal_cell import Cell, StepResult, step_fixed_cell, step_stem_cell


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED"
EMPTY = ("_", "_", "_")

class RecipientNonInitCommandMessageRejectionClaimTests(unittest.TestCase):
    def test_predicate_accepts_fixed_direct_and_upstream_standard_signal_rejection(self):
        cases = (
            Cell(role="wire", memory="right", input=("standard-signal", "_", "_")),
            Cell(role="proc", memory="left", upstream=("_", "standard-signal", "_")),
        )

        for before in cases:
            with self.subTest(before=before):
                predicate = recipient_non_init_command_message_rejected(
                    before,
                    step_fixed_cell(before),
                )

                self.assertEqual(
                    predicate.name,
                    "recipient_non_init_command_message_rejected",
                )
                self.assertTrue(predicate.holds, predicate.detail)

    def test_predicate_accepts_stem_multi_command_conflict_rejection(self):
        before = Cell(
            role="stem",
            memory="right",
            input=("wire-r-init", "write-buf-one", "_"),
            control=(0, 0, 1),
            buffer=(1,),
        )

        predicate = recipient_non_init_command_message_rejected(
            before,
            step_stem_cell(before),
        )

        self.assertTrue(predicate.holds, predicate.detail)

    def test_predicate_rejects_wrong_status_changed_role_and_uncleared_input(self):
        before = Cell(role="wire", memory="right", input=("standard-signal", "_", "_"))
        wrong_status = StepResult(
            status="routed",
            cell=Cell(role="wire", memory="right", input=EMPTY),
        )
        changed_role = StepResult(
            status="rejected-input",
            cell=Cell(role="proc", memory="right", input=EMPTY),
        )
        uncleared_input = StepResult(
            status="rejected-input",
            cell=Cell(role="wire", memory="right", input=("standard-signal", "_", "_")),
        )

        wrong_status_result = recipient_non_init_command_message_rejected(
            before,
            wrong_status,
        )
        changed_role_result = recipient_non_init_command_message_rejected(
            before,
            changed_role,
        )
        uncleared_input_result = recipient_non_init_command_message_rejected(
            before,
            uncleared_input,
        )

        self.assertFalse(wrong_status_result.holds)
        self.assertIn("rejected-input", wrong_status_result.detail)
        self.assertFalse(changed_role_result.holds)
        self.assertIn("role or memory", changed_role_result.detail)
        self.assertFalse(uncleared_input_result.holds)
        self.assertIn("input", uncleared_input_result.detail)

    def test_predicate_rejects_wrong_upstream_handling(self):
        before = Cell(
            role="proc",
            memory="left",
            upstream=("standard-signal", "_", "_"),
        )
        bad = StepResult(
            status="rejected-input",
            cell=Cell(
                role="proc",
                memory="left",
                upstream=("standard-signal", "_", "_"),
                input=EMPTY,
            ),
        )

        predicate = recipient_non_init_command_message_rejected(before, bad)

        self.assertFalse(predicate.holds)
        self.assertIn("upstream", predicate.detail)

    def test_predicate_ignores_init_commands_and_binary_standard_signals(self):
        cases = (
            Cell(role="wire", memory="right", input=("wire-r-init", "_", "_")),
            Cell(role="wire", memory="right", input=(1, 0, 1)),
        )

        for before in cases:
            with self.subTest(before=before):
                predicate = recipient_non_init_command_message_rejected(
                    before,
                    StepResult(status="rejected-input", cell=before),
                )

                self.assertTrue(predicate.holds)
                self.assertIn("precondition not active", predicate.detail)

    def test_manifest_examples_cover_recipient_non_init_rejection_claim(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        evaluations = evaluate_claim_examples([claim])

        self.assertEqual(
            claim.predicate,
            "recipient_non_init_command_message_rejected",
        )
        self.assertEqual({example.expected for example in claim.examples}, {True, False})
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

    def test_manifest_examples_do_not_name_single_write_buffer_rejections(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)
        example_names = {example.name for example in claim.examples}

        self.assertNotIn("fixed upstream write-buf-zero command rejected", example_names)
        self.assertNotIn("fixed upstream write-buf-one command rejected", example_names)

    def test_proof_certificates_cover_recipient_non_init_rejection_claim(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_proof_certificate_omits_single_write_buffer_rejections(self):
        certificates = load_proof_certificates(CERTIFICATES)
        certificate = next(
            certificate
            for certificate in certificates
            if certificate.claim_id == CLAIM_ID
        )
        covered = {
            step.example
            for step in certificate.steps
            if step.expected is True
        }

        self.assertNotIn("fixed upstream write-buf-zero command rejected", covered)
        self.assertNotIn("fixed upstream write-buf-one command rejected", covered)

    def test_object_language_names_recipient_non_init_rejection_predicate(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn("recipient_non_init_command_message_rejected", predicates)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
