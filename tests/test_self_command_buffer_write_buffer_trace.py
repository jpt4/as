import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    SELF_COMMAND_BUFFER_WRITE_BUFFER_TRACE_ARTIFACT_ID,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)


ARTIFACT = Path("schematics/self_command_buffer_write_buffer_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class SelfCommandBufferWriteBufferTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_self_command_buffer_write_buffer_trace(self):
        self.assertEqual(
            SELF_COMMAND_BUFFER_WRITE_BUFFER_TRACE_ARTIFACT_ID,
            "self-command-buffer-write-buffer-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            SELF_COMMAND_BUFFER_WRITE_BUFFER_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.trace.transition_function, "step_stem_cell")

    def test_write_buffer_command_buffer_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_write_buffer_command_buffer_trace_records_self_write_buffer_one(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "stem")
        self.assertEqual(before["memory"], "left")
        self.assertEqual(before["automail"], "_")
        self.assertEqual(before["self_mailbox"], "_")
        self.assertEqual(before["input"], [0, 1, 0])
        self.assertEqual(before["control"], [0, 1, 0])
        self.assertEqual(before["buffer"], [0, 0, 1, 1])
        self.assertEqual(after["role"], "stem")
        self.assertEqual(after["memory"], "left")
        self.assertEqual(after["self_mailbox"], "_")
        self.assertEqual(after["control"], [0, 1, 0])
        self.assertEqual(after["buffer"], [1])
        self.assertEqual(
            self.trace.trace.expected_status,
            "stem-command-buffer-self-write-buffer-appended",
        )

    def test_write_buffer_command_buffer_trace_records_decode_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "control[0,1,0] active",
                "input[0,1,0] matches control -> append 1",
                "buffer[0,0,1,1] -> buffer[0,0,1,1,1]",
                "decode value 7 -> self/write-buf-one",
                "self command[write-buf-one] -> append 1",
                "command buffer consumed; buffer reset to literal append",
                "control preserved",
            ),
        )

    def test_write_buffer_command_buffer_trace_executes_against_existing_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_write_buffer_command_buffer_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_command_buffer_write_bit_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["buffer"] = [0]
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
                and result.subject == "self-command-buffer-write-buffer"
                for result in results
            ),
            results,
        )

    def test_drifted_command_buffer_control_clear_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["control"] = []
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
                and result.subject == "self-command-buffer-write-buffer"
                for result in results
            ),
            results,
        )

    def test_drifted_write_buffer_decode_flow_is_rejected(self):
        drifted = replace(
            self.trace,
            trace=replace(
                self.trace.trace,
                routed_signal_flow=("decode value 7 -> neighbor-a/write-buf-one",),
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
