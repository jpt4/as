import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_available_predecessor_certificate_coverage
from autarkic_systems.fixed_point_available_predecessor_certificate_coverage import (
    REQUIRED_DEFERRED_CASE_KINDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_available_predecessor_certificate_coverage,
    validate_fixed_point_available_predecessor_certificate_coverage,
)


COVERAGE = Path("claims/fixed_point_available_predecessor_certificate_coverage.json")
READINESS = Path("claims/fixed_point_deferred_case_certificate_readiness.json")
SELECTED_ROOT_COVERAGE = Path(
    "claims/fixed_point_selected_root_certificate_coverage.json"
)
BRIDGE_CERTIFICATE = Path("claims/fixed_point_bridge_equality_certificate.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointAvailablePredecessorCertificateCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = load_fixed_point_available_predecessor_certificate_coverage(
            COVERAGE
        )

    def test_checked_in_manifest_names_available_certificate_inputs(self):
        self.assertEqual(self.coverage.schema_version, 1)
        self.assertEqual(
            self.coverage.coverage_id,
            "as-fixed-point-available-predecessor-certificate-coverage-v1",
        )
        self.assertEqual(
            self.coverage.deferred_case_certificate_readiness_path,
            str(READINESS),
        )
        self.assertEqual(
            self.coverage.selected_root_certificate_coverage_path,
            str(SELECTED_ROOT_COVERAGE),
        )
        self.assertEqual(
            self.coverage.bridge_equality_certificate_path,
            str(BRIDGE_CERTIFICATE),
        )
        self.assertEqual(self.coverage.expected_deferred_case_count, 3)
        self.assertEqual(
            self.coverage.expected_deferred_case_kinds,
            REQUIRED_DEFERRED_CASE_KINDS,
        )
        self.assertEqual(
            self.coverage.expected_available_certificate_subjects,
            (
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
            ),
        )
        self.assertEqual(
            self.coverage.expected_total_available_certificate_step_count,
            20,
        )
        self.assertIn("no fixed-point equation proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_available_predecessor_coverage(self):
        report = validate_fixed_point_available_predecessor_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.coverage_entry_count, 3)
        self.assertEqual(report.available_certificate_subjects, self.coverage.expected_available_certificate_subjects)
        self.assertEqual(report.total_available_certificate_step_count, 20)
        self.assertTrue(all(entry.accepted for entry in report.coverage_entries))

    def test_json_payload_exposes_available_predecessor_certificate_coverage(self):
        report = validate_fixed_point_available_predecessor_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_available_predecessor_certificate_coverage
            .fixed_point_available_predecessor_certificate_coverage_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["coverage_entry_count"], 3)
        self.assertEqual(payload["total_available_certificate_step_count"], 20)
        self.assertEqual(
            payload["available_certificate_subjects"],
            [
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
            ],
        )
        coverage_by_kind = {
            entry["deferred_case_kind"]: entry
            for entry in payload["coverage_entries"]
        }
        self.assertEqual(
            coverage_by_kind["substitution-representability-proof"][
                "missing_certificate_predecessor_case_kinds"
            ],
            [],
        )
        self.assertEqual(
            coverage_by_kind["bridge-equality-proof"][
                "missing_certificate_predecessor_case_kinds"
            ],
            ["substitution-representability-proof"],
        )
        self.assertEqual(
            coverage_by_kind["fixed-point-equation-lifting"][
                "certificate_covered_predecessor_case_kinds"
            ],
            ["bridge-equality-proof"],
        )
        self.assertEqual(
            coverage_by_kind["fixed-point-equation-lifting"][
                "missing_certificate_predecessor_case_kinds"
            ],
            [],
        )
        self.assertEqual(
            coverage_by_kind["fixed-point-equation-lifting"][
                "open_proof_blocker_case_kinds"
            ],
            ["bridge-equality-proof"],
        )
        self.assertTrue(payload["observed_bridge_equality_certificate_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])

    def test_text_report_exposes_available_coverage_without_promotion(self):
        report = validate_fixed_point_available_predecessor_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        text = (
            fixed_point_available_predecessor_certificate_coverage
            .format_fixed_point_available_predecessor_certificate_coverage_report(report)
        )

        self.assertIn(
            "Fixed-point available predecessor certificate coverage: accepted",
            text,
        )
        self.assertIn("Available certificate subjects: diagonal-instance-closure", text)
        self.assertIn("Total available certificate steps: 20", text)
        self.assertIn("fixed-point-equation-lifting: blocked", text)
        self.assertIn("covered predecessors: 1/1", text)
        self.assertIn("bridge-equality-proof: blocked", text)
        self.assertIn("missing certificate predecessors: substitution-representability-proof", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_equation_lifting_missing_certificate_predecessor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["expected_missing_certificate_predecessors"][
                "fixed-point-equation-lifting"
            ] = ["bridge-equality-proof"]
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_available_predecessor_certificate_coverage(path)

            report = validate_fixed_point_available_predecessor_certificate_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-available-predecessor-certificate-coverage-missing-predecessors",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing certificate predecessor mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_coverage(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_available_predecessor_certificate_coverage
                .run_fixed_point_available_predecessor_certificate_coverage_cli(
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
            "as-fixed-point-available-predecessor-certificate-coverage-v1",
        )


if __name__ == "__main__":
    unittest.main()
