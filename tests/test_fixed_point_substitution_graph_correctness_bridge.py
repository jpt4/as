import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_substitution_graph_correctness_bridge
from autarkic_systems.fixed_point_substitution_graph_correctness_bridge import (
    REQUIRED_CORRECTNESS_CASE_KINDS,
    REQUIRED_FINITE_DEPENDENCY_SUBJECTS,
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SOURCE_KINDS,
    load_fixed_point_substitution_graph_correctness_bridge,
    validate_fixed_point_substitution_graph_correctness_bridge,
)


BRIDGE = Path("claims/fixed_point_substitution_graph_correctness_bridge.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
SUBSTITUTION_GRAPH_CORRECTNESS = Path("claims/substitution_graph_correctness_targets.json")
SUBSTITUTION_GRAPH_CORRECTNESS_CASES = Path("claims/substitution_graph_correctness_cases.json")
CODEBOOK_ROUNDTRIP = Path("claims/substitution_graph_codebook_roundtrip.json")
QUOTATION_TERM_CLOSURE = Path("claims/substitution_graph_quotation_term_closure.json")
META_SUBSTITUTION_SEMANTICS = Path(
    "claims/substitution_graph_meta_substitution_semantics.json"
)
FORMULA_SCHEMA_RELATION = Path("claims/substitution_graph_formula_schema_relation.json")
DIAGONAL_WITNESS_COMPOSITION = Path(
    "claims/substitution_graph_diagonal_witness_composition.json"
)
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointSubstitutionGraphCorrectnessBridgeTests(unittest.TestCase):
    def setUp(self):
        self.bridge = load_fixed_point_substitution_graph_correctness_bridge(BRIDGE)

    def test_checked_in_manifest_names_graph_correctness_bridge_domain(self):
        self.assertEqual(self.bridge.schema_version, 1)
        self.assertEqual(
            self.bridge.bridge_set_id,
            "as-fixed-point-substitution-graph-correctness-bridge-v1",
        )
        self.assertEqual(
            self.bridge.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.bridge.substitution_graph_correctness_targets_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS),
        )
        self.assertEqual(
            self.bridge.substitution_graph_correctness_cases_path,
            str(SUBSTITUTION_GRAPH_CORRECTNESS_CASES),
        )
        self.assertEqual(
            self.bridge.codebook_roundtrip_path,
            str(CODEBOOK_ROUNDTRIP),
        )
        self.assertEqual(
            self.bridge.quotation_term_closure_path,
            str(QUOTATION_TERM_CLOSURE),
        )
        self.assertEqual(
            self.bridge.meta_substitution_semantics_path,
            str(META_SUBSTITUTION_SEMANTICS),
        )
        self.assertEqual(
            self.bridge.formula_schema_relation_path,
            str(FORMULA_SCHEMA_RELATION),
        )
        self.assertEqual(
            self.bridge.diagonal_witness_composition_path,
            str(DIAGONAL_WITNESS_COMPOSITION),
        )
        self.assertEqual(self.bridge.expected_bridge_count, 1)
        self.assertEqual(self.bridge.expected_correctness_case_count, 5)
        self.assertEqual(REQUIRED_SOURCE_KINDS, ("graph-correctness-bridge",))
        self.assertEqual(
            REQUIRED_CORRECTNESS_CASE_KINDS,
            (
                "codebook-roundtrip",
                "quotation-term-closure",
                "meta-substitution-semantics",
                "formula-schema-relation",
                "diagonal-witness-composition",
            ),
        )
        self.assertEqual(
            REQUIRED_FINITE_DEPENDENCY_SUBJECTS,
            (
                "codebook_roundtrip",
                "quotation_term_closure",
                "meta_substitution_semantics",
                "formula_schema_relation",
                "diagonal_witness_composition",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "substitution-graph-correctness-proof",
                "bridge-equality-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            REQUIRED_NON_CLAIMS,
            (
                "no substitution graph correctness proof",
                "no bridge equality proof",
                "no fixed-point equation proof",
                "no arithmetized proof predicate",
                "no self-consistency theorem",
            ),
        )

    def test_checked_in_manifest_validates_graph_correctness_bridge_domain(self):
        report = validate_fixed_point_substitution_graph_correctness_bridge(
            self.bridge,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.bridge_count, 1)
        self.assertEqual(report.source_kind_counts["graph-correctness-bridge"], 1)

    def test_json_payload_exposes_graph_correctness_bridge(self):
        report = validate_fixed_point_substitution_graph_correctness_bridge(
            self.bridge,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_substitution_graph_correctness_bridge
            .fixed_point_substitution_graph_correctness_bridge_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["bridge_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        bridge = payload["bridges"][0]
        self.assertEqual(
            bridge["bridge_id"],
            "AS-FIXED-POINT-SUBSTITUTION-GRAPH-CORRECTNESS-BRIDGE",
        )
        self.assertEqual(bridge["observed_correctness_case_count"], 5)
        self.assertEqual(bridge["observed_finite_dependency_count"], 5)
        self.assertTrue(bridge["observed_construction_case_is_open"])
        self.assertTrue(bridge["observed_construction_case_requires_correctness"])
        self.assertTrue(bridge["observed_correctness_cases_accepted"])
        self.assertTrue(bridge["observed_all_correctness_case_kinds_present"])
        self.assertTrue(bridge["observed_all_finite_dependencies_accepted"])
        self.assertTrue(bridge["observed_diagonal_composition_links_target"])

    def test_text_report_exposes_graph_correctness_bridge_boundary(self):
        report = validate_fixed_point_substitution_graph_correctness_bridge(
            self.bridge,
            WILLARD_MAP,
        )

        text = (
            fixed_point_substitution_graph_correctness_bridge
            .format_fixed_point_substitution_graph_correctness_bridge_report(report)
        )

        self.assertIn("Fixed-point substitution graph correctness bridge: accepted", text)
        self.assertIn("Graph-correctness bridges: 1", text)
        self.assertIn("graph-correctness-bridge=1", text)
        self.assertIn("Bridge failures: none", text)
        self.assertNotIn("FAIL", text)

    def test_stale_bridge_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridge.json"
            data = json.loads(BRIDGE.read_text(encoding="utf-8"))
            data["expected_bridge_count"] = 2
            path.write_text(json.dumps(data), encoding="utf-8")
            bridge = load_fixed_point_substitution_graph_correctness_bridge(path)

            report = validate_fixed_point_substitution_graph_correctness_bridge(
                bridge,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-bridge-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("bridge count mismatch" in result.detail for result in report.results)
        )

    def test_stale_correctness_case_count_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridge.json"
            data = json.loads(BRIDGE.read_text(encoding="utf-8"))
            data["expected_correctness_case_count"] = 4
            path.write_text(json.dumps(data), encoding="utf-8")
            bridge = load_fixed_point_substitution_graph_correctness_bridge(path)

            report = validate_fixed_point_substitution_graph_correctness_bridge(
                bridge,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-bridge-case-count",
            report.failed_subjects,
        )
        self.assertTrue(
            any("correctness case count mismatch" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bridge.json"
            data = json.loads(BRIDGE.read_text(encoding="utf-8"))
            data["non_claims"] = data["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            bridge = load_fixed_point_substitution_graph_correctness_bridge(path)

            report = validate_fixed_point_substitution_graph_correctness_bridge(
                bridge,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-substitution-graph-correctness-bridge-non-claim",
            report.failed_subjects,
        )
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_bridge_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_graph_correctness_bridge
                .run_fixed_point_substitution_graph_correctness_bridge_cli(
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
        self.assertIn(
            "Fixed-point substitution graph correctness bridge: accepted",
            output,
        )

    def test_cli_returns_json_for_checked_in_bridge_domain(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_substitution_graph_correctness_bridge
                .run_fixed_point_substitution_graph_correctness_bridge_cli(
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

    def test_module_execution_runs_bridge_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_substitution_graph_correctness_bridge",
            ],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Fixed-point substitution graph correctness bridge: accepted",
            completed.stdout,
        )

    def test_module_execution_runs_json_bridge_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.fixed_point_substitution_graph_correctness_bridge",
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
            "as-fixed-point-substitution-graph-correctness-bridge-v1",
        )


if __name__ == "__main__":
    unittest.main()
