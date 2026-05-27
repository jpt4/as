import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_bridge_equality_proof_closure_readiness
from autarkic_systems.fixed_point_bridge_equality_proof_closure_readiness import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_OPEN_PROOF_BLOCKERS,
    REQUIRED_PREDECESSOR_CASE_KINDS,
    load_fixed_point_bridge_equality_proof_closure_readiness,
    validate_fixed_point_bridge_equality_proof_closure_readiness,
)


READINESS = Path("claims/fixed_point_bridge_equality_proof_closure_readiness.json")
EXPANDED_COVERAGE = Path(
    "claims/fixed_point_expanded_available_predecessor_certificate_coverage.json"
)
BRIDGE_FRONTIER = Path("claims/fixed_point_bridge_equality_frontier_status.json")
BRIDGE_CERTIFICATE = Path("claims/fixed_point_bridge_equality_certificate.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointBridgeEqualityProofClosureReadinessTests(unittest.TestCase):
    def setUp(self):
        self.readiness = load_fixed_point_bridge_equality_proof_closure_readiness(
            READINESS
        )

    def test_checked_in_manifest_names_bridge_equality_readiness_inputs(self):
        self.assertEqual(self.readiness.schema_version, 1)
        self.assertEqual(
            self.readiness.readiness_id,
            "as-fixed-point-bridge-equality-proof-closure-readiness-v1",
        )
        self.assertEqual(
            self.readiness.expanded_available_predecessor_certificate_coverage_path,
            str(EXPANDED_COVERAGE),
        )
        self.assertEqual(
            self.readiness.bridge_equality_frontier_status_path,
            str(BRIDGE_FRONTIER),
        )
        self.assertEqual(
            self.readiness.bridge_equality_certificate_path,
            str(BRIDGE_CERTIFICATE),
        )
        self.assertEqual(self.readiness.expected_readiness_case_kind, "bridge-equality-proof")
        self.assertEqual(
            self.readiness.expected_readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(
            self.readiness.expected_predecessor_case_kinds,
            REQUIRED_PREDECESSOR_CASE_KINDS,
        )
        self.assertEqual(
            self.readiness.expected_open_proof_blocker_case_kinds,
            REQUIRED_OPEN_PROOF_BLOCKERS,
        )
        self.assertEqual(self.readiness.expected_available_predecessor_certificate_count, 3)
        self.assertEqual(self.readiness.expected_missing_certificate_predecessor_count, 0)
        self.assertEqual(self.readiness.expected_open_proof_blocker_count, 3)
        self.assertEqual(self.readiness.expected_bridge_equality_certificate_step_count, 6)
        self.assertIn("no bridge equality proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_bridge_equality_proof_closure_readiness(self):
        report = validate_fixed_point_bridge_equality_proof_closure_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.readiness_entry.case_kind, "bridge-equality-proof")
        self.assertEqual(
            report.readiness_entry.readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(report.readiness_entry.available_predecessor_certificate_count, 3)
        self.assertEqual(report.readiness_entry.missing_certificate_predecessor_count, 0)
        self.assertEqual(report.readiness_entry.open_proof_blocker_count, 3)
        self.assertTrue(report.proof_boundary_preserved)

    def test_json_payload_exposes_bridge_equality_certificate_ready_proof_open_boundary(self):
        report = validate_fixed_point_bridge_equality_proof_closure_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_bridge_equality_proof_closure_readiness
            .fixed_point_bridge_equality_proof_closure_readiness_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["observed_expanded_coverage_accepted"])
        self.assertTrue(payload["observed_bridge_frontier_accepted"])
        self.assertTrue(payload["observed_bridge_certificate_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertEqual(payload["bridge_equality_frontier_status"], "blocked")
        self.assertEqual(payload["bridge_equality_frontier_blocker"], "bridge-equality-proof")
        self.assertEqual(payload["bridge_equality_certificate_step_count"], 6)
        entry = payload["readiness_entry"]
        self.assertEqual(entry["case_kind"], "bridge-equality-proof")
        self.assertEqual(entry["readiness_status"], "blocked-certificate-ready-proof-open")
        self.assertEqual(
            entry["predecessor_case_kinds"],
            [
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertEqual(
            entry["certificate_covered_predecessor_case_kinds"],
            [
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertEqual(entry["missing_certificate_predecessor_case_kinds"], [])
        self.assertEqual(
            entry["open_proof_blocker_case_kinds"],
            [
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
            ],
        )

    def test_text_report_exposes_readiness_without_promotion(self):
        report = validate_fixed_point_bridge_equality_proof_closure_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        text = (
            fixed_point_bridge_equality_proof_closure_readiness
            .format_fixed_point_bridge_equality_proof_closure_readiness_report(report)
        )

        self.assertIn(
            "Fixed-point bridge equality proof-closure readiness: accepted",
            text,
        )
        self.assertIn("Readiness status: blocked-certificate-ready-proof-open", text)
        self.assertIn("Available predecessor certificates: 3", text)
        self.assertIn("Missing predecessor certificates: none", text)
        self.assertIn("Open proof blockers: diagonal-instance-closure", text)
        self.assertIn("Bridge frontier: blocked by bridge-equality-proof", text)
        self.assertIn("Bridge certificate steps: 6", text)
        self.assertIn("Non-claims: no diagonal-instance closure proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_open_proof_blocker_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["expected_open_proof_blocker_case_kinds"] = [
                "diagonal-instance-closure",
                "substitution-representability-proof",
            ]
            data["expected_open_proof_blocker_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_bridge_equality_proof_closure_readiness(path)

            report = validate_fixed_point_bridge_equality_proof_closure_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-proof-closure-readiness-open-blockers",
            report.failed_subjects,
        )
        self.assertTrue(
            any("open proof blocker mismatch" in result.detail for result in report.results)
        )

    def test_missing_expanded_coverage_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["expanded_available_predecessor_certificate_coverage_path"] = (
                "claims/missing_expanded_available_predecessor_certificate_coverage.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_bridge_equality_proof_closure_readiness(path)

            report = validate_fixed_point_bridge_equality_proof_closure_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-proof-closure-readiness-dependencies",
            report.failed_subjects,
        )
        self.assertFalse(report.expanded_coverage_accepted)
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_readiness(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_bridge_equality_proof_closure_readiness
                .run_fixed_point_bridge_equality_proof_closure_readiness_cli(
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
            "as-fixed-point-bridge-equality-proof-closure-readiness-v1",
        )


if __name__ == "__main__":
    unittest.main()
