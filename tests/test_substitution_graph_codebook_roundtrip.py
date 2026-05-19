import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_codebook_roundtrip
from autarkic_systems.substitution_graph_codebook_roundtrip import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_substitution_graph_codebook_roundtrip,
    validate_substitution_graph_codebook_roundtrip,
)


ROUNDTRIP = Path("claims/substitution_graph_codebook_roundtrip.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
CODEBOOK = Path("language/formal_codebook.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")


class SubstitutionGraphCodebookRoundtripTests(unittest.TestCase):
    def setUp(self):
        self.roundtrip = load_substitution_graph_codebook_roundtrip(ROUNDTRIP)

    def test_checked_in_manifest_names_roundtrip_domain(self):
        self.assertEqual(self.roundtrip.schema_version, 1)
        self.assertEqual(
            self.roundtrip.roundtrip_set_id,
            "as-substitution-graph-codebook-roundtrip-v1",
        )
        self.assertEqual(self.roundtrip.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.roundtrip.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.roundtrip.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(self.roundtrip.expected_subject_count, 12)
        self.assertEqual(
            REQUIRED_SOURCE_KINDS,
            (
                "formula-candidate",
                "finite-evaluation",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "formula-correctness-proof",
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no formula correctness proof",
                "no substitution representability proof",
                "no diagonal lemma proof",
                "no fixed-point equation proof",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_roundtrip_domain(self):
        report = validate_substitution_graph_codebook_roundtrip(
            self.roundtrip,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.subject_count, 12)
        self.assertEqual(report.source_kind_counts["formula-candidate"], 3)
        self.assertEqual(report.source_kind_counts["finite-evaluation"], 9)
        self.assertTrue(
            any(
                result.subject == "roundtrip_subjects"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_roundtrip_subjects(self):
        report = validate_substitution_graph_codebook_roundtrip(
            self.roundtrip,
            WILLARD_MAP,
        )

        payload = (
            substitution_graph_codebook_roundtrip
            .substitution_graph_codebook_roundtrip_report_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["subject_count"], 12)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["source_kind_counts"]["formula-candidate"], 3)
        self.assertEqual(payload["source_kind_counts"]["finite-evaluation"], 9)
        self.assertTrue(
            all(subject["observed_roundtrip_ok"] for subject in payload["subjects"])
        )
        self.assertIn(
            "AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA.formula_code",
            {subject["subject_id"] for subject in payload["subjects"]},
        )

    def test_text_report_exposes_roundtrip_boundary(self):
        report = validate_substitution_graph_codebook_roundtrip(
            self.roundtrip,
            WILLARD_MAP,
        )

        text = (
            substitution_graph_codebook_roundtrip
            .format_substitution_graph_codebook_roundtrip_report(report)
        )

        self.assertIn("Substitution graph codebook roundtrip: accepted", text)
        self.assertIn("Subjects: 12", text)
        self.assertIn("formula-candidate=3", text)
        self.assertIn("finite-evaluation=9", text)
        self.assertIn("Roundtrip failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_subject_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roundtrip.json"
            data = json.loads(ROUNDTRIP.read_text(encoding="utf-8"))
            data["expected_subject_count"] = 11
            path.write_text(json.dumps(data), encoding="utf-8")
            roundtrip = load_substitution_graph_codebook_roundtrip(path)

            report = validate_substitution_graph_codebook_roundtrip(
                roundtrip,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-codebook-roundtrip-count", report.failed_subjects)
        self.assertTrue(
            any("subject count mismatch" in result.detail for result in report.results)
        )

    def test_missing_required_future_work_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roundtrip.json"
            data = json.loads(ROUNDTRIP.read_text(encoding="utf-8"))
            data["required_future_work"] = data["required_future_work"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            roundtrip = load_substitution_graph_codebook_roundtrip(path)

            report = validate_substitution_graph_codebook_roundtrip(
                roundtrip,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-codebook-roundtrip-future-work", report.failed_subjects)
        self.assertTrue(
            any("missing future work" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_roundtrip_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_codebook_roundtrip
                .run_substitution_graph_codebook_roundtrip_cli(
                    ["--roundtrip", str(ROUNDTRIP), "--willard-map", str(WILLARD_MAP)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph codebook roundtrip: accepted", output)

    def test_cli_returns_json_for_checked_in_roundtrip_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_codebook_roundtrip
                .run_substitution_graph_codebook_roundtrip_cli(
                    [
                        "--roundtrip",
                        str(ROUNDTRIP),
                        "--willard-map",
                        str(WILLARD_MAP),
                        "--format",
                        "json",
                    ]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["subject_count"], 12)

    def test_module_execution_runs_roundtrip_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_codebook_roundtrip"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Substitution graph codebook roundtrip: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_roundtrip_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_codebook_roundtrip",
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
        self.assertEqual(payload["subject_count"], 12)


if __name__ == "__main__":
    unittest.main()
