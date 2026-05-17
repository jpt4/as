import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    NEIGHBOR_COMMAND_BUFFER_DELIVERY_TRACE_ARTIFACT_ID,
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)


ARTIFACT = Path("schematics/neighbor_command_buffer_delivery_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class NeighborCommandBufferDeliveryTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_neighbor_command_buffer_delivery_trace(self):
        self.assertEqual(
            NEIGHBOR_COMMAND_BUFFER_DELIVERY_TRACE_ARTIFACT_ID,
            "neighbor-command-buffer-delivery-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            NEIGHBOR_COMMAND_BUFFER_DELIVERY_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.trace.transition_function, "step_stem_cell")

    def test_neighbor_delivery_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_neighbor_delivery_trace_records_middle_channel_delivery(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "stem")
        self.assertEqual(before["automail"], "_")
        self.assertEqual(before["self_mailbox"], "_")
        self.assertEqual(before["input"], [1, 0, 0])
        self.assertEqual(before["control"], [1, 0, 0])
        self.assertEqual(before["buffer"], [1, 0, 1, 0])
        self.assertEqual(after["role"], "stem")
        self.assertEqual(after["memory"], "right")
        self.assertEqual(after["output"], ["_", "proc-l-init", "_"])
        self.assertEqual(after["control"], [])
        self.assertEqual(after["buffer"], [])
        self.assertEqual(
            self.trace.trace.expected_status,
            "stem-command-buffer-neighbor-delivered",
        )

    def test_neighbor_delivery_trace_records_decode_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "control[1,0,0] active",
                "input[1,0,0] matches control -> append 1",
                "buffer[1,0,1,0] -> buffer[1,0,1,0,1]",
                "decode value 21 -> neighbor-b/proc-l-init",
                "neighbor command[proc-l-init] -> output[1]",
                "command buffer delivered; control/buffer cleared",
            ),
        )

    def test_neighbor_delivery_trace_executes_against_existing_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_neighbor_delivery_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_output_channel_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["output"] = ["proc-l-init", "_", "_"]
        drifted = replace(
            self.trace,
            trace=replace(self.trace.trace, expected_after_cell=drifted_after),
        )

        results = validate_schematic_trace(
            drifted,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "neighbor-command-buffer-delivery"
                for result in results
            ),
            results,
        )

    def test_drifted_uncleared_command_state_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["buffer"] = [1, 0, 1, 0, 1]
        drifted = replace(
            self.trace,
            trace=replace(self.trace.trace, expected_after_cell=drifted_after),
        )

        results = validate_schematic_trace(
            drifted,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "neighbor-command-buffer-delivery"
                for result in results
            ),
            results,
        )

    def test_drifted_decode_flow_is_rejected(self):
        drifted = replace(
            self.trace,
            trace=replace(
                self.trace.trace,
                routed_signal_flow=("decode value 21 -> self/proc-l-init",),
            ),
        )

        results = validate_schematic_trace(
            drifted,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(
            any(
                not result.accepted and result.subject == "routed_signal_flow"
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
