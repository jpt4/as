import unittest
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    SINGLE_NODE_TRACE_ARTIFACT_ID,
    execute_schematic_trace,
    load_single_node_schematic_trace,
    validate_single_node_schematic_trace,
)


ARTIFACT = Path("schematics/single_node_triangular_rlem_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class SingleNodeSchematicTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_single_node_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_matches_adr_0015_recommended_next_artifact(self):
        self.assertEqual(
            SINGLE_NODE_TRACE_ARTIFACT_ID,
            "single-node-triangular-rlem-schematic-and-uc-transition-trace",
        )
        self.assertEqual(self.trace.artifact_id, SINGLE_NODE_TRACE_ARTIFACT_ID)
        self.assertEqual(
            self.trace.artifact_id,
            self.witness_map.recommended_next_artifact,
        )

    def test_schematic_names_three_oriented_ports(self):
        self.assertEqual(len(self.trace.schematic.ports), 3)

        orientations = {port.orientation for port in self.trace.schematic.ports}
        signal_indices = {port.signal_index for port in self.trace.schematic.ports}

        self.assertEqual(orientations, {"north", "east", "west"})
        self.assertEqual(signal_indices, {0, 1, 2})
        for port in self.trace.schematic.ports:
            with self.subTest(port=port.port_id):
                self.assertTrue(port.label)
                self.assertIn(port.signal_index, (0, 1, 2))

    def test_schematic_distinguishes_required_interpretive_layers(self):
        layer_ids = tuple(layer.layer_id for layer in self.trace.schematic.layers)

        self.assertEqual(REQUIRED_INTERPRETIVE_LAYERS, layer_ids)
        for layer in self.trace.schematic.layers:
            with self.subTest(layer=layer.layer_id):
                self.assertTrue(layer.summary)
                self.assertTrue(layer.boundary)

    def test_schematic_memory_direction_matches_recorded_signal_flow(self):
        self.assertEqual(self.trace.schematic.geometry, "triangular-rlem-node")
        self.assertEqual(
            self.trace.schematic.memory_direction,
            self.trace.trace.before_cell["memory"],
        )
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "input[2] -> output[0]",
                "input[0] -> output[1]",
                "input[1] -> output[2]",
            ),
        )

    def test_trace_maps_all_current_cell_fields(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)

        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell
        for field in REQUIRED_CELL_FIELDS:
            with self.subTest(field=field):
                self.assertIn(field, before)
                self.assertIn(field, after)

    def test_trace_executes_against_existing_universal_cell_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_artifact_validates_against_witness_map(self):
        results = validate_single_node_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_missing_interpretive_layer_is_rejected(self):
        incomplete = self.trace.without_interpretive_layer(
            "candidate-physical-implementation"
        )

        results = validate_single_node_schematic_trace(
            incomplete,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "candidate-physical-implementation"
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
