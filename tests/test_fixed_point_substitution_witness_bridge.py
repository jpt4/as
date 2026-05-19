import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_substitution_witness_bridge
from autarkic_systems.fixed_point_substitution_witness_bridge import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_fixed_point_substitution_witness_bridge,
    validate_fixed_point_substitution_witness_bridge,
)


BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")
SUBSTITUTION_GRAPH_CORRECTNESS_CASES = Path("claims/substitution_graph_correctness_cases.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
DIAGONAL_INSTANCE_CLOSURE = Path("claims/fixed_point_diagonal_instance_closure.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointSubstitutionWitnessBridgeTests(unittest.TestCase):
    def setUp(self):
        self.bridge = load_fixed_point_substitution_witness_bridge(BRIDGE)

    def test_checked_in_manifest_names_witness_bridge_domain(self):
        self.assertEqual(self.bridge.schema_version, 1)
        self.assertEqual(
            self.bridge.bridge_set_id,
            "as-fixed-point-substitution-witness-bridge-v1",
        )
        self.assertEqual(self.bridge.formal_language_path, str(LANGUAGE))
        self.assertEqual(self.bridge.codebook_path, str(CODEBOOK))
        self.assertEqual(self.bridge.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(
            self.bridge.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(
            self.bridge.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            self.bridge.substitution_graph_correctness_cases_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_CASES),
        )
        self.assertEqual(
            self.bridge.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.bridge.diagonal_instance_closure_path,
            str(DIAGONAL_INSTANCE_CLOSURE),
        )
        self.assertEqual(self.bridge.expected_bridge_count, 1)
        self.assertEqual(self.bridge.expected_witness_output_code_length, 296)
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("substitution-witness-bridge",))
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution representability proof",
                "no substitution graph correctness proof",
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_witness_bridge_domain(self):
        report = validate_fixed_point_substitution_witness_bridge(
            self.bridge,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.bridge_count, 1)
        self.assertEqual(report.source_kind_counts["substitution-witness-bridge"], 1)

    def test_json_payload_exposes_witness_bridge_point(self):
        report = validate_fixed_point_substitution_witness_bridge(
            self.bridge,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_substitution_witness_bridge
            .fixed_point_substitution_witness_bridge_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bridge_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        bridge = payload["bridges"][0]
        self.assertEqual(
            bridge["bridge_id"],
            "AS-FIXED-POINT-SUBSTITUTION-WITNESS-BRIDGE",
        )
        self.assertTrue(bridge["observed_route_ids_match"])
        self.assertTrue(bridge["observed_self_application_inputs_match"])
        self.assertTrue(bridge["observed_seed_code_matches_witness_formula"])
        self.assertTrue(bridge["observed_witness_output_matches_diagonal_instance"])
        self.assertTrue(bridge["observed_bridge_observation_matches_witness"])
        self.assertTrue(bridge["observed_closure_observation_matches_bridge"])
        self.assertTrue(bridge["observed_correctness_cases_accepted"])

    def test_text_report_exposes_witness_bridge_boundary(self):
        report = validate_fixed_point_substitution_witness_bridge(
            self.bridge,
            WILLARD_MAP,
        )

        text = (
            fixed_point_substitution_witness_bridge
            .format_fixed_point_substitution_witness_bridge_report(report)
        )

        self.assertIn("Fixed-point substitution witness bridge: accepted", text)
        self.assertIn("Witness bridges: 1", text)
        self.assertIn("substitution-witness-bridge=1", text)
        self.assertIn("Bridge failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_bridge_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridge.json"
            data = json.loads(BRIDGE.read_text(encoding="utf-8"))
            data["expected_bridge_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            bridge = load_fixed_point_substitution_witness_bridge(path)

            report = validate_fixed_point_substitution_witness_bridge(
                bridge,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-witness-bridge-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("bridge count mismatch" in result.detail for result in report.results)
        )

    def test_stale_witness_output_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridge.json"
            data = json.loads(BRIDGE.read_text(encoding="utf-8"))
            data["expected_witness_output_code_length"] = 297
            path.write_text(json.dumps(data), encoding="utf-8")
            bridge = load_fixed_point_substitution_witness_bridge(path)

            report = validate_fixed_point_substitution_witness_bridge(
                bridge,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-witness-bridge-length",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "witness output length mismatch" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridge.json"
            data = json.loads(BRIDGE.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            bridge = load_fixed_point_substitution_witness_bridge(path)

            report = validate_fixed_point_substitution_witness_bridge(
                bridge,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-witness-bridge-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_witness_bridge_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_witness_bridge
                .run_fixed_point_substitution_witness_bridge_cli(
                    [
                        "--bridge",
                        str(BRIDGE),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point substitution witness bridge: accepted", output)

    def test_cli_returns_json_for_checked_in_witness_bridge_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_witness_bridge
                .run_fixed_point_substitution_witness_bridge_cli(
                    [
                        "--bridge",
                        str(BRIDGE),
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
        self.assertEqual(payload["bridge_count"], 1)

    def test_module_execution_runs_witness_bridge_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point_substitution_witness_bridge"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Fixed-point substitution witness bridge: accepted", completed.stdout)

    def test_module_execution_runs_json_witness_bridge_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_substitution_witness_bridge",
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
        self.assertEqual(
            payload["bridge_set_id"],
            "as-fixed-point-substitution-witness-bridge-v1",
        )


if __name__ == "__main__":
    unittest.main()
