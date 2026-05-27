import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from autarkic_systems import fixed_point_construction_obligation_graph
from autarkic_systems.fixed_point_construction_obligation_graph import (
    REQUIRED_GRAPH_EDGES,
    REQUIRED_NON_CLAIMS,
    load_fixed_point_construction_obligation_graph,
    validate_fixed_point_construction_obligation_graph,
)


GRAPH = Path("claims/fixed_point_construction_obligation_graph.json")
CONSTRUCTION_CASES = Path("claims/fixed_point_construction_cases.json")
CONSTRUCTION_FRONTIER = Path("claims/fixed_point_construction_frontier_status.json")
WILLARD_MAP = Path("sources/willard_definition_map.json")


class FixedPointConstructionObligationGraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = load_fixed_point_construction_obligation_graph(GRAPH)

    def test_checked_in_manifest_names_obligation_graph_inputs(self):
        self.assertEqual(self.graph.schema_version, 1)
        self.assertEqual(
            self.graph.graph_id,
            "as-fixed-point-construction-obligation-graph-v1",
        )
        self.assertEqual(
            self.graph.fixed_point_construction_cases_path,
            str(CONSTRUCTION_CASES),
        )
        self.assertEqual(
            self.graph.fixed_point_construction_frontier_status_path,
            str(CONSTRUCTION_FRONTIER),
        )
        self.assertEqual(self.graph.frontier_status, "blocked")
        self.assertEqual(self.graph.frontier_blocked_by, "fixed-point-construction")
        self.assertEqual(self.graph.expected_node_count, 5)
        self.assertEqual(self.graph.expected_edge_count, 6)
        self.assertEqual(self.graph.required_edges, REQUIRED_GRAPH_EDGES)
        self.assertEqual(
            REQUIRED_GRAPH_EDGES,
            (
                ("diagonal-instance-closure", "substitution-representability-proof"),
                ("diagonal-instance-closure", "bridge-equality-proof"),
                (
                    "substitution-graph-correctness-proof",
                    "substitution-representability-proof",
                ),
                (
                    "substitution-representability-proof",
                    "bridge-equality-proof",
                ),
                (
                    "substitution-graph-correctness-proof",
                    "bridge-equality-proof",
                ),
                ("bridge-equality-proof", "fixed-point-equation-lifting"),
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

    def test_checked_in_manifest_validates_obligation_graph(self):
        report = validate_fixed_point_construction_obligation_graph(
            self.graph,
            WILLARD_MAP,
        )

        self.assertTrue(report.accepted, report.results)
        self.assertEqual(report.failed_subjects, ())
        self.assertEqual(report.node_count, 5)
        self.assertEqual(report.edge_count, 6)
        self.assertTrue(report.acyclic)
        self.assertEqual(
            report.root_case_kinds,
            ("diagonal-instance-closure", "substitution-graph-correctness-proof"),
        )
        self.assertEqual(report.terminal_case_kinds, ("fixed-point-equation-lifting",))
        self.assertEqual(
            tuple(node.case_kind for node in report.nodes),
            (
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
                "substitution-representability-proof",
                "bridge-equality-proof",
                "fixed-point-equation-lifting",
            ),
        )
        self.assertTrue(all(node.status == "proof-case-open" for node in report.nodes))

    def test_json_payload_exposes_checked_graph_without_promoting_proofs(self):
        report = validate_fixed_point_construction_obligation_graph(
            self.graph,
            WILLARD_MAP,
        )

        payload = (
            fixed_point_construction_obligation_graph
            .fixed_point_construction_obligation_graph_payload(report)
        )

        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["frontier_status"], "blocked")
        self.assertEqual(payload["frontier_blocked_by"], "fixed-point-construction")
        self.assertEqual(payload["failed_subjects"], [])
        self.assertEqual(payload["node_count"], 5)
        self.assertEqual(payload["edge_count"], 6)
        self.assertTrue(payload["acyclic"])
        self.assertEqual(
            payload["root_case_kinds"],
            ["diagonal-instance-closure", "substitution-graph-correctness-proof"],
        )
        self.assertEqual(
            payload["terminal_case_kinds"],
            ["fixed-point-equation-lifting"],
        )
        self.assertEqual(
            [node["case_kind"] for node in payload["nodes"]],
            [
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
                "substitution-representability-proof",
                "bridge-equality-proof",
                "fixed-point-equation-lifting",
            ],
        )
        self.assertEqual(
            [(edge["from"], edge["to"]) for edge in payload["edges"]],
            list(REQUIRED_GRAPH_EDGES),
        )
        self.assertIn("no fixed-point equation proof", payload["non_claims"])

    def test_text_report_exposes_next_open_obligations(self):
        report = validate_fixed_point_construction_obligation_graph(
            self.graph,
            WILLARD_MAP,
        )

        text = (
            fixed_point_construction_obligation_graph
            .format_fixed_point_construction_obligation_graph_report(report)
        )

        self.assertIn("Fixed-point construction obligation graph: accepted", text)
        self.assertIn("Frontier: blocked by fixed-point-construction", text)
        self.assertIn("Nodes: 5", text)
        self.assertIn("Edges: 6", text)
        self.assertIn(
            "Root cases: diagonal-instance-closure, "
            "substitution-graph-correctness-proof",
            text,
        )
        self.assertIn("Terminal cases: fixed-point-equation-lifting", text)
        self.assertIn("diagonal-instance-closure -> bridge-equality-proof", text)
        self.assertIn("Non-claims: no substitution representability proof", text)
        self.assertNotIn("proved", text.lower())
        self.assertNotIn("FAIL", text)

    def test_stale_graph_edge_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "graph.json"
            data = json.loads(GRAPH.read_text(encoding="utf-8"))
            data["required_edges"] = data["required_edges"][:-1]
            path.write_text(json.dumps(data), encoding="utf-8")
            graph = load_fixed_point_construction_obligation_graph(path)

            report = validate_fixed_point_construction_obligation_graph(
                graph,
                WILLARD_MAP,
            )

        self.assertFalse(report.accepted)
        self.assertIn(
            "fixed-point-construction-obligation-graph-edges",
            report.failed_subjects,
        )
        self.assertTrue(
            any("required edge mismatch" in result.detail for result in report.results)
        )

    def test_cli_returns_json_for_checked_in_graph(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = (
                fixed_point_construction_obligation_graph
                .run_fixed_point_construction_obligation_graph_cli(
                    [
                        "--graph",
                        str(GRAPH),
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
            payload["graph_id"],
            "as-fixed-point-construction-obligation-graph-v1",
        )


if __name__ == "__main__":
    unittest.main()
