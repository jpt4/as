import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_diagonal_instance_closure_frontier_status
from autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_fixed_point_diagonal_instance_closure_frontier_status,
    validate_fixed_point_diagonal_instance_closure_frontier_status,
)


STATUS = Path("claims/fixed_point_diagonal_instance_closure_frontier_status.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTION = Path("claims/diagonal_construction_targets.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
DIAGONAL_INSTANCE_CLOSURE = Path("claims/fixed_point_diagonal_instance_closure.json")
DIAGONAL_CANDIDATE = Path(
    "claims/fixed_point_diagonal_instance_candidate_surface.json"
)


class FixedPointDiagonalInstanceClosureFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_fixed_point_diagonal_instance_closure_frontier_status(
            STATUS
        )

    def test_checked_in_manifest_names_current_frontier_dependencies(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-fixed-point-diagonal-instance-closure-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(self.status.frontier_blocked_by, "diagonal-instance-closure")
        self.assertEqual(
            self.status.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(self.status.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(
            self.status.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTION),
        )
        self.assertEqual(
            self.status.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(
            self.status.diagonal_instance_closure_path,
            str(DIAGONAL_INSTANCE_CLOSURE),
        )
        self.assertEqual(
            self.status.diagonal_instance_candidate_surface_path,
            str(DIAGONAL_CANDIDATE),
        )
        self.assertEqual(
            self.status.required_construction_case_id,
            "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE",
        )
        self.assertEqual(
            self.status.required_construction_case_kind,
            "diagonal-instance-closure",
        )
        self.assertEqual(self.status.required_construction_case_status, "proof-case-open")
        self.assertEqual(self.status.expected_support_surface_count, 5)
        self.assertEqual(self.status.expected_diagonal_instance_code_length, 296)
        self.assertEqual(self.status.expected_diagonal_candidate_count, 1)
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "fixed_point",
                "diagonal_construction",
                "fixed_point_equation_bridge",
                "diagonal_instance_closure",
                "diagonal_instance_candidate_surface",
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

    def test_checked_in_manifest_validates_diagonal_instance_closure_frontier(self):
        report = validate_fixed_point_diagonal_instance_closure_frontier_status(
            self.status
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "diagonal-instance-closure")
        self.assertEqual(
            report.construction_case.case_id,
            "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE",
        )
        self.assertEqual(report.construction_case.case_kind, "diagonal-instance-closure")
        self.assertEqual(report.construction_case.status, "proof-case-open")
        self.assertEqual(
            report.construction_case.required_dependency_subjects,
            REQUIRED_SUPPORT_SUBJECTS,
        )
        self.assertEqual(report.support_surface_count, 5)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))
        self.assertTrue(all(surface.failed_subjects == () for surface in report.support_surfaces))

    def test_json_payload_exposes_compact_frontier_status(self):
        report = validate_fixed_point_diagonal_instance_closure_frontier_status(
            self.status
        )

        payload = (
            fixed_point_diagonal_instance_closure_frontier_status
            .fixed_point_diagonal_instance_closure_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "diagonal-instance-closure")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 5)
        self.assertEqual(
            payload["construction_case"]["case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE",
        )
        self.assertEqual(
            payload["construction_case"]["case_kind"],
            "diagonal-instance-closure",
        )
        self.assertEqual(payload["construction_case"]["status"], "proof-case-open")
        self.assertEqual(
            payload["construction_case"]["required_dependency_subjects"],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(payload["support_facts"]["fixed_point"]["target_count"], 1)
        self.assertEqual(
            payload["support_facts"]["diagonal_construction"]["construction_count"],
            1,
        )
        self.assertEqual(
            payload["support_facts"]["fixed_point_equation_bridge"]["bridge_count"],
            1,
        )
        self.assertEqual(
            payload["support_facts"]["diagonal_instance_closure"]["closure_count"],
            1,
        )
        self.assertEqual(
            payload["support_facts"]["diagonal_instance_closure"][
                "diagonal_instance_code_length"
            ],
            296,
        )
        self.assertTrue(
            payload["support_facts"]["diagonal_instance_closure"][
                "bridge_matches_diagonal_instance"
            ]
        )
        self.assertEqual(
            payload["support_facts"]["diagonal_instance_candidate_surface"][
                "candidate_count"
            ],
            1,
        )
        self.assertTrue(
            payload["support_facts"]["diagonal_instance_candidate_surface"][
                "candidate_matches_closure"
            ]
        )

    def test_text_report_exposes_blocked_diagonal_instance_boundary(self):
        report = validate_fixed_point_diagonal_instance_closure_frontier_status(
            self.status
        )

        text = (
            fixed_point_diagonal_instance_closure_frontier_status
            .format_fixed_point_diagonal_instance_closure_frontier_status_report(
                report
            )
        )

        self.assertIn(
            "Fixed-point diagonal instance closure frontier status: accepted",
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: diagonal-instance-closure", text)
        self.assertIn(
            "Construction case: "
            "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE",
            text,
        )
        self.assertIn("Case kind: diagonal-instance-closure", text)
        self.assertIn("Case status: proof-case-open", text)
        self.assertIn("Support surfaces: 5", text)
        self.assertIn("diagonal_instance_closure: accepted", text)
        self.assertIn("diagonal instance length 296", text)
        self.assertIn("diagonal_instance_candidate_surface: accepted", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("FAIL", text)

    def test_proof_promotion_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_diagonal_instance_closure_frontier_status(
                path
            )

            report = validate_fixed_point_diagonal_instance_closure_frontier_status(
                status
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-frontier-status",
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
            status = load_fixed_point_diagonal_instance_closure_frontier_status(
                path
            )

            report = validate_fixed_point_diagonal_instance_closure_frontier_status(
                status
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(any("missing non-claims" in result.detail for result in report.results))

    def test_empty_non_claims_are_rejected_by_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = []
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_fixed_point_diagonal_instance_closure_frontier_status(path)

    def test_stale_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["diagonal_instance_candidate_surface_path"] = (
                "claims/fixed_point_substitution_witness_bridge.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_diagonal_instance_closure_frontier_status(
                path
            )

            report = validate_fixed_point_diagonal_instance_closure_frontier_status(
                status
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-frontier-dependency",
            report.failed_subjects,
        )

    def test_changed_support_subjects_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["required_dependency_subjects"] = [
                "fixed_point",
                "diagonal_construction",
                "fixed_point_equation_bridge",
                "diagonal_instance_closure",
            ]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_diagonal_instance_closure_frontier_status(
                status_path
            )

            report = validate_fixed_point_diagonal_instance_closure_frontier_status(
                status
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-frontier-support-subject",
            report.failed_subjects,
        )

    def test_closed_diagonal_instance_construction_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["status"] = "diagonal-instance-closure-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_diagonal_instance_closure_frontier_status(
                status_path
            )

            report = validate_fixed_point_diagonal_instance_closure_frontier_status(
                status
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-closure-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("construction case is not open" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_closure_frontier_status
                .run_fixed_point_diagonal_instance_closure_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Fixed-point diagonal instance closure frontier status: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_closure_frontier_status
                .run_fixed_point_diagonal_instance_closure_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_blocked_by"], "diagonal-instance-closure")

    def test_module_execution_runs_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "fixed_point_diagonal_instance_closure_frontier_status"
                ),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point diagonal instance closure frontier status: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "fixed_point_diagonal_instance_closure_frontier_status"
                ),
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
            payload["status_set_id"],
            "as-fixed-point-diagonal-instance-closure-frontier-status-v1",
        )


if __name__ == "__main__":
    unittest.main()
