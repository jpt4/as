import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_equation_lifting_frontier_status
from autarkic_systems.fixed_point_equation_lifting_frontier_status import (
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_fixed_point_equation_lifting_frontier_status,
    validate_fixed_point_equation_lifting_frontier_status,
)


STATUS = Path("claims/fixed_point_equation_lifting_frontier_status.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
FIXED_POINT_EQUATION_BRIDGE = Path("claims/fixed_point_equation_bridge_targets.json")
CODEBOOK = Path("language/formal_codebook.json")
EQUATION_LIFTING_ALIGNMENT = Path("claims/fixed_point_equation_lifting_alignment.json")


class FixedPointEquationLiftingFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_fixed_point_equation_lifting_frontier_status(STATUS)

    def test_checked_in_manifest_names_equation_lifting_frontier(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-fixed-point-equation-lifting-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(
            self.status.frontier_blocked_by,
            "fixed-point-equation-lifting",
        )
        self.assertEqual(
            self.status.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(self.status.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(
            self.status.fixed_point_equation_bridge_targets_path,
            str(FIXED_POINT_EQUATION_BRIDGE),
        )
        self.assertEqual(self.status.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.status.equation_lifting_alignment_path,
            str(EQUATION_LIFTING_ALIGNMENT),
        )
        self.assertEqual(self.status.expected_support_surface_count, 4)
        self.assertEqual(self.status.expected_direct_target_code_length, 4528)
        self.assertEqual(self.status.expected_bridge_equation_code_length, 4815)
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "fixed_point",
                "fixed_point_equation_bridge",
                "codebook",
                "equation_lifting_alignment",
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

    def test_checked_in_manifest_validates_equation_lifting_frontier_status(self):
        report = validate_fixed_point_equation_lifting_frontier_status(self.status)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "fixed-point-equation-lifting")
        self.assertEqual(
            report.construction_case.case_id,
            "AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING",
        )
        self.assertEqual(
            report.construction_case.case_kind,
            "fixed-point-equation-lifting",
        )
        self.assertEqual(report.construction_case.status, "proof-case-open")
        self.assertEqual(report.support_surface_count, 4)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))
        self.assertTrue(
            all(not surface.failed_subjects for surface in report.support_surfaces)
        )

    def test_json_payload_exposes_compact_frontier_status(self):
        report = validate_fixed_point_equation_lifting_frontier_status(self.status)

        payload = (
            fixed_point_equation_lifting_frontier_status
            .fixed_point_equation_lifting_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-equation-lifting")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 4)
        self.assertEqual(
            payload["construction_case"]["case_id"],
            "AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING",
        )
        self.assertEqual(
            payload["construction_case"]["case_kind"],
            "fixed-point-equation-lifting",
        )
        self.assertEqual(payload["construction_case"]["status"], "proof-case-open")
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            payload["support_facts"]["fixed_point"]["target_count"],
            1,
        )
        self.assertEqual(
            payload["support_facts"]["fixed_point_equation_bridge"][
                "bridge_equation_code_length"
            ],
            4815,
        )
        self.assertEqual(
            payload["support_facts"]["equation_lifting_alignment"][
                "direct_target_code_length"
            ],
            4528,
        )
        self.assertEqual(
            payload["support_facts"]["equation_lifting_alignment"][
                "alignment_count"
            ],
            1,
        )

    def test_text_report_exposes_blocked_equation_lifting_boundary(self):
        report = validate_fixed_point_equation_lifting_frontier_status(self.status)

        text = (
            fixed_point_equation_lifting_frontier_status
            .format_fixed_point_equation_lifting_frontier_status_report(report)
        )

        self.assertIn("Fixed-point equation lifting frontier status: accepted", text)
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: fixed-point-equation-lifting", text)
        self.assertIn(
            "Construction case: AS-FIXED-POINT-CONSTRUCTION-EQUATION-LIFTING",
            text,
        )
        self.assertIn("Case kind: fixed-point-equation-lifting", text)
        self.assertIn("Case status: proof-case-open", text)
        self.assertIn("Support surfaces: 4", text)
        self.assertIn("fixed_point: accepted", text)
        self.assertIn("fixed_point_equation_bridge: accepted", text)
        self.assertIn("bridge equation length 4815", text)
        self.assertIn("equation_lifting_alignment: accepted", text)
        self.assertIn("direct target length 4528", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("FAIL", text)

    def test_proof_promotion_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_equation_lifting_frontier_status(path)

            report = validate_fixed_point_equation_lifting_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("proof-promotion frontier status" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_equation_lifting_frontier_status(path)

            report = validate_fixed_point_equation_lifting_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-frontier-non-claim",
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
                load_fixed_point_equation_lifting_frontier_status(path)

    def test_stale_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["equation_lifting_alignment_path"] = str(Path(tmp) / "alignment.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_equation_lifting_frontier_status(path)

            report = validate_fixed_point_equation_lifting_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-frontier-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "equation_lifting_alignment_path"
                and not result.accepted
                for result in report.results
            )
        )

    def test_closed_equation_lifting_construction_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "fixed-point-equation-lifting":
                    case["status"] = "fixed-point-equation-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_equation_lifting_frontier_status(status_path)

            report = validate_fixed_point_equation_lifting_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("construction case is not open" in result.detail for result in report.results)
        )

    def test_required_support_subject_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "fixed-point-equation-lifting":
                    case["required_dependency_subjects"] = [
                        subject
                        for subject in case["required_dependency_subjects"]
                        if subject != "codebook"
                    ]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_equation_lifting_frontier_status(status_path)

            report = validate_fixed_point_equation_lifting_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-equation-lifting-frontier-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "construction_case.required_dependency_subjects"
                and not result.accepted
                for result in report.results
            )
        )

    def test_cli_returns_zero_for_checked_in_equation_lifting_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_equation_lifting_frontier_status
                .run_fixed_point_equation_lifting_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point equation lifting frontier status: accepted", output)

    def test_cli_returns_json_for_checked_in_equation_lifting_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_equation_lifting_frontier_status
                .run_fixed_point_equation_lifting_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-equation-lifting")

    def test_module_execution_runs_equation_lifting_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_equation_lifting_frontier_status",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point equation lifting frontier status: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_equation_lifting_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_equation_lifting_frontier_status",
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
            "as-fixed-point-equation-lifting-frontier-status-v1",
        )


if __name__ == "__main__":
    unittest.main()
