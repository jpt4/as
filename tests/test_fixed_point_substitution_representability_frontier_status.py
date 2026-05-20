import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_substitution_representability_frontier_status
from autarkic_systems.fixed_point_substitution_representability_frontier_status import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_fixed_point_substitution_representability_frontier_status,
    validate_fixed_point_substitution_representability_frontier_status,
)


STATUS = Path("claims/fixed_point_substitution_representability_frontier_status.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
SUBSTITUTION_REPRESENTABILITY = Path("claims/substitution_representability_targets.json")
SUBSTITUTION_GRAPH_CORRECTNESS_CASES = Path(
    "claims/substitution_graph_correctness_cases.json"
)
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
SUBSTITUTION_WITNESS_BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")


class FixedPointSubstitutionRepresentabilityFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_fixed_point_substitution_representability_frontier_status(
            STATUS
        )

    def test_checked_in_manifest_names_current_frontier_dependencies(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-fixed-point-substitution-representability-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(
            self.status.frontier_blocked_by,
            "substitution-representability-proof",
        )
        self.assertEqual(
            self.status.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.status.substitution_representability_targets_path,
            str(SUBSTITUTION_REPRESENTABILITY),
        )
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_CASES),
        )
        self.assertEqual(
            self.status.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.status.substitution_witness_bridge_path,
            str(SUBSTITUTION_WITNESS_BRIDGE),
        )
        self.assertEqual(self.status.expected_support_surface_count, 5)
        self.assertEqual(self.status.expected_substitution_witness_bridge_count, 1)
        self.assertEqual(self.status.expected_witness_output_code_length, 296)
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "fixed_point_construction_cases",
                "substitution_representability_target",
                "substitution_graph_correctness_cases",
                "fixed_point_equation_bridge",
                "substitution_witness_bridge",
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

    def test_checked_in_manifest_validates_frontier_status(self):
        report = validate_fixed_point_substitution_representability_frontier_status(
            self.status
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(
            report.frontier_blocked_by,
            "substitution-representability-proof",
        )
        self.assertEqual(
            report.construction_case_id,
            "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY",
        )
        self.assertEqual(
            report.construction_case_kind,
            "substitution-representability-proof",
        )
        self.assertEqual(report.construction_case_status, "proof-case-open")
        self.assertEqual(report.support_surface_count, 5)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))

    def test_json_payload_exposes_compact_frontier_summary(self):
        report = validate_fixed_point_substitution_representability_frontier_status(
            self.status
        )

        payload = (
            fixed_point_substitution_representability_frontier_status
            .fixed_point_substitution_representability_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(
            payload["frontier_blocked_by"],
            "substitution-representability-proof",
        )
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 5)
        self.assertEqual(
            payload["construction_case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY",
        )
        self.assertEqual(
            payload["construction_case_kind"],
            "substitution-representability-proof",
        )
        self.assertEqual(payload["construction_case_status"], "proof-case-open")
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )

    def test_witness_bridge_surface_is_accepted_and_non_promotional(self):
        report = validate_fixed_point_substitution_representability_frontier_status(
            self.status
        )

        witness_surface = {
            surface.subject: surface for surface in report.support_surfaces
        }["substitution_witness_bridge"]

        self.assertTrue(witness_surface.accepted)
        self.assertEqual(
            witness_surface.facts["bridge_set_id"],
            "as-fixed-point-substitution-witness-bridge-v1",
        )
        self.assertEqual(witness_surface.facts["expected_bridge_count"], 1)
        self.assertEqual(
            witness_surface.facts["expected_witness_output_code_length"],
            296,
        )
        self.assertGreaterEqual(witness_surface.facts["non_claim_count"], 6)

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_fixed_point_substitution_representability_frontier_status(
            self.status
        )

        text = (
            fixed_point_substitution_representability_frontier_status
            .format_fixed_point_substitution_representability_frontier_status_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point substitution representability frontier status: accepted",
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: substitution-representability-proof", text)
        self.assertIn(
            "Construction case: "
            "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY",
            text,
        )
        self.assertIn("Kind: substitution-representability-proof", text)
        self.assertIn("Status: proof-case-open", text)
        self.assertIn("Support surfaces: 5", text)
        self.assertIn("Failed subjects: none", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("FAIL", text)

    def test_proof_promotion_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "substitution-representability-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_substitution_representability_frontier_status(
                path
            )

            report = (
                validate_fixed_point_substitution_representability_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-representability-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "proof-promotion frontier status" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_substitution_representability_frontier_status(
                path
            )

            report = (
                validate_fixed_point_substitution_representability_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-representability-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_stale_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["substitution_witness_bridge_path"] = (
                "claims/fixed_point_substitution_graph_correctness_bridge.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_substitution_representability_frontier_status(
                path
            )

            report = (
                validate_fixed_point_substitution_representability_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-representability-frontier-dependency",
            report.failed_subjects,
        )

    def test_closed_construction_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            case_data["cases"][1]["status"] = "substitution-representability-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_substitution_representability_frontier_status(
                status_path
            )

            report = (
                validate_fixed_point_substitution_representability_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-representability-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("construction case is not open" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_representability_frontier_status
                .run_fixed_point_substitution_representability_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Fixed-point substitution representability frontier status: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_representability_frontier_status
                .run_fixed_point_substitution_representability_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["frontier_blocked_by"],
            "substitution-representability-proof",
        )

    def test_module_execution_runs_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "fixed_point_substitution_representability_frontier_status"
                ),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point substitution representability frontier status: accepted",
            completed.stdout,
        )


if __name__ == "__main__":
    unittest.main()
