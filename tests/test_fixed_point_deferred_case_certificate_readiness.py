import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_deferred_case_certificate_readiness
from autarkic_systems.fixed_point_deferred_case_certificate_readiness import (
    REQUIRED_DEFERRED_CASE_KINDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_deferred_case_certificate_readiness,
    validate_fixed_point_deferred_case_certificate_readiness,
)


READINESS = Path("claims/fixed_point_deferred_case_certificate_readiness.json")
GRAPH = Path("claims/fixed_point_construction_obligation_graph.json")
SELECTOR = Path("claims/fixed_point_frontier_selector.json")
COVERAGE = Path("claims/fixed_point_selected_root_certificate_coverage.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointDeferredCaseCertificateReadinessTests(unittest.TestCase):
    def setUp(self):
        self.readiness = load_fixed_point_deferred_case_certificate_readiness(
            READINESS
        )

    def test_checked_in_manifest_names_deferred_readiness_inputs(self):
        self.assertEqual(self.readiness.schema_version, 1)
        self.assertEqual(
            self.readiness.readiness_set_id,
            "as-fixed-point-deferred-case-certificate-readiness-v1",
        )
        self.assertEqual(self.readiness.obligation_graph_path, str(GRAPH))
        self.assertEqual(self.readiness.frontier_selector_path, str(SELECTOR))
        self.assertEqual(
            self.readiness.selected_root_certificate_coverage_path,
            str(COVERAGE),
        )
        self.assertEqual(self.readiness.expected_deferred_case_count, 3)
        self.assertEqual(
            self.readiness.expected_deferred_case_kinds,
            REQUIRED_DEFERRED_CASE_KINDS,
        )
        self.assertEqual(
            self.readiness.expected_predecessor_counts[
                "substitution-representability-proof"
            ],
            2,
        )
        self.assertEqual(
            self.readiness.expected_predecessor_counts["bridge-equality-proof"],
            3,
        )
        self.assertEqual(
            self.readiness.expected_certificate_covered_predecessor_counts[
                "fixed-point-equation-lifting"
            ],
            0,
        )
        self.assertIn("no fixed-point equation proof", REQUIRED_NON_CLAIMS)
        self.assertIn("no self-consistency theorem", REQUIRED_NON_CLAIMS)

    def test_checked_in_manifest_validates_deferred_case_readiness(self):
        report = validate_fixed_point_deferred_case_certificate_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.readiness_count, 3)
        self.assertTrue(all(entry.accepted for entry in report.readiness_entries))

    def test_json_payload_exposes_deferred_case_readiness(self):
        report = validate_fixed_point_deferred_case_certificate_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_deferred_case_certificate_readiness
            .fixed_point_deferred_case_certificate_readiness_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["readiness_count"], 3)
        self.assertEqual(
            payload["deferred_case_kinds"],
            list(REQUIRED_DEFERRED_CASE_KINDS),
        )
        readiness_by_kind = {
            entry["deferred_case_kind"]: entry
            for entry in payload["readiness_entries"]
        }
        self.assertEqual(
            readiness_by_kind["substitution-representability-proof"][
                "predecessor_case_kinds"
            ],
            [
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertEqual(
            readiness_by_kind["substitution-representability-proof"][
                "certificate_covered_predecessor_case_kinds"
            ],
            [
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertEqual(
            readiness_by_kind["bridge-equality-proof"]["predecessor_count"],
            3,
        )
        self.assertEqual(
            readiness_by_kind["bridge-equality-proof"][
                "certificate_covered_predecessor_count"
            ],
            2,
        )
        self.assertEqual(
            readiness_by_kind["fixed-point-equation-lifting"][
                "blocking_open_predecessor_case_kinds"
            ],
            ["bridge-equality-proof"],
        )
        self.assertTrue(payload["observed_selected_root_coverage_accepted"])
        self.assertIn("no bridge equality proof", payload["non_claims"])

    def test_text_report_exposes_deferred_boundary_without_promotion(self):
        report = validate_fixed_point_deferred_case_certificate_readiness(
            self.readiness,
            WILLARD_MAP,
        )

        text = (
            fixed_point_deferred_case_certificate_readiness
            .format_fixed_point_deferred_case_certificate_readiness_report(report)
        )

        self.assertIn("Fixed-point deferred case certificate readiness: accepted", text)
        self.assertIn("Deferred readiness entries: 3", text)
        self.assertIn("substitution-representability-proof: deferred", text)
        self.assertIn("bridge-equality-proof: deferred", text)
        self.assertIn("fixed-point-equation-lifting: deferred", text)
        self.assertIn("covered predecessors: 2/2", text)
        self.assertIn("covered predecessors: 0/1", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_predecessor_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "readiness.json"
            data = json.loads(READINESS.read_text(encoding="utf-8"))
            data["expected_predecessor_counts"][
                "bridge-equality-proof"
            ] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            readiness = load_fixed_point_deferred_case_certificate_readiness(path)

            report = validate_fixed_point_deferred_case_certificate_readiness(
                readiness,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-deferred-case-certificate-readiness-predecessors",
            report.failed_subjects,
        )
        self.assertTrue(
            any("predecessor count mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_readiness(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_deferred_case_certificate_readiness
                .run_fixed_point_deferred_case_certificate_readiness_cli(
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
            payload["readiness_set_id"],
            "as-fixed-point-deferred-case-certificate-readiness-v1",
        )


if __name__ == "__main__":
    unittest.main()
