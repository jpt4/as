import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_obstruction
from autarkic_systems.fixed_point_obstruction import (
    REQUIRED_WILLARD_ANCHORS,
    load_fixed_point_obstructions,
    quote_term_code_length_formula,
    validate_fixed_point_obstructions,
)


OBSTRUCTIONS = Path("claims/fixed_point_obstructions.json")
CANDIDATES = Path("claims/fixed_point_equation_candidates.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointObstructionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_fixed_point_obstructions(OBSTRUCTIONS)

    def test_checked_in_manifest_names_naive_length_obstruction(self):
        obstruction = self.manifest.obstructions[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.obstruction_set_id,
            "as-fixed-point-obstruction-v1",
        )
        self.assertEqual(
            self.manifest.fixed_point_equation_candidates_path,
            str(CANDIDATES),
        )
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.manifest.obstruction_kind,
            "naive-quotation-length-growth",
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
            ),
        )
        self.assertEqual(
            obstruction.candidate_id,
            "AS-FIXED-POINT-SELFCONS1-NAIVE-QUOTE-CANDIDATE",
        )
        self.assertEqual(obstruction.status, "obstruction-observed")
        self.assertEqual(obstruction.expected_template_variable_occurrences, 1)
        self.assertEqual(obstruction.expected_context_code_length, 5)
        self.assertEqual(obstruction.expected_observed_input_length, 7)
        self.assertEqual(obstruction.expected_observed_input_token_sum, 101)
        self.assertEqual(obstruction.expected_observed_candidate_length, 121)

    def test_quote_term_code_length_formula_matches_current_tokens(self):
        tokens = (41, 1, 22, 11, 1, 13, 12)

        self.assertEqual(quote_term_code_length_formula(tokens), 116)
        self.assertEqual(quote_term_code_length_formula(()), 1)

    def test_checked_in_manifest_validates_length_obstruction(self):
        report = validate_fixed_point_obstructions(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.obstruction_count, 1)
        self.assertTrue(report.observations[0].impossible_by_length)
        self.assertEqual(report.observations[0].minimum_growth_delta, 6)

    def test_json_payload_exposes_length_obstruction(self):
        report = validate_fixed_point_obstructions(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = fixed_point_obstruction.fixed_point_obstruction_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["obstruction_set_id"],
            "as-fixed-point-obstruction-v1",
        )
        self.assertEqual(payload["obstruction_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["obstructions"][0]["impossible_by_length"])
        self.assertEqual(payload["obstructions"][0]["context_code_length"], 5)
        self.assertEqual(payload["obstructions"][0]["minimum_growth_delta"], 6)

    def test_text_report_exposes_length_obstruction(self):
        report = validate_fixed_point_obstructions(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = fixed_point_obstruction.format_fixed_point_obstruction_report(report)

        self.assertIn("Fixed-point obstructions: accepted", text)
        self.assertIn("naive candidate length strictly grows", text)
        self.assertIn("Minimum growth delta: 6", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_candidate_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obstructions.json"
            data = json.loads(OBSTRUCTIONS.read_text(encoding="utf-8"))
            data["obstructions"][0]["candidate_id"] = "UNKNOWN-CANDIDATE"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_obstructions(path)

            report = validate_fixed_point_obstructions(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-obstruction-candidate", report.failed_subjects)
        self.assertTrue(
            any("unknown fixed-point equation candidate" in result.detail for result in report.results)
        )

    def test_stale_context_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obstructions.json"
            data = json.loads(OBSTRUCTIONS.read_text(encoding="utf-8"))
            data["obstructions"][0]["expected_context_code_length"] = 4
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_obstructions(path)

            report = validate_fixed_point_obstructions(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-obstruction-length", report.failed_subjects)
        self.assertTrue(
            any("context code length mismatch" in result.detail for result in report.results)
        )

    def test_overclaiming_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "obstructions.json"
            data = json.loads(OBSTRUCTIONS.read_text(encoding="utf-8"))
            data["obstructions"][0]["status"] = "fixed-point-constructed"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_obstructions(path)

            report = validate_fixed_point_obstructions(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-obstruction-status", report.failed_subjects)
        self.assertTrue(any("unknown status" in result.detail for result in report.results))

    def test_cli_returns_zero_for_checked_in_obstructions(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_obstruction.run_fixed_point_obstruction_cli(
                [
                    "--obstructions",
                    str(OBSTRUCTIONS),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point obstructions: accepted", output)

    def test_cli_returns_json_for_checked_in_obstructions(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_obstruction.run_fixed_point_obstruction_cli(
                [
                    "--obstructions",
                    str(OBSTRUCTIONS),
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
        self.assertTrue(payload["obstructions"][0]["impossible_by_length"])

    def test_module_execution_runs_obstruction_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point_obstruction"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fixed-point obstructions: accepted", completed.stdout)

    def test_module_execution_runs_json_obstruction_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_obstruction",
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
        self.assertEqual(
            payload["obstruction_set_id"],
            "as-fixed-point-obstruction-v1",
        )


if __name__ == "__main__":
    unittest.main()
