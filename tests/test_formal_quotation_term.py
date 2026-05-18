import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_quotation_term
from autarkic_systems.formal_code import decode_code, encode_node, load_formal_codebook
from autarkic_systems.formal_quotation import numeral_to_natural
from autarkic_systems.formal_quotation_term import (
    REQUIRED_WILLARD_ANCHORS,
    load_quotation_term_examples,
    quote_tokens_as_term,
    validate_quotation_term_examples,
)


EXAMPLES = Path("language/formal_quotation_term_examples.json")
SEQUENCE = Path("language/formal_quotation_sequence_examples.json")
CODEBOOK = Path("language/formal_codebook.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalQuotationTermTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_quotation_term_examples(EXAMPLES)

    def test_checked_in_manifest_names_quotation_term_surface(self):
        self.assertEqual(self.examples.schema_version, 1)
        self.assertEqual(self.examples.term_set_id, "as-formal-quotation-term-v1")
        self.assertEqual(self.examples.codebook_path, str(CODEBOOK))
        self.assertEqual(self.examples.quotation_sequence_examples_path, str(SEQUENCE))
        self.assertEqual(self.examples.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(self.examples.term_kind, "nested-sequence-cons-term")
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
            ),
        )
        self.assertEqual(len(self.examples.examples), 2)

    def test_quote_tokens_as_term_wraps_sequence_cons_terms(self):
        term = quote_tokens_as_term((1, 0))

        self.assertEqual(term["kind"], "sequence_cons")
        self.assertEqual(numeral_to_natural(term["head"]), 1)
        self.assertEqual(term["tail"]["kind"], "sequence_cons")
        self.assertEqual(numeral_to_natural(term["tail"]["head"]), 0)
        self.assertEqual(term["tail"]["tail"], {"kind": "sequence_nil"})

    def test_quote_tokens_as_term_round_trips_through_codebook(self):
        codebook = load_formal_codebook(CODEBOOK)
        term = quote_tokens_as_term((1, 0))

        code = encode_node(term, codebook)
        decoded = decode_code(code, codebook)

        self.assertEqual(code, (17, 13, 12, 17, 12, 16))
        self.assertEqual(decoded, term)

    def test_checked_in_manifest_validates_dependencies(self):
        report = validate_quotation_term_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.example_count, 2)

    def test_json_payload_exposes_quotation_term_surface(self):
        report = validate_quotation_term_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = formal_quotation_term.quotation_term_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["term_set_id"], "as-formal-quotation-term-v1")
        self.assertEqual(payload["term_kind"], "nested-sequence-cons-term")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["example_count"], 2)

    def test_text_report_exposes_quotation_term_surface(self):
        report = validate_quotation_term_examples(
            self.examples,
            CODEBOOK,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = formal_quotation_term.format_quotation_term_report(report)

        self.assertIn("Formal quotation term: accepted", text)
        self.assertIn("Examples: as-formal-quotation-term-v1", text)
        self.assertIn("Example count: 2", text)
        self.assertNotIn("FAIL", text)

    def test_empty_token_sequence_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["tokens"] = []
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_term_examples(examples_path)

            report = validate_quotation_term_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-term-example", report.failed_subjects)
        self.assertTrue(
            any("code tokens must be a non-empty sequence" in result.detail for result in report.results)
        )

    def test_endpoint_depth_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_last_token_depth"] = 99
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_term_examples(examples_path)

            report = validate_quotation_term_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-term-example", report.failed_subjects)
        self.assertTrue(
            any("expected last token depth mismatch" in result.detail for result in report.results)
        )

    def test_term_kind_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            examples_path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["term_kind"] = "raw-token-list-term"
            examples_path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_quotation_term_examples(examples_path)

            report = validate_quotation_term_examples(
                examples,
                CODEBOOK,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-quotation-term-manifest", report.failed_subjects)
        self.assertTrue(
            any("unknown term kind: raw-token-list-term" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_quotation_term.run_quotation_term_cli(
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
        self.assertIn("Formal quotation term: accepted", output)

    def test_cli_returns_json_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_quotation_term.run_quotation_term_cli(
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
        self.assertEqual(payload["example_count"], 2)

    def test_module_execution_runs_term_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_quotation_term"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal quotation term: accepted", completed.stdout)

    def test_module_execution_runs_json_term_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_quotation_term",
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
        self.assertEqual(payload["term_set_id"], "as-formal-quotation-term-v1")


if __name__ == "__main__":
    unittest.main()
