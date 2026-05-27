import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_construction_proof_readiness_coverage
from autarkic_systems.fixed_point_construction_proof_readiness_coverage import (
    REQUIRED_CASE_KINDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_construction_proof_readiness_coverage,
    validate_fixed_point_construction_proof_readiness_coverage,
)


COVERAGE = Path("claims/fixed_point_construction_proof_readiness_coverage.json")
FRONTIER = Path("claims/fixed_point_construction_frontier_status.json")
DIAGONAL_READINESS = Path(
    "claims/fixed_point_diagonal_instance_closure_proof_readiness.json"
)
SUBSTITUTION_READINESS = Path(
    "claims/fixed_point_substitution_representability_proof_readiness.json"
)
GRAPH_READINESS = Path(
    "claims/fixed_point_substitution_graph_correctness_proof_readiness.json"
)
BRIDGE_READINESS = Path(
    "claims/fixed_point_bridge_equality_proof_closure_readiness.json"
)
EQUATION_READINESS = Path(
    "claims/fixed_point_equation_lifting_proof_readiness.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointConstructionProofReadinessCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = load_fixed_point_construction_proof_readiness_coverage(
            COVERAGE
        )

    def test_checked_in_manifest_names_construction_readiness_inputs(self):
        self.assertEqual(self.coverage.schema_version, 1)
        self.assertEqual(
            self.coverage.coverage_id,
            "as-fixed-point-construction-proof-readiness-coverage-v1",
        )
        self.assertEqual(
            self.coverage.fixed_point_construction_frontier_status_path,
            str(FRONTIER),
        )
        self.assertEqual(
            self.coverage.readiness_paths,
            {
                "diagonal-instance-closure": str(DIAGONAL_READINESS),
                "substitution-representability-proof": str(SUBSTITUTION_READINESS),
                "substitution-graph-correctness-proof": str(GRAPH_READINESS),
                "bridge-equality-proof": str(BRIDGE_READINESS),
                "fixed-point-equation-lifting": str(EQUATION_READINESS),
            },
        )
        self.assertEqual(self.coverage.expected_frontier_status, "blocked")
        self.assertEqual(
            self.coverage.expected_frontier_blocker,
            "fixed-point-construction",
        )
        self.assertEqual(self.coverage.expected_case_kinds, REQUIRED_CASE_KINDS)
        self.assertEqual(self.coverage.expected_open_case_count, 5)
        self.assertEqual(self.coverage.expected_readiness_count, 5)
        self.assertEqual(self.coverage.expected_missing_readiness_count, 0)
        self.assertEqual(self.coverage.expected_certificate_ready_count, 5)
        self.assertIn("no fixed-point construction proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_construction_readiness_coverage(self):
        report = validate_fixed_point_construction_proof_readiness_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(report.frontier_accepted)
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocker, "fixed-point-construction")
        self.assertEqual(report.open_case_count, 5)
        self.assertEqual(report.readiness_count, 5)
        self.assertEqual(report.missing_readiness_count, 0)
        self.assertEqual(report.certificate_ready_count, 5)
        self.assertTrue(report.proof_boundary_preserved)

    def test_json_payload_exposes_complete_construction_readiness_coverage(self):
        report = validate_fixed_point_construction_proof_readiness_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_construction_proof_readiness_coverage
            .fixed_point_construction_proof_readiness_coverage_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["observed_frontier_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocker"], "fixed-point-construction")
        self.assertEqual(payload["open_case_count"], 5)
        self.assertEqual(payload["readiness_count"], 5)
        self.assertEqual(payload["missing_readiness_count"], 0)
        self.assertEqual(payload["certificate_ready_count"], 5)
        self.assertEqual(payload["open_case_kinds"], list(REQUIRED_CASE_KINDS))
        self.assertEqual(
            [entry["case_kind"] for entry in payload["readiness_entries"]],
            list(REQUIRED_CASE_KINDS),
        )
        self.assertTrue(
            all(
                entry["readiness_status"] == "blocked-certificate-ready-proof-open"
                for entry in payload["readiness_entries"]
            )
        )
        self.assertTrue(
            all(entry["certificate_ready"] for entry in payload["readiness_entries"])
        )
        self.assertTrue(
            all(entry["proof_open"] for entry in payload["readiness_entries"])
        )

    def test_text_report_exposes_coverage_without_promotion(self):
        report = validate_fixed_point_construction_proof_readiness_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        text = (
            fixed_point_construction_proof_readiness_coverage
            .format_fixed_point_construction_proof_readiness_coverage_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point construction proof-readiness coverage: accepted",
            text,
        )
        self.assertIn("Frontier: blocked by fixed-point-construction", text)
        self.assertIn("Open construction cases: 5", text)
        self.assertIn("Readiness entries: 5", text)
        self.assertIn("Missing readiness: none", text)
        self.assertIn("Certificate-ready handoffs: 5", text)
        self.assertIn("Readiness coverage: diagonal-instance-closure", text)
        self.assertIn("Non-claims: no diagonal-instance closure proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_case_kind_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["expected_case_kinds"] = [
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
            ]
            data["expected_open_case_count"] = 4
            data["expected_readiness_count"] = 4
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_construction_proof_readiness_coverage(
                path
            )

            report = validate_fixed_point_construction_proof_readiness_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-proof-readiness-coverage-cases",
            report.failed_subjects,
        )
        self.assertTrue(
            any("case kind mismatch" in result.detail for result in report.results)
        )

    def test_missing_readiness_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["readiness_paths"]["fixed-point-equation-lifting"] = (
                "claims/missing_fixed_point_equation_lifting_proof_readiness.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_construction_proof_readiness_coverage(
                path
            )

            report = validate_fixed_point_construction_proof_readiness_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-proof-readiness-coverage-dependencies",
            report.failed_subjects,
        )
        self.assertEqual(report.missing_readiness_count, 1)
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_coverage(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_construction_proof_readiness_coverage
                .run_fixed_point_construction_proof_readiness_coverage_cli(
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
            "as-fixed-point-construction-proof-readiness-coverage-v1",
        )


if __name__ == "__main__":
    unittest.main()
