import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_frontier_selector
from autarkic_systems.fixed_point_frontier_selector import (
    REQUIRED_DEFERRED_CASE_KINDS,
    REQUIRED_NON_CLAIMS,
    REQUIRED_SELECTED_CASE_KINDS,
    load_fixed_point_frontier_selector,
    validate_fixed_point_frontier_selector,
)


SELECTOR = Path("claims/fixed_point_frontier_selector.json")
OBLIGATION_GRAPH = Path("claims/fixed_point_construction_obligation_graph.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointFrontierSelectorTests(unittest.TestCase):
    def setUp(self):
        self.selector = load_fixed_point_frontier_selector(SELECTOR)

    def test_checked_in_manifest_names_current_open_root_frontier(self):
        self.assertEqual(self.selector.schema_version, 1)
        self.assertEqual(
            self.selector.selector_id,
            "as-fixed-point-frontier-selector-v1",
        )
        self.assertEqual(
            self.selector.fixed_point_construction_obligation_graph_path,
            str(OBLIGATION_GRAPH),
        )
        self.assertEqual(
            self.selector.selection_policy,
            "open-root-obligations-before-dependent-cases",
        )
        self.assertEqual(self.selector.frontier_status, "blocked")
        self.assertEqual(self.selector.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(self.selector.expected_selected_count, 2)
        self.assertEqual(self.selector.expected_deferred_count, 3)
        self.assertEqual(
            self.selector.expected_selected_case_kinds,
            REQUIRED_SELECTED_CASE_KINDS,
        )
        self.assertEqual(
            self.selector.expected_deferred_case_kinds,
            REQUIRED_DEFERRED_CASE_KINDS,
        )
        self.assertEqual(
            REQUIRED_SELECTED_CASE_KINDS,
            (
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
            ),
        )
        self.assertEqual(
            REQUIRED_DEFERRED_CASE_KINDS,
            (
                "substitution-representability-proof",
                "bridge-equality-proof",
                "fixed-point-equation-lifting",
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

    def test_checked_in_manifest_validates_frontier_selector(self):
        report = validate_fixed_point_frontier_selector(
            self.selector,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.frontier_status, "blocked")
        self.assertEqual(report.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(report.selected_count, 2)
        self.assertEqual(report.deferred_count, 3)
        self.assertEqual(report.selected_case_kinds, REQUIRED_SELECTED_CASE_KINDS)
        self.assertEqual(report.deferred_case_kinds, REQUIRED_DEFERRED_CASE_KINDS)
        self.assertTrue(all(item.status == "proof-case-open" for item in report.selected))
        self.assertTrue(all(item.status == "proof-case-open" for item in report.deferred))

    def test_json_payload_exposes_selected_and_deferred_open_obligations(self):
        report = validate_fixed_point_frontier_selector(
            self.selector,
            WILLARD_MAP,
        )

        payload = fixed_point_frontier_selector.fixed_point_frontier_selector_payload(
            report,
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-construction")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["selected_count"], 2)
        self.assertEqual(payload["deferred_count"], 3)
        self.assertEqual(
            [item["case_kind"] for item in payload["selected"]],
            list(REQUIRED_SELECTED_CASE_KINDS),
        )
        self.assertEqual(
            [item["case_kind"] for item in payload["deferred"]],
            list(REQUIRED_DEFERRED_CASE_KINDS),
        )
        self.assertEqual(
            payload["selected"][0]["blocking_predecessors"],
            [],
        )
        self.assertEqual(
            payload["deferred"][0]["blocking_predecessors"],
            [
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
            ],
        )
        self.assertIn("no self-consistency theorem", payload["non_claims"])

    def test_text_report_renders_non_promotional_frontier_selection(self):
        report = validate_fixed_point_frontier_selector(
            self.selector,
            WILLARD_MAP,
        )

        text = fixed_point_frontier_selector.format_fixed_point_frontier_selector_report(
            report,
        )

        self.assertIn("Fixed-point frontier selector: accepted", text)
        self.assertIn("Frontier: blocked by fixed-point-construction", text)
        self.assertIn("Selected open obligations: 2", text)
        self.assertIn("- diagonal-instance-closure: proof-case-open", text)
        self.assertIn(
            "- substitution-graph-correctness-proof: proof-case-open",
            text,
        )
        self.assertIn("Deferred open obligations: 3", text)
        self.assertIn(
            "- substitution-representability-proof: proof-case-open",
            text,
        )
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_selected_case_list_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "selector.json"
            data = json.loads(SELECTOR.read_text(encoding="utf-8"))
            data["expected_selected_case_kinds"] = data[
                "expected_selected_case_kinds"
            ][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            selector = load_fixed_point_frontier_selector(path)

            report = validate_fixed_point_frontier_selector(selector, WILLARD_MAP)

        self.assertFalse(report.accepted)
        self.assertIn("fixed-point-frontier-selector-selected", report.failed_subjects)
        self.assertTrue(
            any(
                "selected case mismatch" in result.detail
                for result in report.results
            )
        )

    def test_cli_returns_json_for_checked_in_selector(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = fixed_point_frontier_selector.run_fixed_point_frontier_selector_cli(
                [
                    "--selector",
                    str(SELECTOR),
                    "--willard-map",
                    str(WILLARD_MAP),
                    "--format",
                    "json",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0, payload)
        self.assertTrue(payload["accepted"])
        self.assertEqual(
            payload["selector_id"],
            "as-fixed-point-frontier-selector-v1",
        )


if __name__ == "__main__":
    unittest.main()
