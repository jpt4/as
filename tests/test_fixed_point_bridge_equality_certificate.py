import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_bridge_equality_certificate
from autarkic_systems.fixed_point_bridge_equality_certificate import (
    REQUIRED_CERTIFICATE_STEP_IDS,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_bridge_equality_certificate,
    validate_fixed_point_bridge_equality_certificate,
)


CERTIFICATE = Path("claims/fixed_point_bridge_equality_certificate.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
BRIDGE_EQUALITY_ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
BRIDGE_EQUALITY_EVALUATION = Path("claims/fixed_point_bridge_equality_evaluation.json")
CODEBOOK = Path("language/formal_codebook.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointBridgeEqualityCertificateTests(unittest.TestCase):
    def setUp(self):
        self.certificate = load_fixed_point_bridge_equality_certificate(CERTIFICATE)

    def test_checked_in_manifest_names_bridge_equality_certificate(self):
        self.assertEqual(self.certificate.schema_version, 1)
        self.assertEqual(
            self.certificate.certificate_set_id,
            "as-fixed-point-bridge-equality-certificate-v1",
        )
        self.assertEqual(
            self.certificate.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.certificate.bridge_equality_alignment_path,
            str(BRIDGE_EQUALITY_ALIGNMENT),
        )
        self.assertEqual(
            self.certificate.bridge_equality_evaluation_path,
            str(BRIDGE_EQUALITY_EVALUATION),
        )
        self.assertEqual(self.certificate.codebook_path, str(CODEBOOK))
        self.assertEqual(self.certificate.expected_certificate_count, 1)
        self.assertEqual(self.certificate.expected_step_ids, REQUIRED_CERTIFICATE_STEP_IDS)
        self.assertEqual(self.certificate.expected_bridge_equation_code_length, 4815)
        self.assertEqual(self.certificate.expected_evaluation_output_code_length, 296)
        self.assertEqual(
            REQUIRED_CERTIFICATE_STEP_IDS,
            (
                "decode-left-formula",
                "decode-self-argument",
                "evaluate-substitution-code",
                "match-witness-output",
                "match-right-quote",
                "bridge-equation-formed",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_bridge_equality_certificate(self):
        report = validate_fixed_point_bridge_equality_certificate(
            self.certificate,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.certificate_count, 1)
        self.assertEqual(report.certificate_step_count, 6)
        self.assertTrue(all(certificate.accepted for certificate in report.certificates))

    def test_json_payload_exposes_checked_certificate_steps(self):
        report = validate_fixed_point_bridge_equality_certificate(
            self.certificate,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_bridge_equality_certificate
            .fixed_point_bridge_equality_certificate_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["certificate_count"], 1)
        self.assertEqual(payload["certificate_step_count"], 6)
        certificate = payload["certificates"][0]
        self.assertEqual(
            certificate["certificate_id"],
            "AS-FIXED-POINT-BRIDGE-EQUALITY-CERTIFICATE",
        )
        self.assertEqual(
            certificate["construction_case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-BRIDGE-EQUALITY",
        )
        self.assertEqual(certificate["target_id"], "AS-FIXED-POINT-SELFCONS1-TARGET")
        self.assertEqual(
            certificate["certificate_status"],
            "accepted-finite-certificate-not-proof",
        )
        self.assertTrue(certificate["accepted"])
        self.assertEqual(certificate["observed_bridge_equation_code_length"], 4815)
        self.assertEqual(certificate["observed_evaluation_output_code_length"], 296)
        self.assertTrue(certificate["observed_evaluation_accepted"])
        self.assertTrue(certificate["observed_alignment_accepted"])
        self.assertTrue(certificate["observed_equation_bridge_formed"])
        self.assertTrue(certificate["all_steps_accepted"])
        self.assertEqual(
            [step["step_id"] for step in certificate["steps"]],
            list(REQUIRED_CERTIFICATE_STEP_IDS),
        )
        self.assertTrue(all(step["accepted"] for step in certificate["steps"]))
        self.assertIn("no bridge equality proof", payload["non_claims"])

    def test_text_report_exposes_non_promotional_certificate_boundary(self):
        report = validate_fixed_point_bridge_equality_certificate(
            self.certificate,
            WILLARD_MAP,
        )

        text = (
            fixed_point_bridge_equality_certificate
            .format_fixed_point_bridge_equality_certificate_report(report)
        )

        self.assertIn("Fixed-point bridge equality certificate: accepted", text)
        self.assertIn("Certificates: 1", text)
        self.assertIn("Certificate steps: 6", text)
        self.assertIn("decode-left-formula: accepted", text)
        self.assertIn("evaluate-substitution-code: accepted", text)
        self.assertIn("bridge-equation-formed: accepted", text)
        self.assertIn("Non-claims: no bridge equality proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_certificate_step_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "certificate.json"
            data = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
            data["expected_step_ids"] = data["expected_step_ids"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            certificate = load_fixed_point_bridge_equality_certificate(path)

            report = validate_fixed_point_bridge_equality_certificate(
                certificate,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-bridge-equality-certificate-steps", report.failed_subjects)
        self.assertTrue(
            any("step id mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "certificate.json"
            data = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            certificate = load_fixed_point_bridge_equality_certificate(path)

            report = validate_fixed_point_bridge_equality_certificate(
                certificate,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-bridge-equality-certificate-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_certificate(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_bridge_equality_certificate
                .run_fixed_point_bridge_equality_certificate_cli(
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
            "as-fixed-point-bridge-equality-certificate-v1",
        )


if __name__ == "__main__":
    unittest.main()
