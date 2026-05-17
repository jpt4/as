import unittest
from pathlib import Path

from autarkic_systems.object_language import (
    load_transition_claim_language,
    validate_language_manifest,
)
from autarkic_systems.universal_cell import Cell, step_fixed_cell, step_stem_cell


LANGUAGE = Path("language/transition_claim_language.json")
EMPTY = ("_", "_", "_")


class CommandChannelTokenRepresentationTests(unittest.TestCase):
    def test_output_channels_accept_command_message_tokens(self):
        cell = Cell(role="stem", memory="right", output=("wire-r-init", "_", "_"))

        self.assertEqual(cell.output, ("wire-r-init", "_", "_"))

    def test_unknown_channel_token_is_still_rejected(self):
        with self.assertRaises(ValueError):
            Cell(role="stem", memory="right", output=("neighbor-a", "_", "_"))

    def test_blocked_output_preserves_command_message_token(self):
        cell = Cell(role="stem", memory="right", output=("proc-l-init", "_", "_"))

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "blocked-output")
        self.assertEqual(result.cell, cell)

    def test_write_buffer_command_message_input_is_represented_but_not_executed(self):
        cell = Cell(role="stem", memory="right", input=("write-buf-one", "_", "_"))

        result = step_stem_cell(cell)

        self.assertEqual(result.status, "rejected-input")
        self.assertEqual(result.cell.input, EMPTY)
        self.assertEqual(result.cell.role, "stem")
        self.assertEqual(result.cell.memory, "right")

    def test_fixed_cell_distinguishes_command_token_from_si_shorthand_status(self):
        command_token = Cell(role="wire", memory="left", input=("stem-init", "_", "_"))
        shorthand = Cell(role="wire", memory="left", input=("si", "_", "_"))

        command_result = step_fixed_cell(command_token)
        shorthand_result = step_fixed_cell(shorthand)

        self.assertEqual(
            command_result.status,
            "recipient-init-command-message-processed",
        )
        self.assertEqual(command_result.cell.role, "stem")
        self.assertEqual(command_result.cell.memory, "right")
        self.assertEqual(shorthand_result.status, "stem-init")

    def test_object_language_signal_terms_include_command_messages(self):
        language = load_transition_claim_language(LANGUAGE)
        signals = language.syntax_classes["terms"]["signals"]
        results = validate_language_manifest(language)

        for token in [
            "standard-signal",
            "stem-init",
            "wire-r-init",
            "wire-l-init",
            "proc-r-init",
            "proc-l-init",
            "write-buf-zero",
            "write-buf-one",
        ]:
            with self.subTest(token=token):
                self.assertIn(token, signals)
        self.assertTrue(all(result.accepted for result in results), results)


if __name__ == "__main__":
    unittest.main()
