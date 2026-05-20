import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_diagonal_instance_candidate_surface
from autarkic_systems.fixed_point_diagonal_instance_candidate_surface import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_fixed_point_diagonal_instance_candidate_surface,
    validate_fixed_point_diagonal_instance_candidate_surface,
)


CANDIDATE_SURFACE = Path(
    "claims/fixed_point_diagonal_instance_candidate_surface.json"
)
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
DIAGONAL_CONSTRUCTIONS = Path("claims/diagonal_construction_targets.json")
BRIDGES = Path("claims/fixed_point_equation_bridge_targets.json")
DIAGONAL_INSTANCE_CLOSURE = Path("claims/fixed_point_diagonal_instance_closure.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointDiagonalInstanceCandidateSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.surface = load_fixed_point_diagonal_instance_candidate_surface(
            CANDIDATE_SURFACE
        )

    def test_checked_in_manifest_names_candidate_surface_domain(self):
        self.assertEqual(self.surface.schema_version, 1)
        self.assertEqual(
            self.surface.candidate_surface_set_id,
            "as-fixed-point-diagonal-instance-candidate-surface-v1",
        )
        self.assertEqual(
            self.surface.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(self.surface.formal_language_path, str(LANGUAGE))
        self.assertEqual(self.surface.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.surface.fixed_point_targets_path,
            str(FIXED_POINT_TARGETS),
        )
        self.assertEqual(
            self.surface.diagonal_construction_targets_path,
            str(DIAGONAL_CONSTRUCTIONS),
        )
        self.assertEqual(
            self.surface.fixed_point_equation_bridge_targets_path,
            str(BRIDGES),
        )
        self.assertEqual(
            self.surface.diagonal_instance_closure_path,
            str(DIAGONAL_INSTANCE_CLOSURE),
        )
        self.assertEqual(self.surface.expected_candidate_count, 1)
        self.assertEqual(self.surface.expected_candidate_code_length, 296)
        self.assertEqual(
            tuple(self.surface.expected_candidate_code_prefix),
            (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13),
        )
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("diagonal-instance-candidate",))
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

    def test_checked_in_manifest_validates_candidate_surface_domain(self):
        report = validate_fixed_point_diagonal_instance_candidate_surface(
            self.surface,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.candidate_count, 1)
        self.assertEqual(report.source_kind_counts["diagonal-instance-candidate"], 1)

    def test_json_payload_exposes_candidate_surface(self):
        report = validate_fixed_point_diagonal_instance_candidate_surface(
            self.surface,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_diagonal_instance_candidate_surface
            .fixed_point_diagonal_instance_candidate_surface_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["candidate_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(
            payload["source_kind_counts"]["diagonal-instance-candidate"],
            1,
        )
        candidate = payload["candidates"][0]
        self.assertEqual(
            candidate["candidate_id"],
            "AS-FIXED-POINT-DIAGONAL-INSTANCE-CANDIDATE-SURFACE",
        )
        self.assertEqual(candidate["observed_candidate_code_length"], 296)
        self.assertTrue(candidate["observed_construction_case_is_open"])
        self.assertTrue(candidate["observed_construction_case_requires_candidate"])
        self.assertTrue(candidate["observed_candidate_source_is_closed_instance"])
        self.assertTrue(candidate["observed_candidate_codebook_roundtrip"])
        self.assertTrue(candidate["observed_candidate_preserves_target_skeleton"])
        self.assertTrue(candidate["observed_candidate_slot_is_seed_self_application"])
        self.assertTrue(candidate["observed_candidate_matches_bridge_observation"])
        self.assertTrue(candidate["observed_candidate_matches_closure"])
        self.assertTrue(candidate["observed_all_dependencies_accepted"])

    def test_text_report_exposes_candidate_surface_boundary(self):
        report = validate_fixed_point_diagonal_instance_candidate_surface(
            self.surface,
            WILLARD_MAP,
        )

        text = (
            fixed_point_diagonal_instance_candidate_surface
            .format_fixed_point_diagonal_instance_candidate_surface_report(report)
        )

        self.assertIn("Fixed-point diagonal instance candidate surface: accepted", text)
        self.assertIn("Candidate surfaces: 1", text)
        self.assertIn("diagonal-instance-candidate=1", text)
        self.assertIn("Candidate code length: 296", text)
        self.assertIn("construction_case_open=True", text)
        self.assertIn("requires_candidate=True", text)
        self.assertIn("candidate_closed=True", text)
        self.assertIn("codebook_roundtrip=True", text)
        self.assertIn("target_skeleton_preserved=True", text)
        self.assertIn("seed_self_application_slot=True", text)
        self.assertIn("matches_bridge=True", text)
        self.assertIn("matches_closure=True", text)
        self.assertIn("Candidate failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_candidate_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate_surface.json"
            data = json.loads(CANDIDATE_SURFACE.read_text(encoding="utf-8"))
            data["expected_candidate_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            surface = load_fixed_point_diagonal_instance_candidate_surface(path)

            report = validate_fixed_point_diagonal_instance_candidate_surface(
                surface,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-candidate-surface-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("candidate count mismatch" in result.detail for result in report.results)
        )

    def test_stale_candidate_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate_surface.json"
            data = json.loads(CANDIDATE_SURFACE.read_text(encoding="utf-8"))
            data["expected_candidate_code_length"] = 297
            path.write_text(json.dumps(data), encoding="utf-8")
            surface = load_fixed_point_diagonal_instance_candidate_surface(path)

            report = validate_fixed_point_diagonal_instance_candidate_surface(
                surface,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-candidate-surface-length",
            report.failed_subjects,
        )
        self.assertTrue(
            any("candidate length mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate_surface.json"
            data = json.loads(CANDIDATE_SURFACE.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            surface = load_fixed_point_diagonal_instance_candidate_surface(path)

            report = validate_fixed_point_diagonal_instance_candidate_surface(
                surface,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-candidate-surface-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_missing_dependency_path_is_rejected_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "candidate_surface.json"
            data = json.loads(CANDIDATE_SURFACE.read_text(encoding="utf-8"))
            data["diagonal_instance_closure_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            surface = load_fixed_point_diagonal_instance_candidate_surface(path)

            report = validate_fixed_point_diagonal_instance_candidate_surface(
                surface,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-diagonal-instance-candidate-surface-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "diagonal_instance_closure"
                and not result.accepted
                and "diagonal-instance-closure-load" in result.detail
                for result in report.results
            )
        )

    def test_cli_returns_zero_for_checked_in_candidate_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_candidate_surface
                .run_fixed_point_diagonal_instance_candidate_surface_cli(
                    [
                        "--candidate-surface",
                        str(CANDIDATE_SURFACE),
                        "--willard-map",
                        str(WILLARD_MAP),
                    ]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Fixed-point diagonal instance candidate surface: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_candidate_surface(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_diagonal_instance_candidate_surface
                .run_fixed_point_diagonal_instance_candidate_surface_cli(
                    [
                        "--candidate-surface",
                        str(CANDIDATE_SURFACE),
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
        self.assertEqual(payload["candidate_count"], 1)

    def test_module_execution_runs_candidate_surface_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_diagonal_instance_candidate_surface",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point diagonal instance candidate surface: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_candidate_surface_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_diagonal_instance_candidate_surface",
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
            payload["candidate_surface_set_id"],
            "as-fixed-point-diagonal-instance-candidate-surface-v1",
        )


if __name__ == "__main__":
    unittest.main()
