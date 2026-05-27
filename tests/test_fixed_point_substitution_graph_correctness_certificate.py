import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_substitution_graph_correctness_certificate
from autarkic_systems.fixed_point_substitution_graph_correctness_certificate import (
    REQUIRED_CERTIFICATE_STEP_IDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_substitution_graph_correctness_certificate,
    validate_fixed_point_substitution_graph_correctness_certificate,
)


CERTIFICATE = Path(
    "claims/fixed_point_substitution_graph_correctness_certificate.json"
)
TARGETS = Path("claims/substitution_graph_correctness_targets.json")
CASES = Path("claims/substitution_graph_correctness_cases.json")
BRIDGE = Path("claims/fixed_point_substitution_graph_correctness_bridge.json")
SELECTOR = Path("claims/fixed_point_frontier_selector.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointSubstitutionGraphCorrectnessCertificateTests(unittest.TestCase):
    def setUp(self):
        self.certificate = (
            load_fixed_point_substitution_graph_correctness_certificate(CERTIFICATE)
        )

    def test_checked_in_manifest_names_graph_correctness_certificate_inputs(self):
        self.assertEqual(self.certificate.schema_version, 1)
        self.assertEqual(
            self.certificate.certificate_set_id,
            "as-fixed-point-substitution-graph-correctness-certificate-v1",
        )
        self.assertEqual(
            self.certificate.substitution_graph_correctness_targets_path,
            str(TARGETS),
        )
        self.assertEqual(
            self.certificate.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(
            self.certificate.substitution_graph_correctness_bridge_path,
            str(BRIDGE),
        )
        self.assertEqual(self.certificate.frontier_selector_path, str(SELECTOR))
        self.assertEqual(self.certificate.expected_certificate_count, 1)
        self.assertEqual(self.certificate.expected_step_ids, REQUIRED_CERTIFICATE_STEP_IDS)
        self.assertEqual(
            self.certificate.expected_selected_case_kind,
            "substitution-graph-correctness-proof",
        )
        self.assertEqual(self.certificate.expected_correctness_case_count, 5)
        self.assertEqual(self.certificate.expected_finite_dependency_count, 5)
        self.assertEqual(
            REQUIRED_CERTIFICATE_STEP_IDS,
            (
                "select-open-root-obligation",
                "accept-correctness-target",
                "accept-correctness-case-rollup",
                "accept-bridge-report",
                "check-correctness-case-count",
                "check-finite-dependency-coverage",
                "preserve-open-proof-boundary",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution graph correctness proof",
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_graph_correctness_certificate(self):
        report = validate_fixed_point_substitution_graph_correctness_certificate(
            self.certificate,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.certificate_count, 1)
        self.assertEqual(report.certificate_step_count, 7)
        self.assertTrue(all(certificate.accepted for certificate in report.certificates))

    def test_json_payload_exposes_checked_certificate_steps(self):
        report = validate_fixed_point_substitution_graph_correctness_certificate(
            self.certificate,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_substitution_graph_correctness_certificate
            .fixed_point_substitution_graph_correctness_certificate_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["certificate_count"], 1)
        self.assertEqual(payload["certificate_step_count"], 7)
        certificate = payload["certificates"][0]
        self.assertEqual(
            certificate["certificate_id"],
            "AS-FIXED-POINT-SUBSTITUTION-GRAPH-CORRECTNESS-CERTIFICATE",
        )
        self.assertEqual(
            certificate["construction_case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS",
        )
        self.assertEqual(
            certificate["selected_case_kind"],
            "substitution-graph-correctness-proof",
        )
        self.assertEqual(
            certificate["certificate_status"],
            "accepted-finite-certificate-not-proof",
        )
        self.assertEqual(certificate["observed_correctness_case_count"], 5)
        self.assertEqual(certificate["observed_finite_dependency_count"], 5)
        self.assertTrue(certificate["observed_selector_accepts_root"])
        self.assertTrue(certificate["observed_correctness_target_accepted"])
        self.assertTrue(certificate["observed_correctness_cases_accepted"])
        self.assertTrue(certificate["observed_bridge_report_accepted"])
        self.assertTrue(certificate["observed_bridge_links_construction_case"])
        self.assertTrue(certificate["observed_proof_boundary_preserved"])
        self.assertTrue(certificate["all_steps_accepted"])
        self.assertTrue(certificate["accepted"])
        self.assertEqual(
            [step["step_id"] for step in certificate["steps"]],
            list(REQUIRED_CERTIFICATE_STEP_IDS),
        )
        self.assertIn("no fixed-point equation proof", payload["non_claims"])

    def test_text_report_exposes_non_promotional_certificate_boundary(self):
        report = validate_fixed_point_substitution_graph_correctness_certificate(
            self.certificate,
            WILLARD_MAP,
        )

        text = (
            fixed_point_substitution_graph_correctness_certificate
            .format_fixed_point_substitution_graph_correctness_certificate_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point substitution graph correctness certificate: accepted",
            text,
        )
        self.assertIn("Certificates: 1", text)
        self.assertIn("Certificate steps: 7", text)
        self.assertIn("select-open-root-obligation: accepted", text)
        self.assertIn("accept-bridge-report: accepted", text)
        self.assertIn("Non-claims: no substitution graph correctness proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_certificate_step_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "certificate.json"
            data = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
            data["expected_step_ids"] = data["expected_step_ids"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            certificate = (
                load_fixed_point_substitution_graph_correctness_certificate(path)
            )

            report = validate_fixed_point_substitution_graph_correctness_certificate(
                certificate,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-certificate-steps",
            report.failed_subjects,
        )
        self.assertTrue(
            any("step id mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_certificate(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_graph_correctness_certificate
                .run_fixed_point_substitution_graph_correctness_certificate_cli(
                    [
                        "--certificate",
                        str(CERTIFICATE),
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
            payload["certificate_set_id"],
            "as-fixed-point-substitution-graph-correctness-certificate-v1",
        )


if __name__ == "__main__":
    unittest.main()
