import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import (
    substitution_graph_quotation_term_closure_frontier_status,
)
from autarkic_systems.substitution_graph_quotation_term_closure_frontier_status import (
    REQUIRED_CASE_KIND,
    REQUIRED_CASE_SUPPORT_SUBJECTS,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_substitution_graph_quotation_term_closure_frontier_status,
    validate_substitution_graph_quotation_term_closure_frontier_status,
)


STATUS = Path(
    "claims/substitution_graph_quotation_term_closure_frontier_status.json"
)
CASES = Path("claims/substitution_graph_correctness_cases.json")
CLOSURE = Path("claims/substitution_graph_quotation_term_closure.json")


class SubstitutionGraphQuotationTermClosureFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = (
            load_substitution_graph_quotation_term_closure_frontier_status(STATUS)
        )

    def test_checked_in_manifest_names_quotation_term_closure_frontier(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-substitution-graph-quotation-term-closure-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, "blocked")
        self.assertEqual(self.status.frontier_blocked_by, "quotation-term-closure")
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(self.status.quotation_term_closure_path, str(CLOSURE))
        self.assertEqual(self.status.expected_support_surface_count, 1)
        self.assertEqual(self.status.expected_closure_subject_count, 12)
        self.assertEqual(REQUIRED_CASE_KIND, "quotation-term-closure")
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            ("quotation_term_closure",),
        )
        self.assertEqual(
            REQUIRED_CASE_SUPPORT_SUBJECTS,
            (
                "correctness_target",
                "codebook",
                "quotation_term",
                "quotation_term_closure",
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
        report = validate_substitution_graph_quotation_term_closure_frontier_status(
            self.status
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "quotation-term-closure")
        self.assertEqual(
            report.case.case_id,
            "AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE",
        )
        self.assertEqual(report.case.case_kind, "quotation-term-closure")
        self.assertEqual(report.case.status, "proof-case-open")
        self.assertEqual(report.case.support_subjects, REQUIRED_CASE_SUPPORT_SUBJECTS)
        self.assertEqual(report.support_surface_count, 1)
        self.assertTrue(all(surface.accepted for surface in report.support_surfaces))

    def test_json_payload_exposes_compact_handoff(self):
        report = validate_substitution_graph_quotation_term_closure_frontier_status(
            self.status
        )

        payload = (
            substitution_graph_quotation_term_closure_frontier_status
            .substitution_graph_quotation_term_closure_frontier_status_payload(
                report
            )
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "quotation-term-closure")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["support_surface_count"], 1)
        self.assertEqual(
            payload["case"]["case_id"],
            "AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE",
        )
        self.assertEqual(payload["case"]["case_kind"], "quotation-term-closure")
        self.assertEqual(payload["case"]["status"], "proof-case-open")
        self.assertEqual(
            payload["case"]["support_subjects"],
            list(REQUIRED_CASE_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        self.assertEqual(
            payload["support_facts"]["quotation_term_closure"]["closure_set_id"],
            "as-substitution-graph-quotation-term-closure-v1",
        )
        self.assertEqual(
            payload["support_facts"]["quotation_term_closure"]["subject_count"],
            12,
        )
        self.assertEqual(
            payload["support_facts"]["quotation_term_closure"]["failed_subjects"],
            [],
        )

    def test_closure_support_surface_is_accepted_and_non_promotional(self):
        report = validate_substitution_graph_quotation_term_closure_frontier_status(
            self.status
        )

        surface = {item.subject: item for item in report.support_surfaces}[
            "quotation_term_closure"
        ]

        self.assertTrue(surface.accepted)
        self.assertEqual(
            surface.facts["closure_set_id"],
            "as-substitution-graph-quotation-term-closure-v1",
        )
        self.assertEqual(surface.facts["subject_count"], 12)
        self.assertEqual(
            surface.facts["source_kind_counts"],
            {"finite-evaluation": 9, "formula-candidate": 3},
        )
        self.assertEqual(surface.facts["failed_subjects"], ())
        self.assertGreaterEqual(surface.facts["non_claim_count"], 5)

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_substitution_graph_quotation_term_closure_frontier_status(
            self.status
        )

        text = (
            substitution_graph_quotation_term_closure_frontier_status
            .format_substitution_graph_quotation_term_closure_frontier_status_report(
                report
            )
        )

        self.assertIn(
            "Substitution graph quotation-term-closure frontier status: accepted",
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: quotation-term-closure", text)
        self.assertIn(
            "Case: AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE",
            text,
        )
        self.assertIn("Case kind: quotation-term-closure", text)
        self.assertIn("Case status: proof-case-open", text)
        self.assertIn("Support surfaces: 1", text)
        self.assertIn("quotation_term_closure: accepted", text)
        self.assertIn("closure subjects 12", text)
        self.assertIn("Failed subjects: none", text)
        self.assertIn("Non-claims: no formula correctness proof", text)
        self.assertNotIn("FAIL", text)

    def test_proof_promotion_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "quotation-term-closure-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_quotation_term_closure_frontier_status(path)
            )

            report = (
                validate_substitution_graph_quotation_term_closure_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-quotation-term-closure-frontier-status",
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
            status = (
                load_substitution_graph_quotation_term_closure_frontier_status(path)
            )

            report = (
                validate_substitution_graph_quotation_term_closure_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-quotation-term-closure-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_empty_non_claims_are_rejected_by_loader(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = []
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_substitution_graph_quotation_term_closure_frontier_status(path)

    def test_stale_closure_dependency_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["quotation_term_closure_path"] = str(Path(tmp) / "missing.json")
            path.write_text(json.dumps(data), encoding="utf-8")
            status = (
                load_substitution_graph_quotation_term_closure_frontier_status(path)
            )

            report = (
                validate_substitution_graph_quotation_term_closure_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-quotation-term-closure-frontier-dependency",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "quotation_term_closure_path"
                and not result.accepted
                for result in report.results
            )
        )

    def test_closed_quotation_term_closure_case_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            for case in case_data["cases"]:
                if case["case_kind"] == "quotation-term-closure":
                    case["status"] = "quotation-term-closure-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_quotation_term_closure_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_quotation_term_closure_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-quotation-term-closure-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("case is not open" in result.detail for result in report.results)
        )

    def test_closure_support_failed_subjects_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            closure_path = Path(tmp) / "closure.json"
            closure_data = json.loads(CLOSURE.read_text(encoding="utf-8"))
            closure_data["expected_subject_count"] = 13
            closure_path.write_text(json.dumps(closure_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["quotation_term_closure_path"] = str(closure_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = (
                load_substitution_graph_quotation_term_closure_frontier_status(
                    status_path
                )
            )

            report = (
                validate_substitution_graph_quotation_term_closure_frontier_status(
                    status
                )
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-quotation-term-closure-frontier-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "quotation_term_closure"
                and "failed subjects" in result.detail
                for result in report.results
            )
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_quotation_term_closure_frontier_status
                .run_substitution_graph_quotation_term_closure_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Substitution graph quotation-term-closure frontier status: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_quotation_term_closure_frontier_status
                .run_substitution_graph_quotation_term_closure_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_blocked_by"], "quotation-term-closure")

    def test_module_execution_runs_text_and_json_frontier_status_validation(self):
        text = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_quotation_term_closure_frontier_status"
                ),
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn(
            "Substitution graph quotation-term-closure frontier status: accepted",
            text.stdout,
        )

        json_run = subprocess.run(
            [
                sys.executable,
                "-m",
                (
                    "autarkic_systems."
                    "substitution_graph_quotation_term_closure_frontier_status"
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
