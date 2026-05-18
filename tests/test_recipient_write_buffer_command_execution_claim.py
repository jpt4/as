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
    recipient_write_buffer_command_message_appends_literal,
)
from autarkic_systems.universal_cell import Cell, StepResult


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-RECIPIENT-WRITE-BUFFER-COMMAND-MESSAGE-APPENDED"
STATUS = "recipient-write-buffer-command-message-appended"
EMPTY = ("_", "_", "_")


class RecipientWriteBufferCommandExecutionClaimTests(unittest.TestCase):
    def test_predicate_accepts_upstream_write_buffer_append(self):
        before = Cell(
            role="wire",
            memory="right",
            upstream=("write-buf-zero", "_", "_"),
            buffer=(1,),
        )
        result = StepResult(
            status=STATUS,
            cell=Cell(
                role="wire",
                memory="right",
                upstream=EMPTY,
                input=EMPTY,
                output=EMPTY,
                automail="_",
                self_mailbox="_",
                control=(),
                buffer=(1, 0),
            ),
        )

        predicate = recipient_write_buffer_command_message_appends_literal(
            before,
            result,
        )

        self.assertEqual(
            predicate.name,
            "recipient_write_buffer_command_message_appends_literal",
        )
        self.assertTrue(predicate.holds, predicate.detail)

    def test_predicate_rejects_wrong_literal_bit(self):
        before = Cell(role="proc", memory="left", input=("write-buf-one", "_", "_"))
        result = StepResult(
            status=STATUS,
            cell=Cell(role="proc", memory="left", input=EMPTY, buffer=(0,)),
        )

        predicate = recipient_write_buffer_command_message_appends_literal(
            before,
            result,
        )

        self.assertFalse(predicate.holds)
        self.assertIn("expected buffer", predicate.detail)

    def test_manifest_and_proof_cover_recipient_write_buffer_execution(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        claims_by_id = {claim.claim_id: claim for claim in claims}

        self.assertIn(CLAIM_ID, claims_by_id)
        claim = claims_by_id[CLAIM_ID]
        self.assertEqual(
            claim.predicate,
            "recipient_write_buffer_command_message_appends_literal",
        )
        self.assertEqual({example.expected for example in claim.examples}, {True, False})

        evaluations = evaluate_claim_examples([claim])
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_recipient_write_buffer_surface(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]
        statuses = language.syntax_classes["terms"]["statuses"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn(
            "recipient_write_buffer_command_message_appends_literal",
            predicates,
        )
        self.assertIn(STATUS, statuses)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
