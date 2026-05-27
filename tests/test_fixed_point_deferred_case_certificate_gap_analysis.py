import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_deferred_case_certificate_gap_analysis
from autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis import (
    REQUIRED_DEFERRED_CASE_KINDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_deferred_case_certificate_gap_analysis,
    validate_fixed_point_deferred_case_certificate_gap_analysis,
)


GAP_ANALYSIS = Path("claims/fixed_point_deferred_case_certificate_gap_analysis.json")
READINESS = Path("claims/fixed_point_deferred_case_certificate_readiness.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointDeferredCaseCertificateGapAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.gap_analysis = load_fixed_point_deferred_case_certificate_gap_analysis(
            GAP_ANALYSIS
        )

    def test_checked_in_manifest_names_gap_analysis_input(self):
        self.assertEqual(self.gap_analysis.schema_version, 1)
        self.assertEqual(
            self.gap_analysis.gap_analysis_id,
            "as-fixed-point-deferred-case-certificate-gap-analysis-v1",
        )
        self.assertEqual(
            self.gap_analysis.deferred_case_certificate_readiness_path,
            str(READINESS),
        )
        self.assertEqual(self.gap_analysis.expected_gap_entry_count, 3)
        self.assertEqual(
            self.gap_analysis.expected_deferred_case_kinds,
            REQUIRED_DEFERRED_CASE_KINDS,
        )
        self.assertEqual(
            self.gap_analysis.expected_certificate_gap_counts[
                "substitution-representability-proof"
            ],
            0,
        )
        self.assertEqual(
            self.gap_analysis.expected_missing_certificate_predecessors[
                "bridge-equality-proof"
            ],
            ("substitution-representability-proof",),
        )
        self.assertIn("no bridge equality proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_gap_analysis(self):
        report = validate_fixed_point_deferred_case_certificate_gap_analysis(
            self.gap_analysis,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.gap_entry_count, 3)
        self.assertTrue(all(entry.accepted for entry in report.gap_entries))

    def test_json_payload_exposes_certificate_gaps_and_proof_blockers(self):
        report = validate_fixed_point_deferred_case_certificate_gap_analysis(
            self.gap_analysis,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_deferred_case_certificate_gap_analysis
            .fixed_point_deferred_case_certificate_gap_analysis_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["gap_entry_count"], 3)
        gap_by_kind = {
            entry["deferred_case_kind"]: entry for entry in payload["gap_entries"]
        }
        self.assertEqual(
            gap_by_kind["substitution-representability-proof"][
                "missing_certificate_predecessor_case_kinds"
            ],
            [],
        )
        self.assertEqual(
            gap_by_kind["substitution-representability-proof"][
                "certificate_gap_count"
            ],
            0,
        )
        self.assertEqual(
            gap_by_kind["bridge-equality-proof"][
                "missing_certificate_predecessor_case_kinds"
            ],
            ["substitution-representability-proof"],
        )
        self.assertEqual(
            gap_by_kind["fixed-point-equation-lifting"][
                "missing_certificate_predecessor_case_kinds"
            ],
            ["bridge-equality-proof"],
        )
        self.assertEqual(
            gap_by_kind["bridge-equality-proof"]["open_proof_blocker_count"],
            3,
        )
        self.assertTrue(payload["observed_readiness_accepted"])
        self.assertTrue(payload["observed_proof_boundary_preserved"])

    def test_text_report_exposes_gap_boundary_without_promotion(self):
        report = validate_fixed_point_deferred_case_certificate_gap_analysis(
            self.gap_analysis,
            WILLARD_MAP,
        )

        text = (
            fixed_point_deferred_case_certificate_gap_analysis
            .format_fixed_point_deferred_case_certificate_gap_analysis_report(report)
        )

        self.assertIn("Fixed-point deferred case certificate gap analysis: accepted", text)
        self.assertIn("Gap entries: 3", text)
        self.assertIn("substitution-representability-proof: blocked", text)
        self.assertIn("certificate gaps: 0", text)
        self.assertIn("bridge-equality-proof: blocked", text)
        self.assertIn("missing certificate predecessors: substitution-representability-proof", text)
        self.assertIn("fixed-point-equation-lifting: blocked", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_missing_certificate_predecessor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "gap-analysis.json"
            data = json.loads(GAP_ANALYSIS.read_text(encoding="utf-8"))
            data["expected_missing_certificate_predecessors"][
                "bridge-equality-proof"
            ] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            gap_analysis = load_fixed_point_deferred_case_certificate_gap_analysis(path)

            report = validate_fixed_point_deferred_case_certificate_gap_analysis(
                gap_analysis,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-deferred-case-certificate-gap-analysis-missing-predecessors",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing certificate predecessor mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_gap_analysis(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_deferred_case_certificate_gap_analysis
                .run_fixed_point_deferred_case_certificate_gap_analysis_cli(
                    [
                        "--gap-analysis",
                        str(GAP_ANALYSIS),
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
            payload["gap_analysis_id"],
            "as-fixed-point-deferred-case-certificate-gap-analysis-v1",
        )


if __name__ == "__main__":
    unittest.main()
