import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems.network_sequence_demo import (
    build_network_sequence_demo_registry_report,
    build_network_sequence_demo_report,
    format_network_sequence_demo_registry_report,
    format_network_sequence_demo_report,
    run_network_sequence_demo_cli,
)


BUNDLE = Path("evidence/sequences/post_handoff_signal_bundle.json")
REGISTRY = Path("evidence/sequences/manifest.json")
BUNDLE_ID = "post-handoff-signal-sequence-evidence-bundle"
CLAIM_ID = "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED"
LANGUAGE = "language/network_sequence_claim_language.json"
WITNESS = "autarkic_systems/network_sequence.py"


class NetworkSequenceDemoReportTests(unittest.TestCase):
    def test_payload_maps_the_vertical_sequence_evidence_surface(self):
        report = build_network_sequence_demo_report(BUNDLE)

        self.assertTrue(report["accepted"])
        self.assertEqual(report["bundle_id"], BUNDLE_ID)
        self.assertEqual(report["sequence_claim_id"], CLAIM_ID)
        self.assertEqual(report["predicate"], "post_handoff_signal_routed")
        self.assertEqual(
            report["sequence_function"],
            "execute_post_handoff_signal_witness",
        )
        self.assertEqual(report["validation"]["failed_subjects"], [])
        self.assertEqual(report["validation"]["result_count"], 8)
        self.assertEqual(report["missing_evidence_paths"], [])

        layers = {
            (layer["role"], layer["path"])
            for layer in report["evidence_layers"]
        }
        self.assertIn(
            ("sequence-claim-manifest", "claims/network_sequence_claims.json"),
            layers,
        )
        self.assertIn(
            (
                "sequence-proof-certificates",
                "claims/network_sequence_proof_certificates.json",
            ),
            layers,
        )
        self.assertIn(("sequence-language", LANGUAGE), layers)
        self.assertIn(
            (
                "sequence-claim-validator",
                "autarkic_systems/network_sequence_claims.py",
            ),
            layers,
        )
        self.assertIn(("sequence-witness", WITNESS), layers)
        self.assertIn(
            ("chain-bundle", "evidence/chains/neighbor_delivery_chain_bundle.json"),
            layers,
        )
        self.assertIn(
            (
                "source-status",
                "sources/recipient_command_consumption_source_status.json",
            ),
            layers,
        )
        self.assertTrue(all(layer["exists"] for layer in report["evidence_layers"]))
        self.assertGreaterEqual(len(report["boundaries"]), 1)

    def test_payload_reports_missing_evidence_layer_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted_bundle = Path(tmp) / "drifted_sequence_bundle.json"
            data = json.loads(BUNDLE.read_text(encoding="utf-8"))
            missing_path = "sources/missing_sequence_demo_status.json"
            data["artifacts"]["source_statuses"] = [missing_path]
            drifted_bundle.write_text(json.dumps(data), encoding="utf-8")

            report = build_network_sequence_demo_report(drifted_bundle)

        self.assertFalse(report["accepted"])
        self.assertEqual(report["missing_evidence_paths"], [missing_path])
        missing_layers = [
            layer for layer in report["evidence_layers"] if not layer["exists"]
        ]
        self.assertEqual(
            missing_layers,
            [{"role": "source-status", "path": missing_path, "exists": False}],
        )

    def test_text_report_summarizes_claim_validation_and_artifacts(self):
        report = build_network_sequence_demo_report(BUNDLE)

        text = format_network_sequence_demo_report(report)

        self.assertIn(
            "Vertical network sequence demo: "
            "post-handoff-signal-sequence-evidence-bundle",
            text,
        )
        self.assertIn(f"Claim: {CLAIM_ID}", text)
        self.assertIn("Validation: accepted", text)
        self.assertIn(f"Language: {LANGUAGE}", text)
        self.assertIn(f"Sequence witness: {WITNESS}", text)
        self.assertIn("Missing evidence paths: none", text)
        self.assertIn("Chain bundles: 1", text)
        self.assertIn("Source-status boundaries: 5", text)
        self.assertNotIn("FAIL", text)

    def test_json_mode_preserves_failed_subject_summary_for_success(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_sequence_demo_cli(
                ["--bundle", str(BUNDLE), "--format", "json"]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["validation"]["failed_subjects"], [])
        self.assertEqual(payload["missing_evidence_paths"], [])
        self.assertTrue(
            any(
                layer["role"] == "sequence-language"
                and layer["path"] == LANGUAGE
                and layer["exists"]
                for layer in payload["evidence_layers"]
            )
        )

    def test_registry_payload_summarizes_all_sequence_demo_reports(self):
        report = build_network_sequence_demo_registry_report(REGISTRY)

        self.assertTrue(report["accepted"])
        self.assertEqual(
            report["registry_id"],
            "network-sequence-evidence-bundle-registry",
        )
        self.assertEqual(report["bundle_count"], 1)
        self.assertEqual(report["accepted_count"], 1)
        self.assertEqual(report["failed_count"], 0)
        self.assertEqual(report["missing_evidence_paths"], [])
        self.assertEqual(report["validation"]["failed_subjects"], [])
        self.assertEqual(
            [item["bundle_id"] for item in report["bundle_reports"]],
            [BUNDLE_ID],
        )

    def test_registry_text_report_names_registered_sequence_bundle(self):
        report = build_network_sequence_demo_registry_report(REGISTRY)

        text = format_network_sequence_demo_registry_report(report)

        self.assertIn(
            "Vertical network sequence demo registry: "
            "network-sequence-evidence-bundle-registry",
            text,
        )
        self.assertIn("Bundles: 1", text)
        self.assertIn("Accepted: 1", text)
        self.assertIn("Failed: 0", text)
        self.assertIn("Missing evidence paths: none", text)
        self.assertIn(BUNDLE_ID, text)

    def test_registry_json_mode_reports_all_registered_bundles(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_sequence_demo_cli(
                ["--registry", str(REGISTRY), "--format", "json"]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bundle_count"], 1)
        self.assertEqual(
            [item["bundle_id"] for item in payload["bundle_reports"]],
            [BUNDLE_ID],
        )

    def test_registry_json_mode_reports_missing_bundle_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "manifest.json"
            registry_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "registry_id": "drifted-sequence-demo-registry",
                        "reviewed_at": "2026-05-18",
                        "purpose": "Exercise demo registry failure reporting.",
                        "bundles": [
                            {
                                "bundle_id": BUNDLE_ID,
                                "path": "evidence/sequences/missing_bundle.json",
                                "sequence_claim_id": CLAIM_ID,
                                "expected_status": "post-handoff-signal-routed",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()

            with contextlib.redirect_stdout(stdout):
                exit_code = run_network_sequence_demo_cli(
                    ["--registry", str(registry_path), "--format", "json"]
                )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1, payload)
        self.assertFalse(payload["accepted"])
        self.assertEqual(payload["bundle_count"], 1)
        self.assertEqual(payload["accepted_count"], 0)
        self.assertEqual(payload["failed_count"], 1)
        self.assertEqual(
            payload["missing_evidence_paths"],
            ["evidence/sequences/missing_bundle.json"],
        )
        self.assertEqual(payload["bundle_reports"], [])
        self.assertEqual(
            payload["validation"]["failed_subjects"],
            ["registry-bundle-paths", "registry-bundle-validation"],
        )

    def test_module_execution_runs_registry_text_demo_report(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_demo",
                "--registry",
                str(REGISTRY),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Vertical network sequence demo registry:", completed.stdout)
        self.assertIn(BUNDLE_ID, completed.stdout)

    def test_cli_rejects_ambiguous_bundle_and_registry_targets(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_demo",
                "--bundle",
                str(BUNDLE),
                "--registry",
                str(REGISTRY),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 2, completed)
        self.assertIn("not allowed with argument", completed.stderr)

    def test_drifted_bundle_report_exposes_validation_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted_bundle = Path(tmp) / "drifted_sequence_bundle.json"
            data = json.loads(BUNDLE.read_text(encoding="utf-8"))
            data["expected_status"] = "handoff-not-init-consumed"
            drifted_bundle.write_text(json.dumps(data), encoding="utf-8")

            report = build_network_sequence_demo_report(drifted_bundle)

        self.assertFalse(report["accepted"])
        self.assertEqual(
            report["validation"]["failed_subjects"],
            ["sequence-witness"],
        )

    def test_module_execution_runs_text_demo_report(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence_demo",
                "--bundle",
                str(BUNDLE),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Vertical network sequence demo:", completed.stdout)
        self.assertIn("Validation: accepted", completed.stdout)

    def test_module_execution_returns_one_for_drifted_json_demo_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted_bundle = Path(tmp) / "drifted_sequence_bundle.json"
            data = json.loads(BUNDLE.read_text(encoding="utf-8"))
            data["expected_status"] = "handoff-not-init-consumed"
            drifted_bundle.write_text(json.dumps(data), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autarkic_systems.network_sequence_demo",
                    "--bundle",
                    str(drifted_bundle),
                    "--format",
                    "json",
                ],
                check=False,
                cwd=Path.cwd(),
                capture_output=True,
                text=True,
            )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 1, payload)
        self.assertFalse(payload["accepted"])
        self.assertEqual(
            payload["validation"]["failed_subjects"],
            ["sequence-witness"],
        )


if __name__ == "__main__":
    unittest.main()
