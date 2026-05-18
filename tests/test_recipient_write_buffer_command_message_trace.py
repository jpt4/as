import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    RECIPIENT_WRITE_BUFFER_COMMAND_MESSAGE_TRACE_ARTIFACT_ID,
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)


ARTIFACT = Path("schematics/recipient_write_buffer_command_message_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")
STATUS = "recipient-write-buffer-command-message-appended"


class RecipientWriteBufferCommandMessageTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_recipient_write_buffer_command_message_trace(self):
        self.assertEqual(
            RECIPIENT_WRITE_BUFFER_COMMAND_MESSAGE_TRACE_ARTIFACT_ID,
            "recipient-write-buffer-command-message-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            RECIPIENT_WRITE_BUFFER_COMMAND_MESSAGE_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.trace.transition_function, "step_fixed_cell")

    def test_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_trace_records_upstream_write_buffer_append(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "wire")
        self.assertEqual(before["memory"], "right")
        self.assertEqual(before["upstream"], ["write-buf-zero", "_", "_"])
        self.assertEqual(before["input"], ["_", "_", "_"])
        self.assertEqual(before["buffer"], [1])
        self.assertEqual(after["role"], "wire")
        self.assertEqual(after["memory"], "right")
        self.assertEqual(after["upstream"], ["_", "_", "_"])
        self.assertEqual(after["input"], ["_", "_", "_"])
        self.assertEqual(after["output"], ["_", "_", "_"])
        self.assertEqual(after["self_mailbox"], "_")
        self.assertEqual(after["control"], [])
        self.assertEqual(after["buffer"], [1, 0])
        self.assertEqual(self.trace.trace.expected_status, STATUS)

    def test_trace_records_write_buffer_command_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "upstream[write-buf-zero] -> input[0]",
                "command[write-buf-zero] -> append 0",
                "buffer[1] -> buffer[1,0]",
                "command[write-buf-zero] consumed -> _",
                "upstream cleared; command state cleared",
            ),
        )

    def test_trace_executes_against_current_runtime(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_appended_buffer_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["buffer"] = [1, 1]
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
                and result.subject == "recipient-write-buffer-command-message"
                for result in results
            ),
            results,
        )

    def test_drifted_write_buffer_flow_is_rejected(self):
        drifted = replace(
            self.trace,
            trace=replace(
                self.trace.trace,
                routed_signal_flow=("command[write-buf-zero] -> append 1",),
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
