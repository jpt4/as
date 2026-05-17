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
    stem_command_buffer_delivers_neighbor_command,
)
from autarkic_systems.universal_cell import Cell, StepResult


CLAIMS = Path("claims/transition_claims.json")
CERTIFICATES = Path("claims/proof_certificates.json")
LANGUAGE = Path("language/transition_claim_language.json")
CLAIM_ID = "UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED"
EMPTY = ("_", "_", "_")


class NeighborCommandBufferDeliveryClaimTests(unittest.TestCase):
    def test_predicate_accepts_each_neighbor_delivery_channel(self):
        cases = (
            ((0, 0, 1), (0, 1, 0, 0), ("stem-init", "_", "_")),
            ((1, 0, 0), (1, 0, 1, 0), ("_", "proc-l-init", "_")),
            ((0, 1, 0), (1, 1, 1, 1), ("_", "_", "write-buf-one")),
        )

        for control, buffer, output in cases:
            with self.subTest(buffer=buffer, output=output):
                before = Cell(
                    role="stem",
                    memory="right",
                    upstream=(1, "_", "_"),
                    input=control,
                    control=control,
                    buffer=buffer,
                )
                result = StepResult(
                    status="stem-command-buffer-neighbor-delivered",
                    cell=Cell(
                        role="stem",
                        memory="right",
                        upstream=(1, "_", "_"),
                        input=EMPTY,
                        output=output,
                        automail="_",
                        self_mailbox="_",
                        control=(),
                        buffer=(),
                    ),
                )

                predicate = stem_command_buffer_delivers_neighbor_command(
                    before,
                    result,
                )

                self.assertEqual(
                    predicate.name,
                    "stem_command_buffer_delivers_neighbor_command",
                )
                self.assertTrue(predicate.holds, predicate.detail)

    def test_predicate_rejects_wrong_channel_or_uncleared_state(self):
        before = Cell(
            role="stem",
            memory="right",
            input=(0, 0, 1),
            control=(0, 0, 1),
            buffer=(0, 1, 0, 0),
        )
        wrong_channel = StepResult(
            status="stem-command-buffer-neighbor-delivered",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=("_", "stem-init", "_"),
                automail="_",
                self_mailbox="_",
                control=(),
                buffer=(),
            ),
        )
        uncleared = StepResult(
            status="stem-command-buffer-neighbor-delivered",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=("stem-init", "_", "_"),
                automail="_",
                self_mailbox="_",
                control=(0, 0, 1),
                buffer=(0, 1, 0, 0, 1),
            ),
        )
        wrong_status = StepResult(
            status="stem-buffer-appended",
            cell=Cell(
                role="stem",
                memory="right",
                input=EMPTY,
                output=("stem-init", "_", "_"),
                automail="_",
                self_mailbox="_",
                control=(),
                buffer=(),
            ),
        )

        wrong_channel_result = stem_command_buffer_delivers_neighbor_command(
            before,
            wrong_channel,
        )
        uncleared_result = stem_command_buffer_delivers_neighbor_command(
            before,
            uncleared,
        )
        wrong_status_result = stem_command_buffer_delivers_neighbor_command(
            before,
            wrong_status,
        )

        self.assertFalse(wrong_channel_result.holds)
        self.assertIn("output", wrong_channel_result.detail)
        self.assertFalse(uncleared_result.holds)
        self.assertIn("control or buffer", uncleared_result.detail)
        self.assertFalse(wrong_status_result.holds)
        self.assertIn("stem-command-buffer-neighbor-delivered", wrong_status_result.detail)

    def test_predicate_ignores_self_target_completed_buffer(self):
        before = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(0, 0, 1, 0),
        )
        result = StepResult(
            status="stem-command-buffer-self-processed",
            cell=Cell(role="proc", memory="left"),
        )

        predicate = stem_command_buffer_delivers_neighbor_command(before, result)

        self.assertTrue(predicate.holds)
        self.assertIn("precondition not active", predicate.detail)

    def test_manifest_examples_cover_neighbor_delivery_claim(self):
        claims = load_transition_claims(CLAIMS)
        claim = next(claim for claim in claims if claim.claim_id == CLAIM_ID)

        evaluations = evaluate_claim_examples([claim])

        self.assertEqual(
            claim.predicate,
            "stem_command_buffer_delivers_neighbor_command",
        )
        self.assertEqual({example.expected for example in claim.examples}, {True, False})
        self.assertTrue(evaluations)
        self.assertTrue(all(evaluation.matched for evaluation in evaluations), evaluations)

    def test_proof_certificates_cover_neighbor_delivery_claim(self):
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)

        certificate_ids = {certificate.claim_id for certificate in certificates}
        results = verify_claim_certificates(claims, certificates)

        self.assertIn(CLAIM_ID, certificate_ids)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_object_language_names_neighbor_delivery_predicate(self):
        language = load_transition_claim_language(LANGUAGE)
        claims = load_transition_claims(CLAIMS)
        certificates = load_proof_certificates(CERTIFICATES)
        predicates = language.syntax_classes["formulae"]["predicate_symbols"]

        results = validate_claim_surface(language, claims, certificates)

        self.assertIn("stem_command_buffer_delivers_neighbor_command", predicates)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
