import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import (
    substitution_graph_meta_substitution_semantics_frontier_status,
)
from autarkic_systems.substitution_graph_meta_substitution_semantics_frontier_status import (
    REQUIRED_CASE_KIND,
    REQUIRED_CASE_SUPPORT_SUBJECTS,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_substitution_graph_meta_substitution_semantics_frontier_status,
    validate_substitution_graph_meta_substitution_semantics_frontier_status,
)


STATUS = Path(
    "claims/substitution_graph_meta_substitution_semantics_frontier_status.json"
)
CASES = Path("claims/substitution_graph_correctness_cases.json")
SEMANTICS = Path("claims/substitution_graph_meta_substitution_semantics.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FORMAL_SUBSTITUTION_EXAMPLES = Path("language/formal_substitution_examples.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")


class SubstitutionGraphMetaSubstitutionSemanticsFrontierStatusTests(
    unittest.TestCase
):
    def setUp(self):
        self.status = (
            load_substitution_graph_meta_substitution_semantics_frontier_status(
                STATUS
            )
        )

    def test_checked_in_manifest_names_meta_substitution_frontier(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            (
                "as-substitution-graph-meta-substitution-semantics-"
                "frontier-status-v1"
            ),
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(
            self.status.frontier_blocked_by,
            "meta-substitution-semantics",
        )
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(self.status.meta_substitution_semantics_path, str(SEMANTICS))
        self.assertEqual(self.status.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.status.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.status.formal_substitution_examples_path,
            str(FORMAL_SUBSTITUTION_EXAMPLES),
        )
        self.assertEqual(
            self.status.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.status.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(self.status.required_case_kind, "meta-substitution-semantics")
        self.assertEqual(self.status.required_case_status, "proof-case-open")
        self.assertEqual(self.status.expected_support_surface_count, 1)
        self.assertEqual(self.status.expected_semantics_subject_count, 6)
        self.assertEqual(REQUIRED_CASE_KIND, "meta-substitution-semantics")
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            ("meta_substitution_semantics",),
        )
        self.assertEqual(
            REQUIRED_CASE_SUPPORT_SUBJECTS,
            (
                "correctness_target",
                "formal_substitution",
                "meta_substitution_semantics",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no formula correctness proof",
                "no substitution representability proof",
                "no diagonal lemma proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_frontier_status(self):
        report = (
            validate_substitution_graph_meta_substitution_semantics_frontier_status(
                self.status,
                WILLARD_MAP,
            )
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "meta-substitution-semantics")
        self.assertEqual(
            report.proof_case.case_id,
            "AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS",
        )
        self.assertEqual(report.proof_case.case_kind, "meta-substitution-semantics")
        self.assertEqual(report.proof_case.status, "proof-case-open")
        self.assertEqual(
            report.proof_case.required_dependency_subjects,
            REQUIRED_CASE_SUPPORT_SUBJECTS,
        )
        self.assertEqual(report.support_surface_count, 1)
        self.assertEqual(report.semantics_subject_count, 6)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))

    def test_json_payload_exposes_compact_handoff(self):
        report = (
            validate_substitution_graph_meta_substitution_semantics_frontier_status(
                self.status,
                WILLARD_MAP,
            )
        )

        payload = (
            substitution_graph_meta_substitution_semantics_frontier_status
            .substitution_graph_meta_substitution_semantics_frontier_status_payload(
                report
            )
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "meta-substitution-semantics")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 1)
        self.assertEqual(payload["semantics_subject_count"], 6)
        self.assertEqual(
            payload["proof_case"]["case_id"],
            "AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS",
        )
        self.assertEqual(
            payload["proof_case"]["case_kind"],
            "meta-substitution-semantics",
        )
        self.assertEqual(payload["proof_case"]["status"], "proof-case-open")
        self.assertEqual(
            payload["proof_case"]["required_dependency_subjects"],
            list(REQUIRED_CASE_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            payload["support_facts"]["meta_substitution_semantics"][
                "semantics_set_id"
            ],
            "as-substitution-graph-meta-substitution-semantics-v1",
        )
        self.assertEqual(
            payload["support_facts"]["meta_substitution_semantics"]["subject_count"],
            6,
        )
        self.assertEqual(
            payload["support_facts"]["meta_substitution_semantics"][
                "failed_subjects"
            ],
            [],
        )

    def test_semantics_support_surface_is_accepted_and_non_promotional(self):
        report = (
            validate_substitution_graph_meta_substitution_semantics_frontier_status(
                self.status,
                WILLARD_MAP,
            )
        )

        surface = {item.subject: item for item in report.support_surfaces}[
            "meta_substitution_semantics"
        ]

        self.assertTrue(surface.accepted)
        self.assertEqual(
            surface.facts["semantics_set_id"],
            "as-substitution-graph-meta-substitution-semantics-v1",
        )
        self.assertEqual(surface.facts["subject_count"], 6)
        self.assertEqual(
            surface.facts["source_kind_counts"],
            {"finite-evaluation": 3, "formula-candidate": 3},
        )
        self.assertEqual(surface.facts["failed_subjects"], ())
        self.assertGreaterEqual(surface.facts["non_claim_count"], 5)
        self.assertIn(
            "no arithmetized proof predicate",
            report.manifest.non_claims,
        )

    def test_text_report_exposes_blocked_boundary(self):
        report = (
            validate_substitution_graph_meta_substitution_semantics_frontier_status(
                self.status,
                WILLARD_MAP,
            )
        )

        text = (
            substitution_graph_meta_substitution_semantics_frontier_status
            .format_substitution_graph_meta_substitution_semantics_frontier_status_report(
                report
            )
        )

        self.assertIn(
            (
                "Substitution graph meta-substitution-semantics frontier "
                "status: accepted"
            ),
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: meta-substitution-semantics", text)
        self.assertIn(
            "Proof case: AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS",
            text,
        )
        self.assertIn("Case kind: meta-substitution-semantics", text)
        self.assertIn("Case status: proof-case-open", text)
        self.assertIn("Support surfaces: 1", text)
        self.assertIn("Meta-substitution subjects: 6", text)
        self.assertIn("meta_substitution_semantics: accepted", text)
        self.assertIn("Failed subjects: none", text)
        self.assertIn("Non-claims: no formula correctness proof", text)
        self.assertNotIn("FAIL", text)

    def test_proof_promotion_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "meta-substitution-semantics-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    path
                )
            )

            report = (
                validate_substitution_graph_meta_substitution_semantics_frontier_status(
                    status,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "proof-promotion frontier status" in result.detail
                for result in report.results
            )
        )

    def test_missing_status_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    path
                )
            )

            report = (
                validate_substitution_graph_meta_substitution_semantics_frontier_status(
                    status,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_empty_status_non_claims_are_rejected_by_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = []
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    path
                )

    def test_stale_semantics_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["meta_substitution_semantics_path"] = str(
                Path(tmp) / "missing.json"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    path
                )
            )

            report = (
                validate_substitution_graph_meta_substitution_semantics_frontier_status(
                    status,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-frontier-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "meta_substitution_semantics_path"
                and not result.accepted
                for result in report.results
            )
        )

    def test_closed_meta_substitution_semantics_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "meta-substitution-semantics":
                    case["status"] = "formula-correctness-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_meta_substitution_semantics_frontier_status(
                    status,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("proof case is not open" in result.detail for result in report.results)
        )

    def test_meta_substitution_case_dependency_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "meta-substitution-semantics":
                    case["required_dependency_subjects"] = [
                        "correctness_target",
                        "meta_substitution_semantics",
                    ]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_meta_substitution_semantics_frontier_status(
                    status,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-frontier-case-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any("dependency subjects mismatch" in result.detail for result in report.results)
        )

    def test_semantics_support_failed_subjects_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            semantics_path = Path(tmp) / "semantics.json"
            semantics_data = json.loads(SEMANTICS.read_text(encoding="utf-8"))
            semantics_data["expected_subject_count"] = 7
            semantics_path.write_text(json.dumps(semantics_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["meta_substitution_semantics_path"] = str(semantics_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_meta_substitution_semantics_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_meta_substitution_semantics_frontier_status(
                    status,
                    WILLARD_MAP,
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-meta-substitution-semantics-frontier-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "meta_substitution_semantics"
                and "failed subjects" in result.detail
                for result in report.results
            )
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_meta_substitution_semantics_frontier_status
                .run_substitution_graph_meta_substitution_semantics_frontier_status_cli(
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
        self.assertIn(
            (
                "Substitution graph meta-substitution-semantics frontier "
                "status: accepted"
            ),
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_meta_substitution_semantics_frontier_status
                .run_substitution_graph_meta_substitution_semantics_frontier_status_cli(
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
        self.assertEqual(
            payload["frontier_blocked_by"],
            "meta-substitution-semantics",
        )
        self.assertEqual(payload["semantics_subject_count"], 6)

    def test_module_execution_runs_text_and_json_frontier_status_validation(self):
        text = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_meta_substitution_semantics_frontier_status"
                ),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn(
            (
                "Substitution graph meta-substitution-semantics frontier "
                "status: accepted"
            ),
            text.stdout,
        )

        json_run = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_meta_substitution_semantics_frontier_status"
                ),
                "--format",
                "json",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        payload = json.loads(json_run.stdout)
        self.assertEqual(json_run.returncode, 0, json_run.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["support_surface_count"], 1)


if __name__ == "__main__":
    unittest.main()
