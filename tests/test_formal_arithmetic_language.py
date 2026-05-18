import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_arithmetic
from autarkic_systems.formal_arithmetic import (
    REQUIRED_SYNTAX_CLASSES,
    REQUIRED_WILLARD_ANCHORS,
    load_formal_arithmetic_language,
    validate_formal_arithmetic_language,
)


LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalArithmeticLanguageTests(unittest.TestCase):
    def setUp(self):
        self.language = load_formal_arithmetic_language(LANGUAGE)

    def test_checked_in_language_names_minimal_bounded_arithmetic_surface(self):
        self.assertEqual(self.language.schema_version, 1)
        self.assertEqual(self.language.language_id, "as-formal-arithmetic-v1")
        self.assertEqual(
            REQUIRED_SYNTAX_CLASSES,
            ("terms", "formulae", "sentences", "proof_objects"),
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.6-LEVEL-K-CONSISTENCY",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.4-TYPE-NS-A-S-M",
                "W2020-T4.4-T4.5-LEM-BOUNDARY",
            ),
        )
        self.assertEqual(self.language.arithmetic_profile, "Type-NS")
        self.assertIn("delta0", self.language.bounded_formula_classes)
        self.assertIn("pi1", self.language.sentence_classes)
        self.assertIn("sigma1", self.language.sentence_classes)
        term_symbols = self.language.syntax_classes["terms"]["function_symbols"]
        self.assertEqual(term_symbols["sequence_nil"]["arity"], 0)
        self.assertEqual(term_symbols["sequence_cons"]["arity"], 2)
        self.assertEqual(
            term_symbols["sequence_cons"]["totality_status"],
            "coding-symbol-not-arithmetic-theorem",
        )

    def test_checked_in_language_validates_against_willard_map(self):
        report = validate_formal_arithmetic_language(self.language, WILLARD_MAP)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(
            any(
                result.subject == "willard_anchors" and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_language_surface(self):
        report = validate_formal_arithmetic_language(self.language, WILLARD_MAP)

        payload = formal_arithmetic.formal_arithmetic_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["language_id"], "as-formal-arithmetic-v1")
        self.assertEqual(payload["arithmetic_profile"], "Type-NS")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertIn("delta0", payload["bounded_formula_classes"])
        self.assertIn("terms", payload["syntax_classes"])

    def test_text_report_exposes_language_surface(self):
        report = validate_formal_arithmetic_language(self.language, WILLARD_MAP)

        text = formal_arithmetic.format_formal_arithmetic_report(report)

        self.assertIn("Formal arithmetic language: accepted", text)
        self.assertIn("Language: as-formal-arithmetic-v1", text)
        self.assertIn("Arithmetic profile: Type-NS", text)
        self.assertIn("Bounded formula classes: delta0", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_willard_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "language.json"
            data = json.loads(LANGUAGE.read_text(encoding="utf-8"))
            data["willard_anchor_ids"].append("W2099-UNKNOWN")
            language_path.write_text(json.dumps(data), encoding="utf-8")
            language = load_formal_arithmetic_language(language_path)

            report = validate_formal_arithmetic_language(language, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("formal-arithmetic-willard-anchor", report.failed_subjects)
        self.assertTrue(
            any("unknown Willard anchor IDs: W2099-UNKNOWN" in result.detail for result in report.results)
        )

    def test_missing_syntax_class_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "language.json"
            data = json.loads(LANGUAGE.read_text(encoding="utf-8"))
            del data["syntax_classes"]["formulae"]
            language_path.write_text(json.dumps(data), encoding="utf-8")
            language = load_formal_arithmetic_language(language_path)

            report = validate_formal_arithmetic_language(language, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("formal-arithmetic-syntax", report.failed_subjects)
        self.assertTrue(
            any("missing syntax classes: formulae" in result.detail for result in report.results)
        )

    def test_missing_bounded_formula_example_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "language.json"
            data = json.loads(LANGUAGE.read_text(encoding="utf-8"))
            data["syntax_classes"]["formulae"]["bounded_formula_classes"]["delta0"]["examples"] = []
            language_path.write_text(json.dumps(data), encoding="utf-8")
            language = load_formal_arithmetic_language(language_path)

            report = validate_formal_arithmetic_language(language, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("formal-arithmetic-bounded-formula", report.failed_subjects)
        self.assertTrue(
            any("delta0 must include examples" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_language(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_arithmetic.run_formal_arithmetic_cli(
                ["--language", str(LANGUAGE), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Formal arithmetic language: accepted", output)
        self.assertIn("Language: as-formal-arithmetic-v1", output)

    def test_cli_returns_json_for_checked_in_language(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_arithmetic.run_formal_arithmetic_cli(
                [
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
        self.assertEqual(payload["language_id"], "as-formal-arithmetic-v1")

    def test_module_execution_runs_formal_arithmetic_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_arithmetic"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal arithmetic language: accepted", completed.stdout)

    def test_module_execution_runs_json_formal_arithmetic_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_arithmetic",
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
        self.assertEqual(payload["arithmetic_profile"], "Type-NS")


if __name__ == "__main__":
    unittest.main()
