import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import substitution_graph_evaluation
from autarkic_systems.substitution_graph_evaluation import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_NON_CLAIMS,
    load_substitution_graph_evaluation_examples,
    validate_substitution_graph_evaluation_examples,
)


EXAMPLES = Path("claims/substitution_graph_evaluation_examples.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")
FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
FORMULA_CANDIDATES = Path("claims/substitution_graph_formula_candidates.json")


class SubstitutionGraphEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.examples = load_substitution_graph_evaluation_examples(EXAMPLES)

    def test_checked_in_manifest_names_finite_evaluation_set(self):
        first, second, third = self.examples.examples

        self.assertEqual(self.examples.schema_version, 1)
        self.assertEqual(
            self.examples.evaluation_set_id,
            "as-substitution-graph-evaluation-examples-v1",
        )
        self.assertEqual(self.examples.formal_language_path, str(FORMAL_LANGUAGE))
        self.assertEqual(self.examples.codebook_path, str(CODEBOOK))
        self.assertEqual(
            self.examples.formula_candidates_path,
            str(FORMULA_CANDIDATES),
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
        self.assertEqual(first.example_id, "AS-SUBST-GRAPH-EVAL-N-EQ-ZERO")
        self.assertEqual(first.variable, "n")
        self.assertEqual(first.argument_code, (11, 1))
        self.assertEqual(first.expected_formula_code, (21, 11, 4, 12))
        self.assertEqual(first.expected_formula_free_variables, ("n",))
        self.assertTrue(first.expected_relation_holds)
        self.assertEqual(first.expected_output_code_length, 19)
        self.assertEqual(
            first.expected_output_code_prefix,
            (21, 17, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13),
        )
        self.assertEqual(first.expected_output_free_variables, ())
        self.assertEqual(first.status, "finite-evaluation-not-proof")

        self.assertEqual(second.example_id, "AS-SUBST-GRAPH-EVAL-NESTED-SUBST-CODE")
        self.assertEqual(second.expected_formula_code, (21, 18, 11, 4, 11, 4, 11, 4))
        self.assertEqual(second.expected_output_code_length, 56)
        self.assertEqual(third.example_id, "AS-SUBST-GRAPH-EVAL-NOT-FREE")
        self.assertEqual(third.expected_output_code_length, 4)
        self.assertEqual(third.expected_output_free_variables, ("x",))

    def test_checked_in_manifest_validates_examples(self):
        report = validate_substitution_graph_evaluation_examples(
            self.examples,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.example_count, 3)
        self.assertTrue(
            any(
                result.subject == "examples"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_evaluated_examples(self):
        report = validate_substitution_graph_evaluation_examples(
            self.examples,
            WILLARD_MAP,
        )

        payload = substitution_graph_evaluation.substitution_graph_evaluation_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["example_count"], 3)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertTrue(payload["examples"][0]["observed_relation_holds"])
        self.assertEqual(payload["examples"][0]["observed_output_code_length"], 19)
        self.assertEqual(payload["examples"][1]["observed_output_code_length"], 56)
        self.assertEqual(payload["examples"][2]["observed_output_free_variables"], ["x"])

    def test_text_report_exposes_evaluation_boundary(self):
        report = validate_substitution_graph_evaluation_examples(
            self.examples,
            WILLARD_MAP,
        )

        text = substitution_graph_evaluation.format_substitution_graph_evaluation_report(report)

        self.assertIn("Substitution graph evaluation examples: accepted", text)
        self.assertIn("Examples: 3", text)
        self.assertIn("AS-SUBST-GRAPH-EVAL-N-EQ-ZERO", text)
        self.assertIn("Relation holds: true", text)
        self.assertIn("Output code length: 19", text)
        self.assertNotIn("FAIL", text)

    def test_stale_formula_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_formula_code"] = [21, 11, 4]
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_substitution_graph_evaluation_examples(path)

            report = validate_substitution_graph_evaluation_examples(examples, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-evaluation-formula", report.failed_subjects)
        self.assertTrue(
            any("formula code mismatch" in result.detail for result in report.results)
        )

    def test_stale_output_length_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_output_code_length"] = 296
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_substitution_graph_evaluation_examples(path)

            report = validate_substitution_graph_evaluation_examples(examples, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-evaluation-output", report.failed_subjects)
        self.assertTrue(
            any("output code length mismatch" in result.detail for result in report.results)
        )

    def test_false_relation_expectation_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["expected_relation_holds"] = False
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_substitution_graph_evaluation_examples(path)

            report = validate_substitution_graph_evaluation_examples(examples, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-evaluation-relation", report.failed_subjects)
        self.assertTrue(
            any("relation truth mismatch" in result.detail for result in report.results)
        )

    def test_proved_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "examples.json"
            data = json.loads(EXAMPLES.read_text(encoding="utf-8"))
            data["examples"][0]["status"] = "formula-correctness-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            examples = load_substitution_graph_evaluation_examples(path)

            report = validate_substitution_graph_evaluation_examples(examples, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("substitution-graph-evaluation-status", report.failed_subjects)
        self.assertTrue(
            any("proved formula correctness is not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_evaluation.run_substitution_graph_evaluation_cli(
                ["--examples", str(EXAMPLES), "--willard-map", str(WILLARD_MAP)]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Substitution graph evaluation examples: accepted", output)

    def test_cli_returns_json_for_checked_in_examples(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = substitution_graph_evaluation.run_substitution_graph_evaluation_cli(
                [
                    "--examples",
                    str(EXAMPLES),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["example_count"], 3)

    def test_module_execution_runs_evaluation_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.substitution_graph_evaluation"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Substitution graph evaluation examples: accepted", completed.stdout)

    def test_module_execution_runs_json_evaluation_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.substitution_graph_evaluation",
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
        self.assertEqual(payload["example_count"], 3)


if __name__ == "__main__":
    unittest.main()
