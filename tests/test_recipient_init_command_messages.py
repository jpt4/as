import unittest
from pathlib import Path

from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_language_manifest,
)
from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


LANGUAGE = Path("language/transition_claim_language.json")
EMPTY = ("_", "_", "_")
STATUS = "recipient-init-command-message-processed"


class RecipientInitCommandMessageConsumptionTests(unittest.TestCase):
    def test_fixed_cell_consumes_init_command_message_from_input(self):
        cell = Cell(role="wire", memory="right", input=("_", "proc-l-init", "_"))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "proc")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_fixed_cell_consumes_delivered_upstream_init_command_message(self):
        cell = Cell(role="proc", memory="left", upstream=("wire-r-init", "_", "_"))

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.upstream, EMPTY)
        self.assertEqual(result.cell.input, EMPTY)

    def test_stem_cell_consumes_init_command_message_and_clears_command_state(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=("_", "wire-l-init", "_"),
            self_mailbox="proc-r-init",
            control=(0, 1, 0),
            buffer=(1, 0),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "wire")
        self.assertEqual(result.cell.memory, "left")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.output, EMPTY)
        self.assertEqual(result.cell.automail, "_")
        self.assertEqual(result.cell.self_mailbox, "_")
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_stem_init_command_message_resets_recipient_state(self):
        cell = Cell(
            role="proc",
            memory="left",
            input=("stem-init", "_", "_"),
            control=(1, 0, 0),
            buffer=(1, 1, 0),
        )

        result = step_fixed_cell(cell)

        self.assertEqual(result.status, STATUS)
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, ())
        self.assertEqual(result.cell.buffer, ())

    def test_unresolved_command_message_inputs_remain_rejected(self):
        cases = (
            (
                "fixed standard-signal command message",
                step_fixed_cell,
                Cell(role="wire", memory="right", input=("standard-signal", "_", "_")),
            ),
        )

        for name, step, cell in cases:
            with self.subTest(name=name):
                result = step(cell)

                self.assertEqual(result.status, "rejected-input")
                self.assertEqual(result.cell.input, EMPTY)
                self.assertEqual(result.cell.role, cell.role)
                self.assertEqual(result.cell.memory, cell.memory)

    def test_multiple_command_message_inputs_remain_conflict_boundary(self):
        cell = Cell(
            role="stem",
            memory="right",
            input=("wire-r-init", "proc-l-init", "_"),
            control=(0, 0, 1),
            buffer=(1,),
        )

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.control, (0, 0, 1))
        self.assertEqual(result.cell.buffer, (1,))

    def test_transition_language_names_recipient_init_status(self):
        language = load_transition_claim_language(LANGUAGE)
        statuses = language.syntax_classes["terms"]["statuses"]
        results = validate_language_manifest(language)

        self.assertIn(STATUS, statuses)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
