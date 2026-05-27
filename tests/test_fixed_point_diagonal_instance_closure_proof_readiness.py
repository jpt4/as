import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_diagonal_instance_closure_proof_readiness
from autarkic_systems.fixed_point_diagonal_instance_closure_proof_readiness import (
    REQUIRED_NON_CLAIMS,
    load_fixed_point_diagonal_instance_closure_proof_readiness,
    validate_fixed_point_diagonal_instance_closure_proof_readiness,
)


READINESS = Path("claims/fixed_point_diagonal_instance_closure_proof_readiness.json")
FRONTIER = Path("claims/fixed_point_diagonal_instance_closure_frontier_status.json")
CERTIFICATE = Path("claims/fixed_point_diagonal_instance_closure_certificate.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointDiagonalInstanceClosureProofReadinessTests(unittest.TestCase):
    def setUp(self):
        self.readiness = load_fixed_point_diagonal_instance_closure_proof_readiness(
            READINESS
        )

    def test_checked_in_manifest_names_diagonal_instance_readiness_inputs(self):
        self.assertEqual(self.readiness.schema_version, 1)
        self.assertEqual(
            self.readiness.readiness_id,
            "as-fixed-point-diagonal-instance-closure-proof-readiness-v1",
        )
        self.assertEqual(
            self.readiness.diagonal_instance_closure_frontier_status_path,
            str(FRONTIER),
        )
        self.assertEqual(
            self.readiness.diagonal_instance_closure_certificate_path,
            str(CERTIFICATE),
        )
        self.assertEqual(
            self.readiness.expected_readiness_case_id,
            "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE",
        )
        self.assertEqual(
            self.readiness.expected_readiness_case_kind,
            "diagonal-instance-closure",
        )
        self.assertEqual(
            self.readiness.expected_readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(self.readiness.expected_construction_case_status, "proof-case-open")
        self.assertEqual(self.readiness.expected_frontier_status, "blocked")
        self.assertEqual(self.readiness.expected_frontier_blocker, "diagonal-instance-closure")
        self.assertEqual(self.readiness.expected_support_surface_count, 5)
        self.assertEqual(self.readiness.expected_certificate_count, 1)
        self.assertEqual(self.readiness.expected_certificate_step_count, 7)
        self.assertEqual(self.readiness.expected_diagonal_instance_code_length, 296)
        self.assertIn("no diagonal-instance closure proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_diagonal_instance_proof_readiness(self):
        report = validate_fixed_point_diagonal_instance_closure_proof_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.readiness_entry.case_kind, "diagonal-instance-closure")
        self.assertEqual(
            report.readiness_entry.readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(report.readiness_entry.construction_case_status, "proof-case-open")
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocker, "diagonal-instance-closure")
        self.assertEqual(report.certificate_step_count, 7)
        self.assertEqual(report.diagonal_instance_code_length, 296)
        self.assertTrue(report.proof_boundary_preserved)

    def test_json_payload_exposes_certificate_ready_proof_open_boundary(self):
        report = validate_fixed_point_diagonal_instance_closure_proof_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_diagonal_instance_closure_proof_readiness
            .fixed_point_diagonal_instance_closure_proof_readiness_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["observed_frontier_accepted"])
        self.assertTrue(payload["observed_certificate_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocker"], "diagonal-instance-closure")
        self.assertEqual(payload["support_surface_count"], 5)
        self.assertEqual(payload["certificate_count"], 1)
        self.assertEqual(payload["certificate_step_count"], 7)
        self.assertEqual(payload["diagonal_instance_code_length"], 296)
        entry = payload["readiness_entry"]
        self.assertEqual(
            entry["case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE",
        )
        self.assertEqual(entry["case_kind"], "diagonal-instance-closure")
        self.assertEqual(entry["construction_case_status"], "proof-case-open")
        self.assertEqual(entry["readiness_status"], "blocked-certificate-ready-proof-open")
        self.assertTrue(entry["certificate_ready"])
        self.assertEqual(entry["open_proof_blocker"], "diagonal-instance-closure")

    def test_text_report_exposes_readiness_without_promotion(self):
        report = validate_fixed_point_diagonal_instance_closure_proof_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        text = (
            fixed_point_diagonal_instance_closure_proof_readiness
            .format_fixed_point_diagonal_instance_closure_proof_readiness_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point diagonal instance closure proof readiness: accepted",
            text,
        )
        self.assertIn("Readiness status: blocked-certificate-ready-proof-open", text)
        self.assertIn("Frontier: blocked by diagonal-instance-closure", text)
        self.assertIn("Construction case status: proof-case-open", text)
        self.assertIn("Certificate steps: 7", text)
        self.assertIn("Diagonal instance code length: 296", text)
        self.assertIn("Non-claims: no diagonal-instance closure proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_certificate_step_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["expected_certificate_step_count"] = 6
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_diagonal_instance_closure_proof_readiness(path)

            report = validate_fixed_point_diagonal_instance_closure_proof_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-proof-readiness-certificate",
            report.failed_subjects,
        )
        self.assertTrue(
            any("certificate step count mismatch" in result.detail for result in report.results)
        )

    def test_missing_frontier_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["diagonal_instance_closure_frontier_status_path"] = (
                "claims/missing_diagonal_instance_closure_frontier_status.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_diagonal_instance_closure_proof_readiness(path)

            report = validate_fixed_point_diagonal_instance_closure_proof_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-proof-readiness-dependencies",
            report.failed_subjects,
        )
        self.assertFalse(report.frontier_accepted)
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_readiness(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_closure_proof_readiness
                .run_fixed_point_diagonal_instance_closure_proof_readiness_cli(
                    [
                        "--readiness",
                        str(READINESS),
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
            payload["readiness_id"],
            "as-fixed-point-diagonal-instance-closure-proof-readiness-v1",
        )


if __name__ == "__main__":
    unittest.main()
