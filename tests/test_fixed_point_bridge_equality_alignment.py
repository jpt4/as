import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_bridge_equality_alignment
from autarkic_systems.fixed_point_bridge_equality_alignment import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_fixed_point_bridge_equality_alignment,
    validate_fixed_point_bridge_equality_alignment,
)


ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
SUBSTITUTION_WITNESS_BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")
SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE = Path(
    "claims/fixed_point_substitution_graph_correctness_bridge.json"
)
FORMULA_SCHEMA_RELATION = Path("claims/substitution_graph_formula_schema_relation.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointBridgeEqualityAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.alignment = load_fixed_point_bridge_equality_alignment(ALIGNMENT)

    def test_checked_in_manifest_names_bridge_equality_alignment_domain(self):
        self.assertEqual(self.alignment.schema_version, 1)
        self.assertEqual(
            self.alignment.alignment_set_id,
            "as-fixed-point-bridge-equality-alignment-v1",
        )
        self.assertEqual(
            self.alignment.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.alignment.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.alignment.substitution_witness_bridge_path,
            str(SUBSTITUTION_WITNESS_BRIDGE),
        )
        self.assertEqual(
            self.alignment.substitution_graph_correctness_bridge_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE),
        )
        self.assertEqual(
            self.alignment.formula_schema_relation_path,
            str(FORMULA_SCHEMA_RELATION),
        )
        self.assertEqual(self.alignment.expected_alignment_count, 1)
        self.assertEqual(self.alignment.expected_bridge_equation_code_length, 4815)
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("bridge-equality-alignment",))
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "bridge-equality-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution graph correctness proof",
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_bridge_equality_alignment_domain(self):
        report = validate_fixed_point_bridge_equality_alignment(
            self.alignment,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.alignment_count, 1)
        self.assertEqual(report.source_kind_counts["bridge-equality-alignment"], 1)

    def test_json_payload_exposes_bridge_equality_alignment(self):
        report = validate_fixed_point_bridge_equality_alignment(
            self.alignment,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_bridge_equality_alignment
            .fixed_point_bridge_equality_alignment_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["alignment_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        alignment = payload["alignments"][0]
        self.assertEqual(
            alignment["alignment_id"],
            "AS-FIXED-POINT-BRIDGE-EQUALITY-ALIGNMENT",
        )
        self.assertEqual(alignment["observed_bridge_equation_code_length"], 4815)
        self.assertTrue(alignment["observed_construction_case_is_open"])
        self.assertTrue(alignment["observed_construction_case_requires_alignment"])
        self.assertTrue(alignment["observed_bridge_equation_matches_schema_instance"])
        self.assertTrue(alignment["observed_left_term_matches_witness_output_quote"])
        self.assertTrue(alignment["observed_right_term_quotes_diagonal_instance"])
        self.assertTrue(alignment["observed_route_ids_match"])
        self.assertTrue(alignment["observed_all_dependencies_accepted"])

    def test_text_report_exposes_bridge_equality_alignment_boundary(self):
        report = validate_fixed_point_bridge_equality_alignment(
            self.alignment,
            WILLARD_MAP,
        )

        text = (
            fixed_point_bridge_equality_alignment
            .format_fixed_point_bridge_equality_alignment_report(report)
        )

        self.assertIn("Fixed-point bridge equality alignment: accepted", text)
        self.assertIn("Bridge-equality alignments: 1", text)
        self.assertIn("bridge-equality-alignment=1", text)
        self.assertIn("Alignment failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_alignment_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alignment.json"
            data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
            data["expected_alignment_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            alignment = load_fixed_point_bridge_equality_alignment(path)

            report = validate_fixed_point_bridge_equality_alignment(
                alignment,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-alignment-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("alignment count mismatch" in result.detail for result in report.results)
        )

    def test_stale_bridge_equation_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alignment.json"
            data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
            data["expected_bridge_equation_code_length"] = 4816
            path.write_text(json.dumps(data), encoding="utf-8")
            alignment = load_fixed_point_bridge_equality_alignment(path)

            report = validate_fixed_point_bridge_equality_alignment(
                alignment,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-alignment-length",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "bridge equation length mismatch" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "alignment.json"
            data = json.loads(ALIGNMENT.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            alignment = load_fixed_point_bridge_equality_alignment(path)

            report = validate_fixed_point_bridge_equality_alignment(
                alignment,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-alignment-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_alignment_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_bridge_equality_alignment
                .run_fixed_point_bridge_equality_alignment_cli(
                    [
                        "--alignment",
                        str(ALIGNMENT),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point bridge equality alignment: accepted", output)

    def test_cli_returns_json_for_checked_in_alignment_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_bridge_equality_alignment
                .run_fixed_point_bridge_equality_alignment_cli(
                    [
                        "--alignment",
                        str(ALIGNMENT),
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
        self.assertEqual(payload["alignment_count"], 1)

    def test_module_execution_runs_alignment_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_bridge_equality_alignment",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point bridge equality alignment: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_alignment_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_bridge_equality_alignment",
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
            payload["alignment_set_id"],
            "as-fixed-point-bridge-equality-alignment-v1",
        )


if __name__ == "__main__":
    unittest.main()
