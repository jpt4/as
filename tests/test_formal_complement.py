import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import formal_complement
from autarkic_systems.formal_complement import (
    REQUIRED_WILLARD_ANCHORS,
    complement_sentence,
    load_formal_complement_examples,
    validate_formal_complement_examples,
)


EXAMPLES = Path("language/formal_complement_examples.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FormalComplementTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_formal_complement_examples(EXAMPLES)

    def test_checked_in_manifest_names_complement_surface(self):
        first = self.examples.examples[0]

        self.assertEqual(self.examples.schema_version, 1)
        self.assertEqual(self.examples.complement_set_id, "as-formal-complement-v1")
        self.assertEqual(self.examples.language_path, str(LANGUAGE))
        self.assertEqual(self.examples.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.examples.complement_kind,
            "sentence-wrapper-negation-surface",
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D5.6-LEVEL-K-CONSISTENCY",
                "W2011-D5.7-SELFCONSK",
                "W2020-T4.4-T4.5-LEM-BOUNDARY",
            ),
        )
        self.assertEqual(first.source_sentence_class, "pi1")
        self.assertEqual(first.complement_sentence_class, "sigma1")
        self.assertEqual(first.status, "complement-surface-only")

    def test_complement_sentence_flips_pi1_and_sigma1_wrappers(self):
        pi1 = {
            "kind": "pi1",
            "variable": "x",
            "body": {
                "kind": "less_than",
                "left": {"kind": "variable", "name": "x"},
                "right": {"kind": "variable", "name": "n"},
            },
        }
        sigma1 = {
            "kind": "sigma1",
            "variable": "x",
            "body": {"kind": "not", "body": pi1["body"]},
        }

        self.assertEqual(complement_sentence(pi1), sigma1)
        self.assertEqual(
            complement_sentence(sigma1),
            {
                "kind": "pi1",
                "variable": "x",
                "body": {"kind": "not", "body": sigma1["body"]},
            },
        )
        with self.assertRaises(ValueError):
            complement_sentence(pi1["body"])

    def test_checked_in_manifest_validates_complement_examples(self):
        report = validate_formal_complement_examples(
            self.examples,
            LANGUAGE,
            CODEBOOK,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.example_count, 2)

    def test_json_payload_exposes_complement_examples(self):
        report = validate_formal_complement_examples(
            self.examples,
            LANGUAGE,
            CODEBOOK,
            WILLARD_MAP,
        )

        payload = formal_complement.formal_complement_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["complement_set_id"], "as-formal-complement-v1")
        self.assertEqual(payload["example_count"], 2)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["examples"][0]["source_sentence_class"], "pi1")
        self.assertEqual(payload["examples"][0]["complement_sentence_class"], "sigma1")

    def test_text_report_exposes_complement_examples(self):
        report = validate_formal_complement_examples(
            self.examples,
            LANGUAGE,
            CODEBOOK,
            WILLARD_MAP,
        )

        text = formal_complement.format_formal_complement_report(report)

        self.assertIn("Formal complements: accepted", text)
        self.assertIn("pi1-less-than-to-sigma1-not-less-than", text)
        self.assertIn("pi1 -> sigma1", text)
        self.assertNotIn("FAIL", text)

    def test_stale_expected_complement_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "complements.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_complement_code"] = [42, 1]
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_formal_complement_examples(path)

            report = validate_formal_complement_examples(
                examples,
                LANGUAGE,
                CODEBOOK,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-complement-example", report.failed_subjects)
        self.assertTrue(
            any("expected complement code mismatch" in result.detail for result in report.results)
        )

    def test_unknown_sentence_class_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "complements.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["source_sentence_class"] = "delta0"
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_formal_complement_examples(path)

            report = validate_formal_complement_examples(
                examples,
                LANGUAGE,
                CODEBOOK,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-complement-class", report.failed_subjects)
        self.assertTrue(any("unknown source sentence class" in result.detail for result in report.results))

    def test_overclaiming_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "complements.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["status"] = "complement-theorem-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_formal_complement_examples(path)

            report = validate_formal_complement_examples(
                examples,
                LANGUAGE,
                CODEBOOK,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("formal-complement-status", report.failed_subjects)
        self.assertTrue(any("proved complement theorems are not supported" in result.detail for result in report.results))

    def test_cli_returns_zero_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_complement.run_formal_complement_cli(
                [
                    "--examples",
                    str(EXAMPLES),
                    "--language",
                    str(LANGUAGE),
                    "--codebook",
                    str(CODEBOOK),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Formal complements: accepted", output)

    def test_cli_returns_json_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = formal_complement.run_formal_complement_cli(
                [
                    "--examples",
                    str(EXAMPLES),
                    "--language",
                    str(LANGUAGE),
                    "--codebook",
                    str(CODEBOOK),
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

    def test_module_execution_runs_complement_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.formal_complement"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Formal complements: accepted", completed.stdout)

    def test_module_execution_runs_json_complement_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.formal_complement",
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
        self.assertEqual(payload["complement_set_id"], "as-formal-complement-v1")


if __name__ == "__main__":
    unittest.main()
