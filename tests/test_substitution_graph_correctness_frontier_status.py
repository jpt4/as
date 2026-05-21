import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_correctness_frontier_status
from autarkic_systems.substitution_graph_correctness_frontier_status import (
    FINITE_SUPPORT_BY_CASE_KIND,
    REQUIRED_FRONTIER_BLOCKER,
    REQUIRED_FRONTIER_STATUS,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SUPPORT_SUBJECTS,
    load_substitution_graph_correctness_frontier_status,
    validate_substitution_graph_correctness_frontier_status,
)


STATUS = Path("claims/substitution_graph_correctness_frontier_status.json")
CASES = Path("claims/substitution_graph_correctness_cases.json")
EXPECTED_CASE_STATUS_PATHS = {
    "codebook-roundtrip": (
        "claims/substitution_graph_codebook_roundtrip_frontier_status.json"
    ),
    "quotation-term-closure": (
        "claims/substitution_graph_quotation_term_closure_frontier_status.json"
    ),
    "meta-substitution-semantics": (
        "claims/substitution_graph_meta_substitution_semantics_frontier_status.json"
    ),
    "formula-schema-relation": (
        "claims/substitution_graph_formula_schema_relation_frontier_status.json"
    ),
    "diagonal-witness-composition": (
        "claims/substitution_graph_diagonal_witness_composition_frontier_status.json"
    ),
}


class SubstitutionGraphCorrectnessFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = load_substitution_graph_correctness_frontier_status(STATUS)

    def test_default_frontier_status_validation_reuses_cached_report_and_tracks_temp_manifest(self):
        validate_substitution_graph_correctness_frontier_status.cache_clear()
        first_manifest = load_substitution_graph_correctness_frontier_status(STATUS)
        second_manifest = load_substitution_graph_correctness_frontier_status(STATUS)

        first_report = validate_substitution_graph_correctness_frontier_status(
            first_manifest
        )
        after_first = (
            validate_substitution_graph_correctness_frontier_status.cache_info()
        )
        second_report = validate_substitution_graph_correctness_frontier_status(
            second_manifest
        )
        after_second = (
            validate_substitution_graph_correctness_frontier_status.cache_info()
        )

        self.assertTrue(first_report.accepted, first_report.results)
        self.assertIs(first_report, second_report)
        self.assertEqual(after_first.misses, 1)
        self.assertEqual(after_first.hits, 0)
        self.assertEqual(after_second.misses, 1)
        self.assertEqual(after_second.hits, 1)
        self.assertIn("codebook-roundtrip", first_manifest.case_status_paths)
        self.assertEqual(
            first_manifest.case_status_paths.get("codebook-roundtrip"),
            EXPECTED_CASE_STATUS_PATHS["codebook-roundtrip"],
        )
        self.assertEqual(
            dict(first_manifest.case_status_paths),
            EXPECTED_CASE_STATUS_PATHS,
        )
        self.assertEqual(
            tuple(first_manifest.case_status_paths.items()),
            tuple(EXPECTED_CASE_STATUS_PATHS.items()),
        )

        with tempfile.TemporaryDirectory() as tmp:
            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"]["codebook-roundtrip"] = (
                "claims/missing_substitution_graph_codebook_roundtrip_status.json"
            )
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            modified_manifest = load_substitution_graph_correctness_frontier_status(
                status_path
            )

            modified_report = validate_substitution_graph_correctness_frontier_status(
                modified_manifest
            )
            after_modified = (
                validate_substitution_graph_correctness_frontier_status.cache_info()
            )

        self.assertIsNot(first_report, modified_report)
        self.assertFalse(modified_report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status-rollup",
            modified_report.failed_subjects,
        )
        self.assertEqual(after_modified.misses, 2)
        self.assertEqual(after_modified.hits, 1)

        final_report = validate_substitution_graph_correctness_frontier_status(
            load_substitution_graph_correctness_frontier_status(STATUS)
        )
        after_final = (
            validate_substitution_graph_correctness_frontier_status.cache_info()
        )

        self.assertIs(first_report, final_report)
        self.assertEqual(after_final.misses, 2)
        self.assertEqual(after_final.hits, 2)

    def test_checked_in_manifest_names_frontier_boundary(self):
        self.assertEqual(self.status.schema_version, 1)
        self.assertEqual(
            self.status.status_set_id,
            "as-substitution-graph-correctness-frontier-status-v1",
        )
        self.assertEqual(self.status.frontier_status, REQUIRED_FRONTIER_STATUS)
        self.assertEqual(self.status.frontier_blocked_by, REQUIRED_FRONTIER_BLOCKER)
        self.assertEqual(
            self.status.substitution_graph_correctness_cases_path,
            str(CASES),
        )
        self.assertEqual(self.status.case_status_paths, EXPECTED_CASE_STATUS_PATHS)
        self.assertEqual(
            REQUIRED_SUPPORT_SUBJECTS,
            (
                "correctness_target",
                "codebook",
                "quotation_term",
                "formal_substitution",
                "formula_candidate",
                "substitution_representability",
                "codebook_roundtrip",
                "quotation_term_closure",
                "meta_substitution_semantics",
                "formula_schema_relation",
                "diagonal_witness_composition",
            ),
        )
        self.assertEqual(
            FINITE_SUPPORT_BY_CASE_KIND["codebook-roundtrip"],
            ("codebook_roundtrip",),
        )
        self.assertEqual(
            FINITE_SUPPORT_BY_CASE_KIND["diagonal-witness-composition"],
            ("diagonal_witness_composition",),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no formula correctness proof",
                "no substitution representability proof",
                "no diagonal lemma proof",
                "no fixed-point equation proof",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_frontier_status(self):
        report = validate_substitution_graph_correctness_frontier_status(self.status)

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(
            report.frontier_blocked_by,
            "substitution-graph-correctness",
        )
        self.assertEqual(report.case_count, 5)
        self.assertEqual(report.open_case_count, 5)
        self.assertEqual(report.support_surface_count, 11)
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
            tuple(status.frontier_blocked_by for status in report.case_status_rollup),
            tuple(EXPECTED_CASE_STATUS_PATHS),
        )
        self.assertEqual(
            tuple(status.proof_case_status for status in report.case_status_rollup),
            ("proof-case-open",) * 5,
        )

    def test_json_payload_exposes_per_case_support_summary(self):
        report = validate_substitution_graph_correctness_frontier_status(self.status)

        payload = (
            substitution_graph_correctness_frontier_status
            .substitution_graph_correctness_frontier_status_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(
            payload["frontier_blocked_by"],
            "substitution-graph-correctness",
        )
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["open_case_count"], 5)
        self.assertEqual(payload["support_surface_count"], 11)
        self.assertEqual(payload["case_status_count"], 5)
        self.assertEqual(payload["accepted_case_status_count"], 5)
        self.assertEqual(
            [surface["subject"] for surface in payload["support_surfaces"]],
            list(REQUIRED_SUPPORT_SUBJECTS),
        )
        supports = {
            case["case_kind"]: case["support_subjects"]
            for case in payload["case_supports"]
        }
        finite_supports = {
            case["case_kind"]: case["finite_support_subjects"]
            for case in payload["case_supports"]
        }
        self.assertEqual(
            supports["codebook-roundtrip"],
            ["correctness_target", "codebook", "codebook_roundtrip"],
        )
        self.assertEqual(
            supports["quotation-term-closure"],
            [
                "correctness_target",
                "codebook",
                "quotation_term",
                "quotation_term_closure",
            ],
        )
        self.assertEqual(
            supports["meta-substitution-semantics"],
            [
                "correctness_target",
                "formal_substitution",
                "meta_substitution_semantics",
            ],
        )
        self.assertEqual(
            supports["formula-schema-relation"],
            [
                "correctness_target",
                "formula_candidate",
                "formula_schema_relation",
            ],
        )
        self.assertEqual(
            supports["diagonal-witness-composition"],
            [
                "correctness_target",
                "substitution_representability",
                "diagonal_witness_composition",
            ],
        )
        self.assertEqual(
            finite_supports["formula-schema-relation"],
            ["formula_schema_relation"],
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
            self.assertEqual(rollup[case_kind]["frontier_blocked_by"], case_kind)
            self.assertEqual(rollup[case_kind]["proof_case_status"], "proof-case-open")
            self.assertEqual(rollup[case_kind]["failed_subjects"], [])

    def test_text_report_exposes_blocked_boundary(self):
        report = validate_substitution_graph_correctness_frontier_status(self.status)

        text = (
            substitution_graph_correctness_frontier_status
            .format_substitution_graph_correctness_frontier_status_report(report)
        )

        self.assertIn(
            "Substitution graph correctness frontier status: accepted",
            text,
        )
        self.assertIn("Frontier status: blocked", text)
        self.assertIn("Blocked by: substitution-graph-correctness", text)
        self.assertIn("Open correctness cases: 5/5", text)
        self.assertIn("Support surfaces: 11", text)
        self.assertIn("Compact case-status rollup: 5/5", text)
        self.assertIn(
            "- codebook-roundtrip: accepted "
            "(claims/substitution_graph_codebook_roundtrip_frontier_status.json)",
            text,
        )
        self.assertIn("Case kind: formula-schema-relation", text)
        self.assertIn(
            "Support: correctness_target, formula_candidate, formula_schema_relation",
            text,
        )
        self.assertIn("Finite support: formula_schema_relation", text)
        self.assertIn("Failed subjects: none", text)
        self.assertNotIn("FAIL", text)

    def test_overclaiming_frontier_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["frontier_status"] = "substitution-graph-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("overclaiming frontier status" in result.detail for result in report.results)
        )

    def test_proof_promotion_case_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["status"] = "formula-correctness-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status",
            report.failed_subjects,
        )
        self.assertTrue(
            any("proof promotion status" in result.detail for result in report.results)
        )

    def test_missing_support_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["codebook_roundtrip_path"] = str(Path(tmp) / "missing.json")
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-support",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                result.subject == "codebook_roundtrip"
                and not result.accepted
                and "support artifact missing or invalid" in result.detail
                for result in report.results
            )
        )

    def test_missing_compact_case_status_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"].pop("codebook-roundtrip")
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing case-status paths" in result.detail for result in report.results)
        )

    def test_compact_case_status_blocker_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            compact_path = Path(tmp) / "codebook_status.json"
            compact_data = json.loads(
                Path(
                    EXPECTED_CASE_STATUS_PATHS["codebook-roundtrip"]
                ).read_text(encoding="utf-8")
            )
            compact_data["frontier_blocked_by"] = "quotation-term-closure"
            compact_path.write_text(json.dumps(compact_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"]["codebook-roundtrip"] = str(compact_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "expected codebook-roundtrip blocker" in result.detail
                for result in report.results
            )
        )

    def test_closed_compact_case_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["status"] = "formula-correctness-proved"
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            compact_path = Path(tmp) / "codebook_status.json"
            compact_data = json.loads(
                Path(
                    EXPECTED_CASE_STATUS_PATHS["codebook-roundtrip"]
                ).read_text(encoding="utf-8")
            )
            compact_data["substitution_graph_correctness_cases_path"] = str(case_path)
            compact_path.write_text(json.dumps(compact_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"]["codebook-roundtrip"] = str(compact_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any("expected proof-case-open" in result.detail for result in report.results)
        )

    def test_unaccepted_compact_case_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            compact_path = Path(tmp) / "codebook_status.json"
            compact_data = json.loads(
                Path(
                    EXPECTED_CASE_STATUS_PATHS["codebook-roundtrip"]
                ).read_text(encoding="utf-8")
            )
            compact_data["non_claims"] = compact_data["non_claims"][:-1]
            compact_path.write_text(json.dumps(compact_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["case_status_paths"]["codebook-roundtrip"] = str(compact_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-status-rollup",
            report.failed_subjects,
        )
        self.assertTrue(
            any(
                "case status validator rejected" in result.detail
                for result in report.results
            )
        )

    def test_missing_status_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_empty_status_non_claim_is_rejected_at_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "status.json"
            data = json.loads(STATUS.read_text(encoding="utf-8"))
            data["non_claims"][0] = ""
            path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaises(ValueError):
                load_substitution_graph_correctness_frontier_status(path)

    def test_missing_case_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_path = Path(tmp) / "cases.json"
            case_data = json.loads(CASES.read_text(encoding="utf-8"))
            case_data["cases"][0]["non_claims"] = case_data["cases"][0]["non_claims"][:-1]
            case_path.write_text(json.dumps(case_data), encoding="utf-8")

            status_path = Path(tmp) / "status.json"
            status_data = json.loads(STATUS.read_text(encoding="utf-8"))
            status_data["substitution_graph_correctness_cases_path"] = str(case_path)
            status_path.write_text(json.dumps(status_data), encoding="utf-8")
            status = load_substitution_graph_correctness_frontier_status(status_path)

            report = validate_substitution_graph_correctness_frontier_status(status)

        self.assertFalse(report.accepted)
        self.assertIn(
            "substitution-graph-correctness-frontier-case-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_correctness_frontier_status
                .run_substitution_graph_correctness_frontier_status_cli(
                    ["--status", str(STATUS)]
                )
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn(
            "Substitution graph correctness frontier status: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_frontier_status(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                substitution_graph_correctness_frontier_status
                .run_substitution_graph_correctness_frontier_status_cli(
                    ["--status", str(STATUS), "--format", "json"]
                )
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["frontier_blocked_by"],
            "substitution-graph-correctness",
        )

    def test_module_execution_runs_text_and_json_frontier_status_validation(self):
        text = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_correctness_frontier_status",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )
        self.assertEqual(text.returncode, 0, text.stderr)
        self.assertIn(
            "Substitution graph correctness frontier status: accepted",
            text.stdout,
        )

        json_run = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_correctness_frontier_status",
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
        self.assertEqual(payload["case_count"], 5)
        self.assertEqual(payload["case_status_count"], 5)


if __name__ == "__main__":
    unittest.main()
