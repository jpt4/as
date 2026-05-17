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
    self_mailbox_executes_init_command,
)
from autarkic_systems.universal_cell import Cell, StepResult


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-STEM-SELF-MAILBOX-INIT-COMMAND"
EMPTY = ("_", "_", "_")


class SelfMailboxInitClaimTests(unittest.TestCase):
    def test_predicate_accepts_self_mailbox_init_processing(self):
        before = Cell(role="stem", memory="right", self_mailbox="wire-l-init")
        result = StepResult(
            status="self-mailbox-processed",
            cell=Cell(role="wire", memory="left", self_mailbox="_"),
        )

        predicate = self_mailbox_executes_init_command(before, result)

        self.assertEqual(predicate.name, "self_mailbox_executes_init_command")
        self.assertTrue(predicate.holds)

    def test_predicate_rejects_wrong_target_or_uncleared_mailbox(self):
        before = Cell(role="stem", memory="right", self_mailbox="proc-r-init")
        wrong_target = StepResult(
            status="self-mailbox-processed",
            cell=Cell(role="wire", memory="right", self_mailbox="_"),
        )
        uncleared_mailbox = StepResult(
            status="self-mailbox-processed",
            cell=Cell(role="proc", memory="right", self_mailbox="proc-r-init"),
        )

        wrong_target_result = self_mailbox_executes_init_command(before, wrong_target)
        uncleared_result = self_mailbox_executes_init_command(before, uncleared_mailbox)

        self.assertFalse(wrong_target_result.holds)
        self.assertIn("expected", wrong_target_result.detail)
        self.assertFalse(uncleared_result.holds)
        self.assertIn("self mailbox", uncleared_result.detail)

    def test_manifest_examples_cover_self_mailbox_init_claim(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        evaluations = evaluate_claim_examples([claim])

        self.assertEqual(claim.predicate, "self_mailbox_executes_init_command")
        self.assertEqual({example.expected for example in claim.examples}, {True, False})
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

    def test_proof_certificates_cover_self_mailbox_init_claim(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_self_mailbox_init_predicate(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn("self_mailbox_executes_init_command", predicates)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
