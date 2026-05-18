import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_target
from autarkic_systems.substitution_graph_target import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_LANGUAGE_FEATURES,
    REQUIRED_WILLARD_ANCHORS,
    load_substitution_graph_targets,
    validate_substitution_graph_targets,
)


TARGETS = Path("claims/substitution_graph_targets.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
SUBSTITUTION_WITNESSES = Path("claims/substitution_representability_targets.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class SubstitutionGraphTargetTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_substitution_graph_targets(TARGETS)

    def test_checked_in_manifest_names_delta0_graph_target(self):
        target = self.manifest.targets[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.graph_target_set_id,
            "as-substitution-graph-target-v1",
        )
        self.assertEqual(self.manifest.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.manifest.substitution_representability_targets_path,
            str(SUBSTITUTION_WITNESSES),
        )
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
                "W2020-D3.4-TYPE-NS-A-S-M",
            ),
        )
        self.assertEqual(
            REQUIRED_LANGUAGE_FEATURES,
            (
                "bounded-formula-class:delta0",
                "function-symbol:substitution_code",
                "relation-symbol:equals",
                "relation-symbol:less_than",
                "quantifier-form:bounded-forall",
                "quantifier-form:bounded-exists",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "delta0-graph-formula",
                "formula-correctness-proof",
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            target.target_id,
            "AS-SUBSTITUTION-GRAPH-DELTA0-TARGET",
        )
        self.assertEqual(
            target.witness_id,
            "AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS",
        )
        self.assertEqual(target.relation_name, "subst_code_graph")
        self.assertEqual(target.formula_class, "delta0")
        self.assertEqual(target.status, "graph-formula-target-not-constructed")
        self.assertEqual(
            target.graph_variables,
            {"formula_code": "x", "argument_code": "y", "output_code": "z"},
        )
        self.assertEqual(target.expected_witness_formula_code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))
        self.assertEqual(target.expected_witness_argument_code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))
        self.assertEqual(target.expected_witness_output_code_length, 296)
        self.assertEqual(
            target.expected_witness_output_code_prefix,
            (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13),
        )
        self.assertEqual(target.expected_witness_output_free_variables, ())
        self.assertIn("no substitution representability proof", target.non_claims)

    def test_checked_in_manifest_validates_delta0_graph_target(self):
        report = validate_substitution_graph_targets(
            self.manifest,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.target_count, 1)
        self.assertTrue(
            any(
                result.subject == "targets"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_graph_target_and_witness_tether(self):
        report = validate_substitution_graph_targets(
            self.manifest,
            WILLARD_MAP,
        )

        payload = substitution_graph_target.substitution_graph_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["target_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["targets"][0]["formula_class"], "delta0")
        self.assertEqual(payload["targets"][0]["observed_witness_formula_code_length"], 10)
        self.assertEqual(payload["targets"][0]["observed_witness_output_code_length"], 296)
        self.assertEqual(
            payload["targets"][0]["status"],
            "graph-formula-target-not-constructed",
        )

    def test_text_report_exposes_graph_target_boundary(self):
        report = validate_substitution_graph_targets(
            self.manifest,
            WILLARD_MAP,
        )

        text = substitution_graph_target.format_substitution_graph_report(report)

        self.assertIn("Substitution graph targets: accepted", text)
        self.assertIn("AS-SUBSTITUTION-GRAPH-DELTA0-TARGET", text)
        self.assertIn("Formula class: delta0", text)
        self.assertIn("Witness output code length: 296", text)
        self.assertIn("Status: graph-formula-target-not-constructed", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_witness_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["witness_id"] = "UNKNOWN-WITNESS"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_targets(path)

            report = validate_substitution_graph_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-witness", report.failed_subjects)
        self.assertTrue(
            any("unknown substitution witness: UNKNOWN-WITNESS" in result.detail for result in report.results)
        )

    def test_stale_witness_output_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["expected_witness_output_code_length"] = 10
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_targets(path)

            report = validate_substitution_graph_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-witness", report.failed_subjects)
        self.assertTrue(
            any("witness output code length mismatch" in result.detail for result in report.results)
        )

    def test_constructed_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["status"] = "delta0-graph-formula-constructed"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_targets(path)

            report = validate_substitution_graph_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-status", report.failed_subjects)
        self.assertTrue(
            any("constructed graph formulas are not supported" in result.detail for result in report.results)
        )

    def test_missing_language_feature_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["required_language_features"].remove(
                "quantifier-form:bounded-exists"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_substitution_graph_targets(path)

            report = validate_substitution_graph_targets(manifest, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-language-feature", report.failed_subjects)
        self.assertTrue(
            any("missing required language features" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_target.run_substitution_graph_cli(
                ["--targets", str(TARGETS), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph targets: accepted", output)

    def test_cli_returns_json_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_target.run_substitution_graph_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["targets"][0]["observed_witness_output_code_length"], 296)

    def test_module_execution_runs_substitution_graph_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_target"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Substitution graph targets: accepted", completed.stdout)

    def test_module_execution_runs_json_substitution_graph_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_target",
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
        self.assertEqual(payload["target_count"], 1)


if __name__ == "__main__":
    unittest.main()
