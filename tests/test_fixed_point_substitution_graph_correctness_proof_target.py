import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_substitution_graph_correctness_proof_target
from autarkic_systems.fixed_point_substitution_graph_correctness_proof_target import (
    REQUIRED_MISSING_PROOF_ARTIFACTS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_substitution_graph_correctness_proof_target,
    validate_fixed_point_substitution_graph_correctness_proof_target,
)


TARGET = Path("claims/fixed_point_substitution_graph_correctness_proof_target.json")
CERTIFICATE = Path(
    "claims/fixed_point_substitution_graph_correctness_certificate.json"
)
READINESS = Path(
    "claims/fixed_point_substitution_graph_correctness_proof_readiness.json"
)
COVERAGE = Path("claims/fixed_point_selected_root_proof_readiness_coverage.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointSubstitutionGraphCorrectnessProofTargetTests(unittest.TestCase):
    def setUp(self):
        self.target = (
            load_fixed_point_substitution_graph_correctness_proof_target(
                TARGET,
            )
        )

    def test_checked_in_manifest_names_proof_target_inputs(self):
        self.assertEqual(self.target.schema_version, 1)
        self.assertEqual(
            self.target.target_id,
            "as-fixed-point-substitution-graph-correctness-proof-target-v1",
        )
        self.assertEqual(
            self.target.substitution_graph_correctness_certificate_path,
            str(CERTIFICATE),
        )
        self.assertEqual(
            self.target.substitution_graph_correctness_readiness_path,
            str(READINESS),
        )
        self.assertEqual(
            self.target.selected_root_readiness_coverage_path,
            str(COVERAGE),
        )
        self.assertEqual(
            self.target.expected_case_id,
            "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS",
        )
        self.assertEqual(
            self.target.expected_case_kind,
            "substitution-graph-correctness-proof",
        )
        self.assertEqual(
            self.target.expected_proof_target_status,
            "blocked-proof-closure-targeted",
        )
        self.assertEqual(
            self.target.expected_readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(self.target.expected_certificate_count, 1)
        self.assertEqual(self.target.expected_certificate_step_count, 7)
        self.assertEqual(self.target.expected_correctness_case_count, 5)
        self.assertEqual(self.target.expected_finite_dependency_count, 5)
        self.assertEqual(
            self.target.expected_missing_proof_artifacts,
            REQUIRED_MISSING_PROOF_ARTIFACTS,
        )
        self.assertEqual(self.target.expected_missing_proof_artifact_count, 3)
        self.assertIn("no substitution graph correctness proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no fixed-point construction proof", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_proof_target(self):
        report = validate_fixed_point_substitution_graph_correctness_proof_target(
            self.target,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(report.certificate_accepted)
        self.assertTrue(report.readiness_accepted)
        self.assertTrue(report.selected_root_coverage_accepted)
        self.assertEqual(report.proof_target_status, "blocked-proof-closure-targeted")
        self.assertEqual(report.certificate_count, 1)
        self.assertEqual(report.certificate_step_count, 7)
        self.assertEqual(report.correctness_case_count, 5)
        self.assertEqual(report.finite_dependency_count, 5)
        self.assertEqual(report.missing_proof_artifact_count, 3)
        self.assertTrue(report.proof_boundary_preserved)
        self.assertFalse(report.proof_closure_ready)

    def test_json_payload_exposes_blocked_proof_target(self):
        report = validate_fixed_point_substitution_graph_correctness_proof_target(
            self.target,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_substitution_graph_correctness_proof_target
            .fixed_point_substitution_graph_correctness_proof_target_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["case_kind"], "substitution-graph-correctness-proof")
        self.assertEqual(payload["proof_target_status"], "blocked-proof-closure-targeted")
        self.assertEqual(
            payload["readiness_status"],
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(payload["certificate_count"], 1)
        self.assertEqual(payload["certificate_step_count"], 7)
        self.assertEqual(payload["correctness_case_count"], 5)
        self.assertEqual(payload["finite_dependency_count"], 5)
        self.assertEqual(payload["missing_proof_artifact_count"], 3)
        self.assertEqual(
            payload["missing_proof_artifacts"],
            list(REQUIRED_MISSING_PROOF_ARTIFACTS),
        )
        self.assertTrue(payload["observed_certificate_accepted"])
        self.assertTrue(payload["observed_readiness_accepted"])
        self.assertTrue(payload["observed_selected_root_coverage_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertFalse(payload["proof_closure_ready"])

    def test_text_report_exposes_target_without_promotion(self):
        report = validate_fixed_point_substitution_graph_correctness_proof_target(
            self.target,
            WILLARD_MAP,
        )

        text = (
            fixed_point_substitution_graph_correctness_proof_target
            .format_fixed_point_substitution_graph_correctness_proof_target_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point substitution graph correctness proof target: accepted",
            text,
        )
        self.assertIn("Proof target status: blocked-proof-closure-targeted", text)
        self.assertIn("Certificate steps: 7", text)
        self.assertIn("Correctness cases: 5", text)
        self.assertIn("Finite dependencies: 5", text)
        self.assertIn("Missing proof artifacts: formal graph-correctness derivation", text)
        self.assertIn("Proof closure ready: false", text)
        self.assertIn("Non-claims: no substitution graph correctness proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_missing_proof_artifacts_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "target.json"
            data = json.loads(TARGET.read_text(encoding="utf-8"))
            data["expected_missing_proof_artifacts"] = data[
                "expected_missing_proof_artifacts"
            ][:-1]
            data["expected_missing_proof_artifact_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            target = load_fixed_point_substitution_graph_correctness_proof_target(path)

            report = validate_fixed_point_substitution_graph_correctness_proof_target(
                target,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-proof-target-artifacts",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing proof artifact mismatch" in result.detail for result in report.results)
        )

    def test_stale_correctness_case_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "target.json"
            data = json.loads(TARGET.read_text(encoding="utf-8"))
            data["expected_correctness_case_count"] = 4
            path.write_text(json.dumps(data), encoding="utf-8")
            target = load_fixed_point_substitution_graph_correctness_proof_target(path)

            report = validate_fixed_point_substitution_graph_correctness_proof_target(
                target,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-proof-target-cases",
            report.failed_subjects,
        )
        self.assertTrue(
            any("correctness case count mismatch" in result.detail for result in report.results)
        )

    def test_missing_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "target.json"
            data = json.loads(TARGET.read_text(encoding="utf-8"))
            data["substitution_graph_correctness_readiness_path"] = (
                "claims/missing_substitution_graph_correctness_readiness.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            target = load_fixed_point_substitution_graph_correctness_proof_target(path)

            report = validate_fixed_point_substitution_graph_correctness_proof_target(
                target,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-proof-target-dependencies",
            report.failed_subjects,
        )
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_target(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_graph_correctness_proof_target
                .run_fixed_point_substitution_graph_correctness_proof_target_cli(
                    [
                        "--target",
                        str(TARGET),
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
            payload["target_id"],
            "as-fixed-point-substitution-graph-correctness-proof-target-v1",
        )


if __name__ == "__main__":
    unittest.main()
