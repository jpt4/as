import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_selected_root_certificate_coverage
from autarkic_systems.fixed_point_selected_root_certificate_coverage import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_SELECTED_CASE_KINDS,
    load_fixed_point_selected_root_certificate_coverage,
    validate_fixed_point_selected_root_certificate_coverage,
)


COVERAGE = Path("claims/fixed_point_selected_root_certificate_coverage.json")
SELECTOR = Path("claims/fixed_point_frontier_selector.json")
DIAGONAL_CERTIFICATE = Path(
    "claims/fixed_point_diagonal_instance_closure_certificate.json"
)
GRAPH_CERTIFICATE = Path(
    "claims/fixed_point_substitution_graph_correctness_certificate.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointSelectedRootCertificateCoverageTests(unittest.TestCase):
    def setUp(self):
        self.coverage = load_fixed_point_selected_root_certificate_coverage(COVERAGE)

    def test_checked_in_manifest_names_selected_root_certificate_inputs(self):
        self.assertEqual(self.coverage.schema_version, 1)
        self.assertEqual(
            self.coverage.coverage_set_id,
            "as-fixed-point-selected-root-certificate-coverage-v1",
        )
        self.assertEqual(self.coverage.frontier_selector_path, str(SELECTOR))
        self.assertEqual(
            self.coverage.diagonal_instance_closure_certificate_path,
            str(DIAGONAL_CERTIFICATE),
        )
        self.assertEqual(
            self.coverage.substitution_graph_correctness_certificate_path,
            str(GRAPH_CERTIFICATE),
        )
        self.assertEqual(self.coverage.expected_selected_certificate_count, 2)
        self.assertEqual(self.coverage.expected_total_certificate_step_count, 14)
        self.assertEqual(
            self.coverage.expected_selected_case_kinds,
            REQUIRED_SELECTED_CASE_KINDS,
        )
        self.assertEqual(
            REQUIRED_SELECTED_CASE_KINDS,
            ("diagonal-instance-closure", "substitution-graph-correctness-proof"),
        )
        self.assertIn("no fixed-point equation proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_selected_root_certificate_coverage(self):
        report = validate_fixed_point_selected_root_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.coverage_count, 2)
        self.assertEqual(report.total_certificate_step_count, 14)
        self.assertTrue(all(item.accepted for item in report.coverage_entries))

    def test_json_payload_exposes_selected_root_certificate_coverage(self):
        report = validate_fixed_point_selected_root_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_selected_root_certificate_coverage
            .fixed_point_selected_root_certificate_coverage_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["coverage_count"], 2)
        self.assertEqual(payload["total_certificate_step_count"], 14)
        self.assertEqual(
            payload["selected_case_kinds"],
            list(REQUIRED_SELECTED_CASE_KINDS),
        )
        coverage_by_kind = {
            entry["selected_case_kind"]: entry
            for entry in payload["coverage_entries"]
        }
        self.assertEqual(
            coverage_by_kind["diagonal-instance-closure"]["certificate_id"],
            "AS-FIXED-POINT-DIAGONAL-INSTANCE-CLOSURE-CERTIFICATE",
        )
        self.assertEqual(
            coverage_by_kind["substitution-graph-correctness-proof"][
                "certificate_id"
            ],
            "AS-FIXED-POINT-SUBSTITUTION-GRAPH-CORRECTNESS-CERTIFICATE",
        )
        self.assertTrue(
            coverage_by_kind["diagonal-instance-closure"][
                "observed_selector_selects_case"
            ]
        )
        self.assertTrue(
            coverage_by_kind["substitution-graph-correctness-proof"][
                "observed_certificate_accepted"
            ]
        )
        self.assertTrue(payload["observed_proof_boundary_preserved"])
        self.assertIn("no substitution representability proof", payload["non_claims"])

    def test_text_report_exposes_non_promotional_coverage_boundary(self):
        report = validate_fixed_point_selected_root_certificate_coverage(
            self.coverage,
            WILLARD_MAP,
        )

        text = (
            fixed_point_selected_root_certificate_coverage
            .format_fixed_point_selected_root_certificate_coverage_report(report)
        )

        self.assertIn("Fixed-point selected root certificate coverage: accepted", text)
        self.assertIn("Coverage entries: 2", text)
        self.assertIn("Total certificate steps: 14", text)
        self.assertIn("diagonal-instance-closure: accepted", text)
        self.assertIn("substitution-graph-correctness-proof: accepted", text)
        self.assertIn("Non-claims: no diagonal-instance closure proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_selected_case_kinds_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "coverage.json"
            data = json.loads(COVERAGE.read_text(encoding="utf-8"))
            data["expected_selected_case_kinds"] = data[
                "expected_selected_case_kinds"
            ][::-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            coverage = load_fixed_point_selected_root_certificate_coverage(path)

            report = validate_fixed_point_selected_root_certificate_coverage(
                coverage,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-selected-root-certificate-coverage-selected-roots",
            report.failed_subjects,
        )
        self.assertTrue(
            any("selected root mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_coverage(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_selected_root_certificate_coverage
                .run_fixed_point_selected_root_certificate_coverage_cli(
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
            payload["coverage_set_id"],
            "as-fixed-point-selected-root-certificate-coverage-v1",
        )


if __name__ == "__main__":
    unittest.main()
