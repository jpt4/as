import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_equation_lifting_proof_readiness
from autarkic_systems.fixed_point_equation_lifting_proof_readiness import (
    REQUIRED_NON_CLAIMS,
    load_fixed_point_equation_lifting_proof_readiness,
    validate_fixed_point_equation_lifting_proof_readiness,
)


READINESS = Path("claims/fixed_point_equation_lifting_proof_readiness.json")
FRONTIER = Path("claims/fixed_point_equation_lifting_frontier_status.json")
BRIDGE_READINESS = Path(
    "claims/fixed_point_bridge_equality_proof_closure_readiness.json"
)
BRIDGE_PREDECESSOR_COVERAGE = Path(
    "claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointEquationLiftingProofReadinessTests(unittest.TestCase):
    def setUp(self):
        self.readiness = load_fixed_point_equation_lifting_proof_readiness(
            READINESS
        )

    def test_checked_in_manifest_names_equation_lifting_readiness_inputs(self):
        self.assertEqual(self.readiness.schema_version, 1)
        self.assertEqual(
            self.readiness.readiness_id,
            "as-fixed-point-equation-lifting-proof-readiness-v1",
        )
        self.assertEqual(
            self.readiness.equation_lifting_frontier_status_path,
            str(FRONTIER),
        )
        self.assertEqual(
            self.readiness.bridge_equality_readiness_path,
            str(BRIDGE_READINESS),
        )
        self.assertEqual(
            self.readiness.bridge_predecessor_readiness_coverage_path,
            str(BRIDGE_PREDECESSOR_COVERAGE),
        )
        self.assertEqual(
            self.readiness.expected_readiness_case_id,
            "AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING",
        )
        self.assertEqual(
            self.readiness.expected_readiness_case_kind,
            "fixed-point-equation-lifting",
        )
        self.assertEqual(
            self.readiness.expected_readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(self.readiness.expected_construction_case_status, "proof-case-open")
        self.assertEqual(self.readiness.expected_frontier_status, "blocked")
        self.assertEqual(self.readiness.expected_frontier_blocker, "fixed-point-equation-lifting")
        self.assertEqual(self.readiness.expected_support_surface_count, 4)
        self.assertEqual(self.readiness.expected_direct_target_code_length, 4528)
        self.assertEqual(self.readiness.expected_bridge_equation_code_length, 4815)
        self.assertEqual(
            self.readiness.expected_predecessor_case_kinds,
            ("bridge-equality-proof",),
        )
        self.assertEqual(self.readiness.expected_predecessor_readiness_count, 1)
        self.assertEqual(self.readiness.expected_missing_predecessor_readiness_count, 0)
        self.assertIn("no fixed-point equation proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_equation_lifting_proof_readiness(self):
        report = validate_fixed_point_equation_lifting_proof_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(report.frontier_accepted)
        self.assertTrue(report.bridge_readiness_accepted)
        self.assertTrue(report.bridge_predecessor_coverage_accepted)
        self.assertEqual(report.readiness_entry.case_kind, "fixed-point-equation-lifting")
        self.assertEqual(
            report.readiness_entry.readiness_status,
            "blocked-certificate-ready-proof-open",
        )
        self.assertEqual(report.readiness_entry.construction_case_status, "proof-case-open")
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocker, "fixed-point-equation-lifting")
        self.assertEqual(report.support_surface_count, 4)
        self.assertEqual(report.direct_target_code_length, 4528)
        self.assertEqual(report.bridge_equation_code_length, 4815)
        self.assertEqual(report.predecessor_readiness_count, 1)
        self.assertEqual(report.missing_predecessor_readiness_count, 0)
        self.assertTrue(report.proof_boundary_preserved)

    def test_json_payload_exposes_certificate_ready_proof_open_boundary(self):
        report = validate_fixed_point_equation_lifting_proof_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_equation_lifting_proof_readiness
            .fixed_point_equation_lifting_proof_readiness_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["observed_frontier_accepted"])
        self.assertTrue(payload["observed_bridge_readiness_accepted"])
        self.assertTrue(payload["observed_bridge_predecessor_coverage_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocker"], "fixed-point-equation-lifting")
        self.assertEqual(payload["support_surface_count"], 4)
        self.assertEqual(payload["direct_target_code_length"], 4528)
        self.assertEqual(payload["bridge_equation_code_length"], 4815)
        self.assertEqual(payload["predecessor_readiness_count"], 1)
        self.assertEqual(payload["missing_predecessor_readiness_count"], 0)
        entry = payload["readiness_entry"]
        self.assertEqual(
            entry["case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING",
        )
        self.assertEqual(entry["case_kind"], "fixed-point-equation-lifting")
        self.assertEqual(entry["construction_case_status"], "proof-case-open")
        self.assertEqual(entry["readiness_status"], "blocked-certificate-ready-proof-open")
        self.assertTrue(entry["certificate_ready"])
        self.assertEqual(entry["predecessor_case_kinds"], ["bridge-equality-proof"])
        self.assertEqual(entry["missing_predecessor_case_kinds"], [])
        self.assertEqual(entry["open_proof_blocker"], "fixed-point-equation-lifting")

    def test_text_report_exposes_readiness_without_promotion(self):
        report = validate_fixed_point_equation_lifting_proof_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        text = (
            fixed_point_equation_lifting_proof_readiness
            .format_fixed_point_equation_lifting_proof_readiness_report(report)
        )

        self.assertIn(
            "Fixed-point equation lifting proof readiness: accepted",
            text,
        )
        self.assertIn("Readiness status: blocked-certificate-ready-proof-open", text)
        self.assertIn("Frontier: blocked by fixed-point-equation-lifting", text)
        self.assertIn("Construction case status: proof-case-open", text)
        self.assertIn("Support surfaces: 4", text)
        self.assertIn("Direct target code length: 4528", text)
        self.assertIn("Bridge equation code length: 4815", text)
        self.assertIn("Predecessor readiness: bridge-equality-proof", text)
        self.assertIn("Non-claims: no bridge equality proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_direct_target_code_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["expected_direct_target_code_length"] = 4527
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_equation_lifting_proof_readiness(path)

            report = validate_fixed_point_equation_lifting_proof_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-proof-readiness-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any("direct target code length mismatch" in result.detail for result in report.results)
        )

    def test_stale_predecessor_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["expected_predecessor_case_kinds"] = []
            data["expected_predecessor_readiness_count"] = 0
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_equation_lifting_proof_readiness(path)

            report = validate_fixed_point_equation_lifting_proof_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-proof-readiness-predecessors",
            report.failed_subjects,
        )
        self.assertTrue(
            any("predecessor case kind mismatch" in result.detail for result in report.results)
        )

    def test_missing_frontier_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["equation_lifting_frontier_status_path"] = (
                "claims/missing_fixed_point_equation_lifting_frontier_status.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_equation_lifting_proof_readiness(path)

            report = validate_fixed_point_equation_lifting_proof_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-proof-readiness-dependencies",
            report.failed_subjects,
        )
        self.assertFalse(report.frontier_accepted)
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_readiness(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_equation_lifting_proof_readiness
                .run_fixed_point_equation_lifting_proof_readiness_cli(
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
            "as-fixed-point-equation-lifting-proof-readiness-v1",
        )


if __name__ == "__main__":
    unittest.main()
