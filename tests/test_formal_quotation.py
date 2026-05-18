import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_quotation
from autarkic_systems.formal_quotation import (
    REQUIRED_WILLARD_ANCHORS,
    load_quotation_examples,
    natural_to_numeral,
    numeral_to_natural,
    quote_code_tokens,
    validate_quotation_examples,
)


EXAMPLES = Path("language/formal_quotation_examples.json")
CODEBOOK = Path("language/formal_codebook.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalQuotationTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_quotation_examples(EXAMPLES)

    def test_checked_in_manifest_names_quotation_surface(self):
        self.assertEqual(self.examples.schema_version, 1)
        self.assertEqual(self.examples.quotation_set_id, "as-formal-quotation-v1")
        self.assertEqual(self.examples.codebook_path, str(CODEBOOK))
        self.assertEqual(self.examples.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(
            self.examples.quotation_kind,
            "unary-successor-token-numerals",
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
            ),
        )
        self.assertEqual(len(self.examples.examples), 3)

    def test_natural_to_numeral_round_trips(self):
        for value in (0, 3, 13):
            numeral = natural_to_numeral(value)

            self.assertEqual(numeral_to_natural(numeral), value)

    def test_quote_code_tokens_round_trips_fixed_point_instance(self):
        tokens = (41, 1, 22, 11, 1, 13, 12)

        numerals = quote_code_tokens(tokens)

        self.assertEqual(len(numerals), 7)
        self.assertEqual(numeral_to_natural(numerals[0]), 41)
        self.assertEqual(numeral_to_natural(numerals[-1]), 12)

    def test_checked_in_manifest_validates_against_codebook(self):
        report = validate_quotation_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.example_count, 3)

    def test_json_payload_exposes_quotation_surface(self):
        report = validate_quotation_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = formal_quotation.quotation_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["quotation_set_id"], "as-formal-quotation-v1")
        self.assertEqual(payload["quotation_kind"], "unary-successor-token-numerals")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["example_count"], 3)

    def test_text_report_exposes_quotation_surface(self):
        report = validate_quotation_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = formal_quotation.format_quotation_report(report)

        self.assertIn("Formal quotation: accepted", text)
        self.assertIn("Examples: as-formal-quotation-v1", text)
        self.assertIn("Example count: 3", text)
        self.assertNotIn("FAIL", text)

    def test_negative_token_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["token"] = -1
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_examples(examples_path)

            report = validate_quotation_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-example", report.failed_subjects)
        self.assertTrue(
            any("natural value must be nonnegative" in result.detail for result in report.results)
        )

    def test_expected_depth_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][1]["expected_depth"] = 12
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_examples(examples_path)

            report = validate_quotation_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-example", report.failed_subjects)
        self.assertTrue(
            any("expected depth mismatch" in result.detail for result in report.results)
        )

    def test_sequence_count_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][2]["expected_token_count"] = 6
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_examples(examples_path)

            report = validate_quotation_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-example", report.failed_subjects)
        self.assertTrue(
            any("expected token count mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_quotation.run_quotation_cli(
                [
                    "--examples",
                    str(EXAMPLES),
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
        self.assertIn("Formal quotation: accepted", output)

    def test_cli_returns_json_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_quotation.run_quotation_cli(
                [
                    "--examples",
                    str(EXAMPLES),
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
        self.assertEqual(payload["example_count"], 3)

    def test_module_execution_runs_quotation_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_quotation"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal quotation: accepted", completed.stdout)

    def test_module_execution_runs_json_quotation_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_quotation",
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
        self.assertEqual(payload["quotation_set_id"], "as-formal-quotation-v1")


if __name__ == "__main__":
    unittest.main()
