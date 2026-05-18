import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import consistency_level
from autarkic_systems.consistency_level import (
    REQUIRED_WILLARD_ANCHORS,
    load_consistency_level_targets,
    validate_consistency_level_targets,
)


TARGETS = Path("claims/consistency_level_targets.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
CODEBOOK = Path("language/formal_codebook.json")
SUBSTITUTION = Path("language/formal_substitution_examples.json")
COMPLEMENT = Path("language/formal_complement_examples.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class ConsistencyLevelTargetTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_consistency_level_targets(TARGETS)

    def test_checked_in_manifest_selects_level_one_target(self):
        target = self.manifest.targets[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(self.manifest.target_set_id, "as-consistency-level-target-v1")
        self.assertEqual(self.manifest.language_path, str(LANGUAGE))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(self.manifest.substitution_examples_path, str(SUBSTITUTION))
        self.assertEqual(self.manifest.complement_examples_path, str(COMPLEMENT))
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D5.6-LEVEL-K-CONSISTENCY",
                "W2011-D5.7-SELFCONSK",
            ),
        )
        self.assertEqual(target.target_id, "AS-CONSISTENCY-LEVEL-1")
        self.assertEqual(target.level, 1)
        self.assertEqual(target.notion, "level-1-consistency")
        self.assertEqual(target.statement_class, "pi1")
        self.assertEqual(target.negation_class, "sigma1")
        self.assertEqual(target.status, "target-selected-not-claimed")

    def test_checked_in_manifest_validates_against_dependencies(self):
        report = validate_consistency_level_targets(
            self.manifest,
            LANGUAGE,
            CODEBOOK,
            SUBSTITUTION,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertTrue(
            any(
                result.subject == "targets" and result.accepted
                for result in report.results
            )
        )
        self.assertTrue(
            any(
                result.subject == "complement" and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_level_target(self):
        report = validate_consistency_level_targets(
            self.manifest,
            LANGUAGE,
            CODEBOOK,
            SUBSTITUTION,
            WILLARD_MAP,
        )

        payload = consistency_level.consistency_level_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["target_set_id"], "as-consistency-level-target-v1")
        self.assertEqual(payload["target_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["complement_examples_path"], str(COMPLEMENT))
        self.assertEqual(payload["targets"][0]["level"], 1)
        self.assertEqual(payload["targets"][0]["status"], "target-selected-not-claimed")

    def test_text_report_exposes_level_target(self):
        report = validate_consistency_level_targets(
            self.manifest,
            LANGUAGE,
            CODEBOOK,
            SUBSTITUTION,
            WILLARD_MAP,
        )

        text = consistency_level.format_consistency_level_report(report)

        self.assertIn("Consistency level targets: accepted", text)
        self.assertIn("Target set: as-consistency-level-target-v1", text)
        self.assertIn("AS-CONSISTENCY-LEVEL-1: level-1-consistency", text)
        self.assertIn("Status: target-selected-not-claimed", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_willard_anchor_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["willard_anchor_ids"].append("W2099-UNKNOWN")
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_consistency_level_targets(targets_path)

            report = validate_consistency_level_targets(
                manifest,
                LANGUAGE,
                CODEBOOK,
                SUBSTITUTION,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("consistency-level-willard-anchor", report.failed_subjects)
        self.assertTrue(
            any("unknown Willard anchor IDs: W2099-UNKNOWN" in result.detail for result in report.results)
        )

    def test_missing_sentence_class_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            language_path = Path(tmp) / "language.json"
            data = json.loads(LANGUAGE.read_text(encoding="utf-8"))
            del data["syntax_classes"]["sentences"]["classes"]["sigma1"]
            language_path.write_text(json.dumps(data), encoding="utf-8")

            report = validate_consistency_level_targets(
                self.manifest,
                language_path,
                CODEBOOK,
                SUBSTITUTION,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("consistency-level-sentence-class", report.failed_subjects)
        self.assertTrue(
            any("missing sentence classes: sigma1" in result.detail for result in report.results)
        )

    def test_proved_consistency_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets_path = Path(tmp) / "targets.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["targets"][0]["status"] = "proved"
            targets_path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_consistency_level_targets(targets_path)

            report = validate_consistency_level_targets(
                manifest,
                LANGUAGE,
                CODEBOOK,
                SUBSTITUTION,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("consistency-level-status", report.failed_subjects)
        self.assertTrue(
            any("proved consistency is not supported" in result.detail for result in report.results)
        )

    def test_missing_complement_examples_are_rejected(self):
        report = validate_consistency_level_targets(
            self.manifest,
            LANGUAGE,
            CODEBOOK,
            SUBSTITUTION,
            WILLARD_MAP,
            Path("language/missing_formal_complement_examples.json"),
        )

        self.assertFalse(report.accepted)
        self.assertIn("consistency-level-complement", report.failed_subjects)
        self.assertTrue(
            any("formal complement rejected" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = consistency_level.run_consistency_level_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--language",
                    str(LANGUAGE),
                    "--codebook",
                    str(CODEBOOK),
                    "--substitution",
                    str(SUBSTITUTION),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Consistency level targets: accepted", output)

    def test_cli_returns_json_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = consistency_level.run_consistency_level_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--language",
                    str(LANGUAGE),
                    "--codebook",
                    str(CODEBOOK),
                    "--substitution",
                    str(SUBSTITUTION),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["targets"][0]["level"], 1)

    def test_module_execution_runs_consistency_level_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.consistency_level"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Consistency level targets: accepted", completed.stdout)

    def test_module_execution_runs_json_consistency_level_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.consistency_level",
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
        self.assertEqual(payload["target_set_id"], "as-consistency-level-target-v1")


if __name__ == "__main__":
    unittest.main()
