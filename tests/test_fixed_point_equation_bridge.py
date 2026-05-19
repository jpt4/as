import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_equation_bridge
from autarkic_systems.fixed_point_equation_bridge import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)


BRIDGES = Path("claims/fixed_point_equation_bridge_targets.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")
SUBSTITUTION_GRAPH_CASES = Path("claims/substitution_graph_correctness_cases.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointEquationBridgeTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_fixed_point_equation_bridge_targets(BRIDGES)

    def test_checked_in_manifest_names_bridge_target(self):
        bridge = self.manifest.bridges[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.bridge_set_id,
            "as-fixed-point-equation-bridge-v1",
        )
        self.assertEqual(
            self.manifest.fixed_point_targets_path,
            str(FIXED_POINT_TARGETS),
        )
        self.assertEqual(
            self.manifest.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(
            self.manifest.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            self.manifest.substitution_graph_correctness_cases_path,
            str(SUBSTITUTION_GRAPH_CASES),
        )
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(
            bridge.bridge_id,
            "AS-FIXED-POINT-SELFCONS1-DIAGONAL-EQUATION-BRIDGE",
        )
        self.assertEqual(bridge.status, "bridge-target-open")
        self.assertEqual(bridge.expected_diagonal_instance_code_length, 296)
        self.assertEqual(bridge.expected_direct_target_code_length, 4528)
        self.assertEqual(bridge.expected_bridge_equation_code_length, 4815)
        self.assertEqual(bridge.expected_bridge_left_term_code_length, 291)
        self.assertEqual(bridge.expected_bridge_right_term_code_length, 4523)
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "substitution-representability-proof",
                "substitution-graph-correctness-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution representability proof",
                "no substitution graph correctness proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_bridge_target(self):
        report = validate_fixed_point_equation_bridge_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.bridge_count, 1)
        self.assertTrue(
            any(
                result.subject == "bridges"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_bridge_observation(self):
        report = validate_fixed_point_equation_bridge_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = fixed_point_equation_bridge.fixed_point_equation_bridge_payload(
            report
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bridge_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        bridge = payload["bridges"][0]
        self.assertEqual(
            bridge["bridge_id"],
            "AS-FIXED-POINT-SELFCONS1-DIAGONAL-EQUATION-BRIDGE",
        )
        self.assertEqual(bridge["observed_diagonal_instance_code_length"], 296)
        self.assertEqual(bridge["observed_direct_target_code_length"], 4528)
        self.assertEqual(bridge["observed_bridge_equation_code_length"], 4815)
        self.assertTrue(bridge["observed_target_skeleton_matches"])
        self.assertTrue(bridge["observed_diagonal_slot_is_substitution_code"])
        self.assertTrue(bridge["observed_direct_slot_quotes_diagonal_instance"])
        self.assertTrue(bridge["observed_witness_output_matches_diagonal"])
        self.assertFalse(bridge["observed_diagonal_equals_direct_target"])

    def test_text_report_exposes_bridge_boundary(self):
        report = validate_fixed_point_equation_bridge_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = fixed_point_equation_bridge.format_fixed_point_equation_bridge_report(
            report
        )

        self.assertIn("Fixed-point equation bridge targets: accepted", text)
        self.assertIn(
            "AS-FIXED-POINT-SELFCONS1-DIAGONAL-EQUATION-BRIDGE",
            text,
        )
        self.assertIn("Diagonal instance length: 296", text)
        self.assertIn("Direct target length: 4528", text)
        self.assertIn("Bridge equation length: 4815", text)
        self.assertNotIn("FAIL", text)

    def test_stale_bridge_equation_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridges.json"
            data = json.loads(BRIDGES.read_text(encoding="utf-8"))
            data["bridges"][0]["expected_bridge_equation_code_length"] = 7
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_bridge_targets(path)

            report = validate_fixed_point_equation_bridge_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-bridge-length", report.failed_subjects)
        self.assertTrue(
            any("bridge equation length mismatch" in result.detail for result in report.results)
        )

    def test_proved_bridge_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridges.json"
            data = json.loads(BRIDGES.read_text(encoding="utf-8"))
            data["bridges"][0]["status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_bridge_targets(path)

            report = validate_fixed_point_equation_bridge_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-bridge-status", report.failed_subjects)
        self.assertTrue(
            any("proved fixed-point equation bridges are not supported" in result.detail for result in report.results)
        )

    def test_missing_diagonal_construction_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridges.json"
            data = json.loads(BRIDGES.read_text(encoding="utf-8"))
            data["diagonal_construction_targets_path"] = (
                "claims/missing_diagonal_construction_targets.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_fixed_point_equation_bridge_targets(path)

            report = validate_fixed_point_equation_bridge_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-equation-bridge-dependency", report.failed_subjects)
        self.assertTrue(
            any("diagonal construction rejected" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_bridge_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_equation_bridge.run_fixed_point_equation_bridge_cli(
                    [
                        "--bridges",
                        str(BRIDGES),
                        "--language",
                        str(LANGUAGE),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point equation bridge targets: accepted", output)

    def test_cli_returns_json_for_checked_in_bridge_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_equation_bridge.run_fixed_point_equation_bridge_cli(
                    [
                        "--bridges",
                        str(BRIDGES),
                        "--language",
                        str(LANGUAGE),
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

    def test_module_execution_runs_bridge_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.fixed_point_equation_bridge"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point equation bridge targets: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_bridge_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_equation_bridge",
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
            "as-fixed-point-equation-bridge-v1",
        )


if __name__ == "__main__":
    unittest.main()
