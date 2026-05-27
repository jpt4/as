import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_expanded_available_predecessor_certificate_coverage
from autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage import (
    REQUIRED_AVAILABLE_CERTIFICATE_SUBJECTS,
    REQUIRED_DEFERRED_CASE_KINDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_expanded_available_predecessor_certificate_coverage,
    validate_fixed_point_expanded_available_predecessor_certificate_coverage,
)


COVERAGE = Path(
    "claims/fixed_point_expanded_available_predecessor_certificate_coverage.json"
)
BASE_COVERAGE = Path("claims/fixed_point_available_predecessor_certificate_coverage.json")
SUBSTITUTION_CERTIFICATE = Path(
    "claims/fixed_point_substitution_representability_certificate.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointExpandedAvailablePredecessorCertificateCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = (
            load_fixed_point_expanded_available_predecessor_certificate_coverage(
                COVERAGE
            )
        )

    def test_checked_in_manifest_names_expanded_certificate_inputs(self):
        self.assertEqual(self.coverage.schema_version, 1)
        self.assertEqual(
            self.coverage.coverage_id,
            "as-fixed-point-expanded-available-predecessor-certificate-coverage-v1",
        )
        self.assertEqual(
            self.coverage.available_predecessor_certificate_coverage_path,
            str(BASE_COVERAGE),
        )
        self.assertEqual(
            self.coverage.substitution_representability_certificate_path,
            str(SUBSTITUTION_CERTIFICATE),
        )
        self.assertEqual(self.coverage.expected_deferred_case_count, 3)
        self.assertEqual(
            self.coverage.expected_deferred_case_kinds,
            REQUIRED_DEFERRED_CASE_KINDS,
        )
        self.assertEqual(
            self.coverage.expected_available_certificate_subjects,
            REQUIRED_AVAILABLE_CERTIFICATE_SUBJECTS,
        )
        self.assertEqual(self.coverage.expected_total_available_certificate_step_count, 27)
        self.assertIn("no bridge equality proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_expanded_available_predecessor_coverage(self):
        report = validate_fixed_point_expanded_available_predecessor_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.coverage_entry_count, 3)
        self.assertEqual(
            report.available_certificate_subjects,
            self.coverage.expected_available_certificate_subjects,
        )
        self.assertEqual(report.total_available_certificate_step_count, 27)
        self.assertTrue(all(entry.accepted for entry in report.coverage_entries))

    def test_json_payload_exposes_expanded_predecessor_certificate_coverage(self):
        report = validate_fixed_point_expanded_available_predecessor_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_expanded_available_predecessor_certificate_coverage
            .fixed_point_expanded_available_predecessor_certificate_coverage_payload(
                report
            )
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["coverage_entry_count"], 3)
        self.assertEqual(payload["total_available_certificate_step_count"], 27)
        self.assertEqual(
            payload["available_certificate_subjects"],
            [
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
                "substitution-representability-proof",
                "bridge-equality-proof",
            ],
        )
        coverage_by_kind = {
            entry["deferred_case_kind"]: entry
            for entry in payload["coverage_entries"]
        }
        self.assertEqual(
            coverage_by_kind["bridge-equality-proof"][
                "certificate_covered_predecessor_case_kinds"
            ],
            [
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertEqual(
            coverage_by_kind["bridge-equality-proof"][
                "missing_certificate_predecessor_case_kinds"
            ],
            [],
        )
        self.assertEqual(
            coverage_by_kind["bridge-equality-proof"][
                "open_proof_blocker_case_kinds"
            ],
            [
                "diagonal-instance-closure",
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertTrue(payload["observed_base_coverage_accepted"])
        self.assertTrue(payload["observed_substitution_certificate_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])

    def test_text_report_exposes_expanded_coverage_without_promotion(self):
        report = validate_fixed_point_expanded_available_predecessor_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        text = (
            fixed_point_expanded_available_predecessor_certificate_coverage
            .format_fixed_point_expanded_available_predecessor_certificate_coverage_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point expanded available predecessor certificate coverage: accepted",
            text,
        )
        self.assertIn("Available certificate subjects: diagonal-instance-closure", text)
        self.assertIn("Total available certificate steps: 27", text)
        self.assertIn("bridge-equality-proof: blocked", text)
        self.assertIn("covered predecessors: 3/3", text)
        self.assertIn("missing certificate predecessors: none", text)
        self.assertIn("open proof blockers: diagonal-instance-closure", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_bridge_missing_certificate_predecessor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["expected_missing_certificate_predecessors"][
                "bridge-equality-proof"
            ] = ["substitution-representability-proof"]
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = (
                load_fixed_point_expanded_available_predecessor_certificate_coverage(
                    path
                )
            )

            report = (
                validate_fixed_point_expanded_available_predecessor_certificate_coverage(
                    coverage,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-expanded-available-predecessor-certificate-coverage-missing-predecessors",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing certificate predecessor mismatch" in result.detail for result in report.results)
        )

    def test_missing_base_coverage_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["available_predecessor_certificate_coverage_path"] = (
                "claims/missing_available_predecessor_certificate_coverage.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = (
                load_fixed_point_expanded_available_predecessor_certificate_coverage(
                    path
                )
            )

            report = (
                validate_fixed_point_expanded_available_predecessor_certificate_coverage(
                    coverage,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-expanded-available-predecessor-certificate-coverage-dependencies",
            report.failed_subjects,
        )
        self.assertFalse(report.base_coverage_accepted)
        self.assertFalse(report.proof_boundary_preserved)

    def test_missing_substitution_certificate_dependency_is_structured_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["substitution_representability_certificate_path"] = (
                "claims/missing_substitution_representability_certificate.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = (
                load_fixed_point_expanded_available_predecessor_certificate_coverage(
                    path
                )
            )

            report = (
                validate_fixed_point_expanded_available_predecessor_certificate_coverage(
                    coverage,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-expanded-available-predecessor-certificate-coverage-dependencies",
            report.failed_subjects,
        )
        self.assertFalse(report.substitution_certificate_accepted)
        self.assertFalse(report.proof_boundary_preserved)

    def test_cli_returns_json_for_checked_in_coverage(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_expanded_available_predecessor_certificate_coverage
                .run_fixed_point_expanded_available_predecessor_certificate_coverage_cli(
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
            "as-fixed-point-expanded-available-predecessor-certificate-coverage-v1",
        )


if __name__ == "__main__":
    unittest.main()
