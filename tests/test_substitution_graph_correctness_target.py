import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_correctness
from autarkic_systems.substitution_graph_correctness import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    load_substitution_graph_correctness_targets,
    validate_substitution_graph_correctness_targets,
)


TARGETS = Path("claims/substitution_graph_correctness_targets.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
GRAPH_TARGETS = Path("claims/substitution_graph_targets.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")
EVALUATION_EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")


class SubstitutionGraphCorrectnessTargetTests(unittest.TestCase):
    def setUp(self):
        self.targets = load_substitution_graph_correctness_targets(TARGETS)

    def test_checked_in_manifest_names_correctness_target(self):
        (target,) = self.targets.targets

        self.assertEqual(self.targets.schema_version, 1)
        self.assertEqual(
            self.targets.target_set_id,
            "as-substitution-graph-correctness-target-v1",
        )
        self.assertEqual(self.targets.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.targets.codebook_path, str(CODEBOOK))
        self.assertEqual(self.targets.substitution_graph_targets_path, str(GRAPH_TARGETS))
        self.assertEqual(
            self.targets.formula_candidates_path,
            str(FORMULA_CANDIDATES),
        )
        self.assertEqual(
            self.targets.evaluation_examples_path,
            str(EVALUATION_EXAMPLES),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "formula-correctness-proof",
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
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
        self.assertEqual(
            target.target_id,
            "AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET",
        )
        self.assertEqual(
            target.graph_target_id,
            "AS-SUBSTITUTION-GRAPH-DELTA0-TARGET",
        )
        self.assertEqual(
            target.formula_candidate_id,
            "AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA",
        )
        self.assertEqual(target.relation_name, "subst_code_graph")
        self.assertEqual(target.formula_class, "delta0")
        self.assertEqual(target.status, "correctness-proof-not-constructed")
        self.assertEqual(
            target.checked_evaluation_example_ids,
            (
                "AS-SUBST-GRAPH-EVAL-N-EQ-ZERO",
                "AS-SUBST-GRAPH-EVAL-NESTED-SUBST-CODE",
                "AS-SUBST-GRAPH-EVAL-NOT-FREE",
            ),
        )

    def test_checked_in_manifest_validates_correctness_target(self):
        report = validate_substitution_graph_correctness_targets(
            self.targets,
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

    def test_json_payload_exposes_correctness_boundary(self):
        report = validate_substitution_graph_correctness_targets(
            self.targets,
            WILLARD_MAP,
        )

        payload = substitution_graph_correctness.substitution_graph_correctness_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["target_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["targets"][0]["observed_evaluation_example_count"], 3)
        self.assertTrue(payload["targets"][0]["observed_all_examples_hold"])
        self.assertIn(
            "formula-correctness-proof",
            payload["targets"][0]["required_future_work"],
        )

    def test_text_report_exposes_correctness_boundary(self):
        report = validate_substitution_graph_correctness_targets(
            self.targets,
            WILLARD_MAP,
        )

        text = substitution_graph_correctness.format_substitution_graph_correctness_report(report)

        self.assertIn("Substitution graph correctness targets: accepted", text)
        self.assertIn("AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET", text)
        self.assertIn("Status: correctness-proof-not-constructed", text)
        self.assertIn("Formula candidate: AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA", text)
        self.assertIn("Finite examples: 3", text)
        self.assertIn("Future work:", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_formula_candidate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["formula_candidate_id"] = "AS-UNKNOWN-FORMULA"
            path.write_text(json.dumps(data), encoding="utf-8")
            targets = load_substitution_graph_correctness_targets(path)

            report = validate_substitution_graph_correctness_targets(targets, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-formula", report.failed_subjects)
        self.assertTrue(
            any("unknown formula candidate" in result.detail for result in report.results)
        )

    def test_missing_evaluation_example_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["checked_evaluation_example_ids"].append(
                "AS-UNKNOWN-EVALUATION-EXAMPLE"
            )
            path.write_text(json.dumps(data), encoding="utf-8")
            targets = load_substitution_graph_correctness_targets(path)

            report = validate_substitution_graph_correctness_targets(targets, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-evaluation", report.failed_subjects)
        self.assertTrue(
            any("unknown evaluation example" in result.detail for result in report.results)
        )

    def test_missing_non_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["non_claims"] = data["targets"][0]["non_claims"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            targets = load_substitution_graph_correctness_targets(path)

            report = validate_substitution_graph_correctness_targets(targets, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-non-claim", report.failed_subjects)
        self.assertTrue(
            any("missing non-claims" in result.detail for result in report.results)
        )

    def test_proved_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["status"] = "formula-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            targets = load_substitution_graph_correctness_targets(path)

            report = validate_substitution_graph_correctness_targets(targets, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-correctness-status", report.failed_subjects)
        self.assertTrue(
            any("proved formula correctness is not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_correctness.run_substitution_graph_correctness_cli(
                ["--targets", str(TARGETS), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph correctness targets: accepted", output)

    def test_cli_returns_json_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_correctness.run_substitution_graph_correctness_cli(
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
        self.assertEqual(payload["target_count"], 1)

    def test_module_execution_runs_correctness_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_correctness"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Substitution graph correctness targets: accepted", completed.stdout)

    def test_module_execution_runs_json_correctness_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_correctness",
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
