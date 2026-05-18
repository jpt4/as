import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_code
from autarkic_systems.formal_code import (
    REQUIRED_CODEBOOK_SECTIONS,
    REQUIRED_WILLARD_ANCHORS,
    decode_code,
    encode_node,
    load_formal_codebook,
    validate_formal_codebook,
)


CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalCodeEncodingTests(unittest.TestCase):
    def setUp(self):
        self.codebook = load_formal_codebook(CODEBOOK)

    def test_checked_in_codebook_names_first_proof_code_surface(self):
        self.assertEqual(self.codebook.schema_version, 1)
        self.assertEqual(self.codebook.codebook_id, "as-formal-codebook-v1")
        self.assertEqual(self.codebook.language_id, "as-formal-arithmetic-v1")
        self.assertEqual(self.codebook.encoding_kind, "tagged-prefix-natural-sequence")
        self.assertEqual(
            REQUIRED_CODEBOOK_SECTIONS,
            (
                "variable_codes",
                "term_tags",
                "formula_tags",
                "sentence_tags",
                "proof_line_tags",
                "proof_rule_codes",
                "examples",
            ),
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.4-TYPE-NS-A-S-M",
            ),
        )
        self.assertIn("successor", self.codebook.term_tags)
        self.assertIn("sequence_nil", self.codebook.term_tags)
        self.assertIn("sequence_cons", self.codebook.term_tags)
        self.assertIn("substitution_code", self.codebook.term_tags)
        self.assertIn("bounded_exists", self.codebook.formula_tags)
        self.assertIn("pi1", self.codebook.sentence_tags)
        self.assertIn("proof_line", self.codebook.proof_line_tags)

    def test_checked_in_codebook_validates_against_language_and_willard_map(self):
        report = validate_formal_codebook(self.codebook, LANGUAGE, WILLARD_MAP)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(
            any(
                result.subject == "examples" and result.accepted
                for result in report.results
            )
        )

    def test_encoder_and_decoder_round_trip_a_term(self):
        node = {"kind": "successor", "term": {"kind": "variable", "name": "x"}}

        code = encode_node(node, self.codebook)
        decoded = decode_code(code, self.codebook)

        self.assertEqual(code, (13, 11, 1))
        self.assertEqual(decoded, node)

    def test_encoder_and_decoder_round_trip_a_sequence_term(self):
        node = {
            "kind": "sequence_cons",
            "head": {"kind": "successor", "term": {"kind": "zero"}},
            "tail": {
                "kind": "sequence_cons",
                "head": {"kind": "zero"},
                "tail": {"kind": "sequence_nil"},
            },
        }

        code = encode_node(node, self.codebook)
        decoded = decode_code(code, self.codebook)

        self.assertEqual(code, (17, 13, 12, 17, 12, 16))
        self.assertEqual(decoded, node)

    def test_encoder_and_decoder_round_trip_a_substitution_code_term(self):
        node = {
            "kind": "substitution_code",
            "left": {"kind": "variable", "name": "n"},
            "right": {"kind": "variable", "name": "n"},
        }

        code = encode_node(node, self.codebook)
        decoded = decode_code(code, self.codebook)

        self.assertEqual(code, (18, 11, 4, 11, 4))
        self.assertEqual(decoded, node)

    def test_encoder_and_decoder_round_trip_a_bounded_formula(self):
        node = {
            "kind": "bounded_exists",
            "variable": "y",
            "bound": {"kind": "variable", "name": "n"},
            "body": {
                "kind": "equals",
                "left": {"kind": "variable", "name": "y"},
                "right": {"kind": "variable", "name": "x"},
            },
        }

        code = encode_node(node, self.codebook)
        decoded = decode_code(code, self.codebook)

        self.assertEqual(code, (30, 2, 11, 4, 21, 11, 2, 11, 1))
        self.assertEqual(decoded, node)

    def test_encoder_and_decoder_round_trip_a_proof_line_shell(self):
        formula = {
            "kind": "pi1",
            "variable": "x",
            "body": {
                "kind": "less_than",
                "left": {"kind": "variable", "name": "x"},
                "right": {"kind": "variable", "name": "n"},
            },
        }
        node = {
            "kind": "proof_line",
            "line": 1,
            "rule": "assumption",
            "formula": formula,
            "premises": [],
        }

        code = encode_node(node, self.codebook)
        decoded = decode_code(code, self.codebook)

        self.assertEqual(code, (61, 1, 1, 41, 1, 22, 11, 1, 11, 4, 0))
        self.assertEqual(decoded, node)

    def test_json_payload_exposes_codebook_surface(self):
        report = validate_formal_codebook(self.codebook, LANGUAGE, WILLARD_MAP)

        payload = formal_code.formal_code_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["codebook_id"], "as-formal-codebook-v1")
        self.assertEqual(payload["language_id"], "as-formal-arithmetic-v1")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["example_count"], 6)
        self.assertIn("proof_line", payload["proof_line_tags"])

    def test_text_report_exposes_codebook_surface(self):
        report = validate_formal_codebook(self.codebook, LANGUAGE, WILLARD_MAP)

        text = formal_code.format_formal_code_report(report)

        self.assertIn("Formal codebook: accepted", text)
        self.assertIn("Codebook: as-formal-codebook-v1", text)
        self.assertIn("Language: as-formal-arithmetic-v1", text)
        self.assertIn("Examples: 6", text)
        self.assertNotIn("FAIL", text)

    def test_duplicate_tag_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            codebook_path = Path(tmp) / "codebook.json"
            data = json.loads(CODEBOOK.read_text(encoding="utf-8"))
            data["formula_tags"]["equals"] = data["term_tags"]["variable"]
            codebook_path.write_text(json.dumps(data), encoding="utf-8")
            codebook = load_formal_codebook(codebook_path)

            report = validate_formal_codebook(codebook, LANGUAGE, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("formal-codebook-tag", report.failed_subjects)
        self.assertTrue(
            any("duplicate code values" in result.detail for result in report.results)
        )

    def test_unknown_variable_in_example_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            codebook_path = Path(tmp) / "codebook.json"
            data = json.loads(CODEBOOK.read_text(encoding="utf-8"))
            data["examples"][0]["node"]["term"]["name"] = "q"
            codebook_path.write_text(json.dumps(data), encoding="utf-8")
            codebook = load_formal_codebook(codebook_path)

            report = validate_formal_codebook(codebook, LANGUAGE, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("formal-codebook-example", report.failed_subjects)
        self.assertTrue(
            any("unknown variable: q" in result.detail for result in report.results)
        )

    def test_mismatched_expected_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            codebook_path = Path(tmp) / "codebook.json"
            data = json.loads(CODEBOOK.read_text(encoding="utf-8"))
            data["examples"][0]["expected_code"] = [99]
            codebook_path.write_text(json.dumps(data), encoding="utf-8")
            codebook = load_formal_codebook(codebook_path)

            report = validate_formal_codebook(codebook, LANGUAGE, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("formal-codebook-example", report.failed_subjects)
        self.assertTrue(
            any("expected code mismatch" in result.detail for result in report.results)
        )

    def test_decode_rejects_trailing_tokens(self):
        with self.assertRaisesRegex(ValueError, "trailing code tokens"):
            decode_code((11, 1, 99), self.codebook)

    def test_cli_returns_zero_for_checked_in_codebook(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_code.run_formal_code_cli(
                [
                    "--codebook",
                    str(CODEBOOK),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Formal codebook: accepted", output)
        self.assertIn("Codebook: as-formal-codebook-v1", output)

    def test_cli_returns_json_for_checked_in_codebook(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_code.run_formal_code_cli(
                [
                    "--codebook",
                    str(CODEBOOK),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["codebook_id"], "as-formal-codebook-v1")

    def test_module_execution_runs_formal_code_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_code"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal codebook: accepted", completed.stdout)

    def test_module_execution_runs_json_formal_code_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_code",
                "--format",
                "json",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["example_count"], 6)


if __name__ == "__main__":
    unittest.main()
