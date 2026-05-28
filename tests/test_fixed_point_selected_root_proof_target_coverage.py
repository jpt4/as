import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_selected_root_proof_target_coverage
from autarkic_systems.fixed_point_selected_root_proof_target_coverage import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_SELECTED_CASE_KINDS,
    load_fixed_point_selected_root_proof_target_coverage,
    validate_fixed_point_selected_root_proof_target_coverage,
)


COVERAGE = Path("claims/fixed_point_selected_root_proof_target_coverage.json")
READINESS_COVERAGE = Path(
    "claims/fixed_point_selected_root_proof_readiness_coverage.json"
)
DIAGONAL_TARGET = Path(
    "claims/fixed_point_diagonal_instance_closure_proof_target.json"
)
GRAPH_TARGET = Path(
    "claims/fixed_point_substitution_graph_correctness_proof_target.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointSelectedRootProofTargetCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = load_fixed_point_selected_root_proof_target_coverage(
            COVERAGE
        )

    def test_checked_in_manifest_names_selected_root_proof_target_inputs(self):
        self.assertEqual(self.coverage.schema_version, 1)
        self.assertEqual(
            self.coverage.coverage_id,
            "as-fixed-point-selected-root-proof-target-coverage-v1",
        )
        self.assertEqual(
            self.coverage.selected_root_readiness_coverage_path,
            str(READINESS_COVERAGE),
        )
        self.assertEqual(
            self.coverage.proof_target_paths,
            {
                "diagonal-instance-closure": str(DIAGONAL_TARGET),
                "substitution-graph-correctness-proof": str(GRAPH_TARGET),
            },
        )
        self.assertEqual(
            self.coverage.expected_selected_case_kinds,
            REQUIRED_SELECTED_CASE_KINDS,
        )
        self.assertEqual(self.coverage.expected_selected_count, 2)
        self.assertEqual(self.coverage.expected_proof_target_count, 2)
        self.assertEqual(self.coverage.expected_blocked_proof_target_count, 2)
        self.assertEqual(self.coverage.expected_proof_closure_ready_count, 0)
        self.assertEqual(self.coverage.expected_missing_proof_artifact_count, 6)
        self.assertIn("no diagonal-instance closure proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no fixed-point construction proof", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_selected_root_proof_target_coverage(self):
        report = validate_fixed_point_selected_root_proof_target_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(report.selected_root_readiness_coverage_accepted)
        self.assertEqual(report.selected_case_count, 2)
        self.assertEqual(report.proof_target_count, 2)
        self.assertEqual(report.blocked_proof_target_count, 2)
        self.assertEqual(report.proof_closure_ready_count, 0)
        self.assertEqual(report.missing_proof_artifact_count, 6)
        self.assertTrue(report.proof_boundary_preserved)

    def test_json_payload_exposes_selected_root_proof_target_coverage(self):
        report = validate_fixed_point_selected_root_proof_target_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_selected_root_proof_target_coverage
            .fixed_point_selected_root_proof_target_coverage_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["observed_selected_root_readiness_coverage_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertEqual(
            payload["selected_case_kinds"],
            list(REQUIRED_SELECTED_CASE_KINDS),
        )
        self.assertEqual(payload["selected_case_count"], 2)
        self.assertEqual(payload["proof_target_count"], 2)
        self.assertEqual(payload["blocked_proof_target_count"], 2)
        self.assertEqual(payload["proof_closure_ready_count"], 0)
        self.assertEqual(payload["missing_proof_artifact_count"], 6)
        self.assertEqual(
            [entry["case_kind"] for entry in payload["proof_target_entries"]],
            list(REQUIRED_SELECTED_CASE_KINDS),
        )
        self.assertTrue(
            all(
                entry["proof_target_status"] == "blocked-proof-closure-targeted"
                for entry in payload["proof_target_entries"]
            )
        )
        self.assertFalse(
            any(entry["proof_closure_ready"] for entry in payload["proof_target_entries"])
        )

    def test_text_report_exposes_target_coverage_without_promotion(self):
        report = validate_fixed_point_selected_root_proof_target_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        text = (
            fixed_point_selected_root_proof_target_coverage
            .format_fixed_point_selected_root_proof_target_coverage_report(report)
        )

        self.assertIn(
            "Fixed-point selected-root proof-target coverage: accepted",
            text,
        )
        self.assertIn("Selected roots: 2", text)
        self.assertIn("Proof targets: 2", text)
        self.assertIn("Blocked proof targets: 2", text)
        self.assertIn("Proof-closure-ready roots: 0", text)
        self.assertIn("Missing proof artifacts: 6", text)
        self.assertIn("Target coverage: diagonal-instance-closure", text)
        self.assertIn("Non-claims: no diagonal-instance closure proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_selected_root_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["expected_selected_case_kinds"] = [
                "diagonal-instance-closure",
            ]
            data["expected_selected_count"] = 1
            data["expected_proof_target_count"] = 1
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_selected_root_proof_target_coverage(path)

            report = validate_fixed_point_selected_root_proof_target_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-selected-root-proof-target-coverage-selection",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "selected case kind mismatch" in result.detail
                for result in report.results
            )
        )

    def test_stale_missing_artifact_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["expected_missing_proof_artifact_count"] = 5
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_selected_root_proof_target_coverage(path)

            report = validate_fixed_point_selected_root_proof_target_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-selected-root-proof-target-coverage-artifacts",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing proof artifact count mismatch" in result.detail for result in report.results)
        )

    def test_missing_target_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["proof_target_paths"]["substitution-graph-correctness-proof"] = (
                "claims/missing_fixed_point_graph_correctness_proof_target.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_selected_root_proof_target_coverage(path)

            report = validate_fixed_point_selected_root_proof_target_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-selected-root-proof-target-coverage-dependencies",
            report.failed_subjects,
        )
        self.assertEqual(report.proof_target_count, 1)
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_coverage(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_selected_root_proof_target_coverage
                .run_fixed_point_selected_root_proof_target_coverage_cli(
                    [
                        "--coverage",
                        str(COVERAGE),
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
        self.assertEqual(
            payload["coverage_id"],
            "as-fixed-point-selected-root-proof-target-coverage-v1",
        )


if __name__ == "__main__":
    unittest.main()
