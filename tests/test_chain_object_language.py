import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import chain_object_language
from autarkic_systems.chain_claims import load_transition_chain_claims
from autarkic_systems.chain_object_language import (
    REQUIRED_CHAIN_SYNTAX_CLASSES,
    load_transition_chain_claim_language,
    validate_chain_claim_surface,
    validate_chain_language_manifest,
)
from autarkic_systems.proof_certificates import CertificateStep, load_proof_certificates


LANGUAGE = Path("language/transition_chain_claim_language.json")
CLAIMS = Path("claims/transition_chain_claims.json")
CERTIFICATES = Path("claims/transition_chain_proof_certificates.json")


class ChainObjectLanguageTests(unittest.TestCase):
    def setUp(self):
        self.language = load_transition_chain_claim_language(LANGUAGE)
        self.claims = load_transition_chain_claims(CLAIMS)
        self.certificates = load_proof_certificates(CERTIFICATES)

    def test_chain_language_manifest_names_required_syntax_classes(self):
        results = validate_chain_language_manifest(self.language)

        self.assertEqual(
            REQUIRED_CHAIN_SYNTAX_CLASSES,
            (
                "terms",
                "chain_formulae",
                "chain_sentences",
                "proof_objects",
                "substrate_chain_claims",
            ),
        )
        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_current_chain_claim_surface_validates_against_language(self):
        results = validate_chain_claim_surface(
            self.language,
            self.claims,
            self.certificates,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_report_formats_successful_chain_language_validation(self):
        report = chain_object_language.validate_transition_chain_claim_language_project(
            language_path=LANGUAGE,
            claims_path=CLAIMS,
            certificates_path=CERTIFICATES,
        )

        text = chain_object_language.format_transition_chain_claim_language_report(
            report
        )

        self.assertIn(
            "Transition chain claim language: as-transition-chain-claim-v1",
            text,
        )
        self.assertIn("OK terms.roles:", text)
        self.assertIn("OK UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED:", text)
        self.assertNotIn("FAIL", text)

    def test_json_payload_records_successful_chain_language_validation(self):
        report = chain_object_language.validate_transition_chain_claim_language_project(
            language_path=LANGUAGE,
            claims_path=CLAIMS,
            certificates_path=CERTIFICATES,
        )

        payload = chain_object_language.transition_chain_claim_language_report_payload(
            report
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["language_id"], "as-transition-chain-claim-v1")
        self.assertEqual(payload["claim_count"], len(self.claims))
        self.assertEqual(payload["certificate_count"], len(self.certificates))
        self.assertEqual(payload["result_count"], len(report.results))
        self.assertTrue(
            any(
                result["subject"] == "proof_objects.rules" and result["accepted"]
                for result in payload["results"]
            )
        )

    def test_cli_returns_zero_for_checked_in_chain_language_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = chain_object_language.run_transition_chain_claim_language_cli(
                [
                    "--language",
                    str(LANGUAGE),
                    "--claims",
                    str(CLAIMS),
                    "--certificates",
                    str(CERTIFICATES),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Transition chain claim language:", output)
        self.assertIn("OK UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED:", output)

    def test_cli_returns_json_for_checked_in_chain_language_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = chain_object_language.run_transition_chain_claim_language_cli(
                [
                    "--language",
                    str(LANGUAGE),
                    "--claims",
                    str(CLAIMS),
                    "--certificates",
                    str(CERTIFICATES),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["claim_count"], len(self.claims))
        self.assertNotIn("OK ", stdout.getvalue())

    def test_cli_returns_one_for_missing_chain_language_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "transition_chain_claim_language.json"
            data = json.loads(LANGUAGE.read_text(encoding="utf-8"))
            del data["syntax_classes"]["chain_formulae"]
            language_path.write_text(json.dumps(data), encoding="utf-8")
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = (
                    chain_object_language.run_transition_chain_claim_language_cli(
                        [
                            "--language",
                            str(language_path),
                            "--claims",
                            str(CLAIMS),
                            "--certificates",
                            str(CERTIFICATES),
                        ]
                    )
                )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn(
            "FAIL chain_formulae: missing syntax class: chain_formulae",
            output,
        )

    def test_module_execution_runs_chain_language_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_object_language",
                "--language",
                str(LANGUAGE),
                "--claims",
                str(CLAIMS),
                "--certificates",
                str(CERTIFICATES),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Transition chain claim language:", completed.stdout)
        self.assertIn(
            "OK UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-CONSUMED:",
            completed.stdout,
        )

    def test_module_execution_runs_json_chain_language_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.chain_object_language",
                "--language",
                str(LANGUAGE),
                "--claims",
                str(CLAIMS),
                "--certificates",
                str(CERTIFICATES),
                "--format",
                "json",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["language_id"], "as-transition-chain-claim-v1")

    def test_unknown_chain_predicate_is_rejected(self):
        bad_claim = self.claims[0].with_checker("not_a_chain_predicate")

        results = validate_chain_claim_surface(
            self.language,
            [bad_claim],
            self.certificates,
        )

        self.assertFalse(results[0].accepted)
        self.assertIn("unknown chain predicate", results[0].detail)

    def test_unknown_proof_rule_is_rejected(self):
        first = self.certificates[0]
        bad_step = CertificateStep(
            rule="not-a-proof-rule",
            example=first.steps[0].example,
            expected=first.steps[0].expected,
        )
        bad_certificate = first.with_steps((bad_step, *first.steps[1:]))

        results = validate_chain_claim_surface(
            self.language,
            self.claims,
            [bad_certificate],
        )

        self.assertTrue(
            any(
                not result.accepted
                and "unknown proof object rule" in result.detail
                for result in results
            ),
            results,
        )

    def test_chain_status_vocabulary_must_cover_evaluated_examples(self):
        terms = dict(self.language.syntax_classes["terms"])
        terms["chain_statuses"] = ["neighbor-delivery-consumed"]
        bad_language = self.language.with_syntax_class("terms", terms)

        results = validate_chain_claim_surface(
            bad_language,
            self.claims,
            self.certificates,
        )

        self.assertFalse(all(result.accepted for result in results))
        self.assertTrue(any("unknown chain status" in result.detail for result in results))


if __name__ == "__main__":
    unittest.main()
