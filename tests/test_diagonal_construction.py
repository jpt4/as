import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import diagonal_construction
from autarkic_systems.diagonal_construction import (
    REQUIRED_FUTURE_WORK,
    REQUIRED_WILLARD_ANCHORS,
    build_diagonal_instance_code,
    build_diagonal_seed_node,
    load_diagonal_construction_targets,
    validate_diagonal_construction_targets,
)
from autarkic_systems.fixed_point import load_fixed_point_targets
from autarkic_systems.formal_code import encode_node, load_formal_codebook
from autarkic_systems.formal_substitution import free_variables


TARGETS = Path("claims/diagonal_construction_targets.json")
FIXED_POINT_TARGETS = Path("claims/fixed_point_targets.json")
CODEBOOK = Path("language/formal_codebook.json")
LANGUAGE = Path("language/formal_arithmetic_language.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class DiagonalConstructionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load_diagonal_construction_targets(TARGETS)

    def test_checked_in_manifest_names_diagonal_seed_surface(self):
        target = self.manifest.constructions[0]

        self.assertEqual(self.manifest.schema_version, 1)
        self.assertEqual(
            self.manifest.construction_set_id,
            "as-diagonal-construction-target-v1",
        )
        self.assertEqual(self.manifest.fixed_point_targets_path, str(FIXED_POINT_TARGETS))
        self.assertEqual(self.manifest.codebook_path, str(CODEBOOK))
        self.assertEqual(
            REQUIRED_WILLARD_ANCHORS,
            (
                "W2011-D3.4-GENERIC-CONFIGURATION",
                "W2011-D5.7-SELFCONSK",
                "W2020-D3.2-SELF-JUSTIFYING-GENAC",
            ),
        )
        self.assertEqual(
            REQUIRED_FUTURE_WORK,
            (
                "substitution-representability-proof",
                "diagonal-lemma-proof",
                "fixed-point-equation-proof",
                "self-consistency-theorem",
            ),
        )
        self.assertEqual(
            target.construction_id,
            "AS-FIXED-POINT-SELFCONS1-DIAGONAL-SEED",
        )
        self.assertEqual(target.target_id, "AS-FIXED-POINT-SELFCONS1-TARGET")
        self.assertEqual(target.substitution_term_kind, "substitution_code")
        self.assertEqual(target.status, "diagonal-seed-not-proved")
        self.assertEqual(target.expected_seed_code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))
        self.assertEqual(target.expected_seed_free_variables, ("n",))
        self.assertEqual(target.expected_instance_code_length, 296)
        self.assertEqual(
            target.expected_instance_code_prefix,
            (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13),
        )
        self.assertEqual(target.expected_instance_free_variables, ())
        self.assertIn("no diagonal lemma proof", target.non_claims)

    def test_build_diagonal_seed_uses_substitution_code_term(self):
        fixed_point_targets = load_fixed_point_targets(FIXED_POINT_TARGETS)
        fixed_point_target = fixed_point_targets.targets[0]
        codebook = load_formal_codebook(CODEBOOK)

        seed = build_diagonal_seed_node(fixed_point_target)
        seed_code = encode_node(seed, codebook)

        self.assertEqual(seed["body"]["right"]["kind"], "substitution_code")
        self.assertEqual(seed["body"]["right"]["left"], {"kind": "variable", "name": "n"})
        self.assertEqual(seed["body"]["right"]["right"], {"kind": "variable", "name": "n"})
        self.assertEqual(seed_code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))
        self.assertEqual(free_variables(seed), frozenset({"n"}))

    def test_build_diagonal_instance_quotes_seed_code(self):
        code = build_diagonal_instance_code(
            construction_id="AS-FIXED-POINT-SELFCONS1-DIAGONAL-SEED",
            targets_path=TARGETS,
            fixed_point_targets_path=FIXED_POINT_TARGETS,
            codebook_path=CODEBOOK,
        )

        self.assertEqual(len(code), 296)
        self.assertEqual(code[:12], (41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13))
        self.assertNotEqual(code, (41, 1, 22, 11, 1, 18, 11, 4, 11, 4))

    def test_checked_in_manifest_validates_diagonal_seed(self):
        report = validate_diagonal_construction_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.construction_count, 1)
        self.assertTrue(
            any(
                result.subject == "constructions"
                and result.accepted
                for result in report.results
            )
        )

    def test_json_payload_exposes_diagonal_seed_surface(self):
        report = validate_diagonal_construction_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        payload = diagonal_construction.diagonal_construction_report_payload(report)

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["construction_count"], 1)
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["constructions"][0]["status"], "diagonal-seed-not-proved")
        self.assertEqual(payload["constructions"][0]["observed_seed_code_length"], 10)
        self.assertEqual(payload["constructions"][0]["observed_instance_code_length"], 296)

    def test_text_report_exposes_diagonal_seed_surface(self):
        report = validate_diagonal_construction_targets(
            self.manifest,
            LANGUAGE,
            WILLARD_MAP,
        )

        text = diagonal_construction.format_diagonal_construction_report(report)

        self.assertIn("Diagonal construction targets: accepted", text)
        self.assertIn("AS-FIXED-POINT-SELFCONS1-DIAGONAL-SEED", text)
        self.assertIn("Status: diagonal-seed-not-proved", text)
        self.assertIn("Instance code length: 296", text)
        self.assertNotIn("FAIL", text)

    def test_unknown_fixed_point_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagonal.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["constructions"][0]["target_id"] = "UNKNOWN-TARGET"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_diagonal_construction_targets(path)

            report = validate_diagonal_construction_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("diagonal-construction-target", report.failed_subjects)
        self.assertTrue(
            any("unknown fixed-point target: UNKNOWN-TARGET" in result.detail for result in report.results)
        )

    def test_stale_seed_code_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagonal.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["constructions"][0]["expected_seed_code"] = [99]
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_diagonal_construction_targets(path)

            report = validate_diagonal_construction_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("diagonal-construction-seed", report.failed_subjects)
        self.assertTrue(
            any("seed code mismatch" in result.detail for result in report.results)
        )

    def test_proved_diagonal_status_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "diagonal.json"
            data = json.loads(TARGETS.read_text(encoding="utf-8"))
            data["constructions"][0]["status"] = "diagonal-lemma-proved"
            path.write_text(json.dumps(data), encoding="utf-8")
            manifest = load_diagonal_construction_targets(path)

            report = validate_diagonal_construction_targets(
                manifest,
                LANGUAGE,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn("diagonal-construction-status", report.failed_subjects)
        self.assertTrue(
            any("proved diagonal constructions are not supported" in result.detail for result in report.results)
        )

    def test_cli_returns_zero_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = diagonal_construction.run_diagonal_construction_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                ]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 0, output)
        self.assertIn("Diagonal construction targets: accepted", output)

    def test_cli_returns_json_for_checked_in_targets(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = diagonal_construction.run_diagonal_construction_cli(
                [
                    "--targets",
                    str(TARGETS),
                    "--language",
                    str(LANGUAGE),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["constructions"][0]["observed_instance_code_length"], 296)

    def test_module_execution_runs_diagonal_construction_validation(self):
        completed = subprocess.run(
            [sys.executable, "-m", "autarkic_systems.diagonal_construction"],
            check=False,
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Diagonal construction targets: accepted", completed.stdout)

    def test_module_execution_runs_json_diagonal_construction_validation(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.diagonal_construction",
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
        self.assertEqual(payload["construction_count"], 1)


if __name__ == "__main__":
    unittest.main()
