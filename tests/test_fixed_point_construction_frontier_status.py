import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_construction_frontier_status
from autarkic_systems.fixed_point_construction_frontier_status import (
    REQUIRED_DEPENDENCY_SUBJECTS,
    REQUIRED_NON_CLAIMS,
    SUPPORT_BY_CASE_KIND,
    load_fixed_point_construction_frontier_status,
    validate_fixed_point_construction_frontier_status,
)


STATUS = Path("claims/fixed_point_construction_frontier_status.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
DIAGONAL_CANDIDATE = Path(
    "claims/fixed_point_diagonal_instance_candidate_surface.json"
)
SUBSTITUTION_WITNESS_BRIDGE = Path("claims/fixed_point_substitution_witness_bridge.json")
SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE = Path(
    "claims/fixed_point_substitution_graph_correctness_bridge.json"
)
BRIDGE_EQUALITY_ALIGNMENT = Path("claims/fixed_point_bridge_equality_alignment.json")
BRIDGE_EQUALITY_EVALUATION = Path("claims/fixed_point_bridge_equality_evaluation.json")
EQUATION_LIFTING_ALIGNMENT = Path("claims/fixed_point_equation_lifting_alignment.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
EXPECTED_CASE_STATUS_PATHS = {
    "diagonal-instance-closure": (
        "claims/fixed_point_diagonal_instance_closure_frontier_status.json"
    ),
    "substitution-representability-proof": (
        "claims/fixed_point_substitution_representability_frontier_status.json"
    ),
    "substitution-graph-correctness-proof": (
        "claims/substitution_graph_correctness_frontier_status.json"
    ),
    "bridge-equality-proof": (
        "claims/fixed_point_bridge_equality_frontier_status.json"
    ),
    "fixed-point-equation-lifting": (
        "claims/fixed_point_equation_lifting_frontier_status.json"
    ),
}
EXPECTED_CASE_STATUS_BLOCKERS = {
    "diagonal-instance-closure": "diagonal-instance-closure",
    "substitution-representability-proof": "substitution-representability-proof",
    "substitution-graph-correctness-proof": "substitution-graph-correctness",
    "bridge-equality-proof": "bridge-equality-proof",
    "fixed-point-equation-lifting": "fixed-point-equation-lifting",
}


class FixedPointConstructionFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_fixed_point_construction_frontier_status(STATUS)

    def test_checked_in_manifest_names_current_frontier_dependencies(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-fixed-point-construction-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(self.status.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(
            self.status.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.status.diagonal_instance_candidate_surface_path,
            str(DIAGONAL_CANDIDATE),
        )
        self.assertEqual(
            self.status.substitution_witness_bridge_path,
            str(SUBSTITUTION_WITNESS_BRIDGE),
        )
        self.assertEqual(
            self.status.substitution_graph_correctness_bridge_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_BRIDGE),
        )
        self.assertEqual(
            self.status.bridge_equality_alignment_path,
            str(BRIDGE_EQUALITY_ALIGNMENT),
        )
        self.assertEqual(
            self.status.bridge_equality_evaluation_path,
            str(BRIDGE_EQUALITY_EVALUATION),
        )
        self.assertEqual(
            self.status.equation_lifting_alignment_path,
            str(EQUATION_LIFTING_ALIGNMENT),
        )
        self.assertEqual(self.status.case_status_paths, EXPECTED_CASE_STATUS_PATHS)
        self.assertEqual(
            REQUIRED_DEPENDENCY_SUBJECTS,
            (
                "fixed_point_construction_cases",
                "diagonal_instance_candidate_surface",
                "substitution_witness_bridge",
                "substitution_graph_correctness_bridge",
                "bridge_equality_alignment",
                "bridge_equality_evaluation",
                "equation_lifting_alignment",
            ),
        )
        self.assertEqual(
            SUPPORT_BY_CASE_KIND["diagonal-instance-closure"],
            ("diagonal_instance_candidate_surface",),
        )
        self.assertEqual(
            SUPPORT_BY_CASE_KIND["bridge-equality-proof"],
            ("bridge_equality_alignment", "bridge_equality_evaluation"),
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
        report = validate_fixed_point_construction_frontier_status(
            self.status,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(report.case_count, 5)
        self.assertEqual(report.open_case_count, 5)
        self.assertEqual(report.support_surface_count, 7)
        self.assertEqual(report.case_status_count, 5)
        self.assertEqual(report.accepted_case_status_count, 5)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))
        self.assertTrue(all(status.accepted for status in report.case_status_rollup))
        self.assertEqual(
            tuple(case.status for case in report.case_supports),
            ("proof-case-open",) * 5,
        )
        self.assertEqual(
            tuple(status.case_kind for status in report.case_status_rollup),
            tuple(EXPECTED_CASE_STATUS_PATHS),
        )
        self.assertEqual(
            {
                status.case_kind: status.frontier_blocked_by
                for status in report.case_status_rollup
            },
            EXPECTED_CASE_STATUS_BLOCKERS,
        )
        self.assertEqual(
            tuple(status.construction_case_status for status in report.case_status_rollup),
            ("proof-case-open",) * 5,
        )

    def test_json_payload_exposes_per_case_finite_support_and_status_rollup(self):
        report = validate_fixed_point_construction_frontier_status(
            self.status,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_construction_frontier_status
            .fixed_point_construction_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-construction")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 7)
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["open_case_count"], 5)
        self.assertEqual(payload["case_status_count"], 5)
        self.assertEqual(payload["accepted_case_status_count"], 5)
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_DEPENDENCY_SUBJECTS),
        )
        self.assertTrue(
            all(surface["accepted"] for surface in payload["support_surfaces"])
        )

        supports = {
            case["case_kind"]: case["finite_support_subjects"]
            for case in payload["case_supports"]
        }
        self.assertEqual(
            supports["diagonal-instance-closure"],
            ["diagonal_instance_candidate_surface"],
        )
        self.assertEqual(
            supports["substitution-representability-proof"],
            ["substitution_witness_bridge"],
        )
        self.assertEqual(
            supports["substitution-graph-correctness-proof"],
            ["substitution_graph_correctness_bridge"],
        )
        self.assertEqual(
            supports["bridge-equality-proof"],
            ["bridge_equality_alignment", "bridge_equality_evaluation"],
        )
        self.assertEqual(
            supports["fixed-point-equation-lifting"],
            ["equation_lifting_alignment"],
        )
        rollup = {
            status["case_kind"]: status
            for status in payload["case_status_rollup"]
        }
        self.assertEqual(set(rollup), set(EXPECTED_CASE_STATUS_PATHS))
        for case_kind, expected_path in EXPECTED_CASE_STATUS_PATHS.items():
            self.assertTrue(rollup[case_kind]["accepted"])
            self.assertEqual(rollup[case_kind]["path"], expected_path)
            self.assertEqual(rollup[case_kind]["frontier_status"], "blocked")
            self.assertEqual(
                rollup[case_kind]["expected_frontier_blocker"],
                EXPECTED_CASE_STATUS_BLOCKERS[case_kind],
            )
            self.assertEqual(
                rollup[case_kind]["frontier_blocked_by"],
                EXPECTED_CASE_STATUS_BLOCKERS[case_kind],
            )
            self.assertEqual(
                rollup[case_kind]["construction_case_status"],
                "proof-case-open",
            )
            self.assertEqual(rollup[case_kind]["failed_subjects"], [])

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_fixed_point_construction_frontier_status(
            self.status,
            WILLARD_MAP,
        )

        text = (
            fixed_point_construction_frontier_status
            .format_fixed_point_construction_frontier_status_report(report)
        )

        self.assertIn("Fixed-point construction frontier status: accepted", text)
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: fixed-point-construction", text)
        self.assertIn("Open construction cases: 5/5", text)
        self.assertIn("Support surfaces: 7", text)
        self.assertIn("Compact construction-case status rollup: 5/5", text)
        self.assertIn(
            "- substitution-graph-correctness-proof: accepted "
            "(claims/substitution_graph_correctness_frontier_status.json)",
            text,
        )
        self.assertIn("Expected blocker: substitution-graph-correctness", text)
        self.assertIn("bridge-equality-proof", text)
        self.assertIn(
            "Finite support: bridge_equality_alignment, bridge_equality_evaluation",
            text,
        )
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("FAIL", text)

    def test_overclaiming_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "fixed-point-equation-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("overclaiming frontier status" in result.detail for result in report.results)
        )

    def test_construction_case_not_open_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            case_data["cases"][4]["status"] = "fixed-point-equation-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["fixed_point_construction_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(status_path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("construction case is not open" in result.detail for result in report.results)
        )

    def test_missing_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["bridge_equality_evaluation_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "bridge_equality_evaluation"
                and not result.accepted
                and "fixed-point-bridge-equality-evaluation-load" in result.detail
                for result in report.results
            )
        )

    def test_missing_compact_case_status_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["case_status_paths"].pop("bridge-equality-proof")
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing case-status paths" in result.detail for result in report.results)
        )

    def test_compact_case_status_blocker_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            compact_path = Path(tmp) / "substitution_graph_status.json"
            compact_data = json.loads(
                Path(
                    EXPECTED_CASE_STATUS_PATHS[
                        "substitution-graph-correctness-proof"
                    ]
                ).read_text(encoding="utf-8")
            )
            compact_data["frontier_blocked_by"] = "substitution-graph-correctness-proof"
            compact_path.write_text(json.dumps(compact_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"][
                "substitution-graph-correctness-proof"
            ] = str(compact_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(status_path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "expected substitution-graph-correctness blocker" in result.detail
                for result in report.results
            )
        )

    def test_closed_compact_construction_case_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CONSTRUCTION_CASES.read_text(encoding="utf-8"))
            case_data["cases"][1]["status"] = "fixed-point-equation-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            compact_path = Path(tmp) / "substitution_status.json"
            compact_data = json.loads(
                Path(
                    EXPECTED_CASE_STATUS_PATHS[
                        "substitution-representability-proof"
                    ]
                ).read_text(encoding="utf-8")
            )
            compact_data["fixed_point_construction_cases_path"] = str(case_path)
            compact_path.write_text(json.dumps(compact_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"][
                "substitution-representability-proof"
            ] = str(compact_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(status_path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any("expected proof-case-open" in result.detail for result in report.results)
        )

    def test_unaccepted_compact_case_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            compact_path = Path(tmp) / "bridge_status.json"
            compact_data = json.loads(
                Path(
                    EXPECTED_CASE_STATUS_PATHS["bridge-equality-proof"]
                ).read_text(encoding="utf-8")
            )
            compact_data["non_claims"] = compact_data["non_claims"][:-1]
            compact_path.write_text(json.dumps(compact_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"]["bridge-equality-proof"] = str(
                compact_path
            )
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(status_path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "case status validator rejected" in result.detail
                for result in report.results
            )
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_fixed_point_construction_frontier_status(path)

            report = validate_fixed_point_construction_frontier_status(
                status,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_construction_frontier_status
                .run_fixed_point_construction_frontier_status_cli(
                    [
                        "--status",
                        str(STATUS),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Fixed-point construction frontier status: accepted", output)

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_construction_frontier_status
                .run_fixed_point_construction_frontier_status_cli(
                    [
                        "--status",
                        str(STATUS),
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
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-construction")
        self.assertEqual(payload["case_status_count"], 5)

    def test_module_execution_runs_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_construction_frontier_status",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point construction frontier status: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_frontier_status_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_construction_frontier_status",
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
            "as-fixed-point-construction-frontier-status-v1",
        )
        self.assertEqual(payload["case_status_count"], 5)


if __name__ == "__main__":
    unittest.main()
