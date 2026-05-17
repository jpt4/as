import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    RECIPIENT_NON_INIT_COMMAND_REJECTION_TRACE_ARTIFACT_ID,
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)
from autarkic_systems.transition_predicates import (
    recipient_non_init_command_message_rejected,
)
from autarkic_systems.universal_cell import Cell, step_fixed_cell


ARTIFACT = Path("schematics/recipient_non_init_command_rejection_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class RecipientNonInitCommandRejectionTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_recipient_non_init_command_rejection_trace(self):
        self.assertEqual(
            RECIPIENT_NON_INIT_COMMAND_REJECTION_TRACE_ARTIFACT_ID,
            "recipient-non-init-command-rejection-schematic-and-uc-transition-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            RECIPIENT_NON_INIT_COMMAND_REJECTION_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.trace.transition_function, "step_fixed_cell")

    def test_rejection_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_rejection_trace_records_upstream_standard_signal_rejection(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "proc")
        self.assertEqual(before["memory"], "left")
        self.assertEqual(before["upstream"], ["_", "standard-signal", "_"])
        self.assertEqual(before["input"], ["_", "_", "_"])
        self.assertEqual(before["output"], ["_", "_", "_"])
        self.assertEqual(after["role"], "proc")
        self.assertEqual(after["memory"], "left")
        self.assertEqual(after["upstream"], ["_", "_", "_"])
        self.assertEqual(after["input"], ["_", "_", "_"])
        self.assertEqual(after["output"], ["_", "_", "_"])
        self.assertEqual(after["automail"], "_")
        self.assertEqual(after["self_mailbox"], "_")
        self.assertEqual(after["control"], [])
        self.assertEqual(after["buffer"], [])
        self.assertEqual(self.trace.trace.expected_status, "rejected-input")

    def test_rejection_trace_records_upstream_rejection_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "upstream[standard-signal] -> input[1]",
                "command[standard-signal] rejected as recipient non-init command-message",
                "role/memory preserved",
                "upstream cleared; input/output cleared",
                "command side state preserved",
            ),
        )

    def test_rejection_trace_executes_against_existing_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_rejection_trace_satisfies_named_transition_claim(self):
        before = self.trace.trace.before_cell
        before_cell = Cell(
            role=before["role"],
            memory=before["memory"],
            upstream=tuple(before["upstream"]),
            input=tuple(before["input"]),
            output=tuple(before["output"]),
            automail=before["automail"],
            self_mailbox=before["self_mailbox"],
            control=tuple(before["control"]),
            buffer=tuple(before["buffer"]),
        )

        predicate = recipient_non_init_command_message_rejected(
            before_cell,
            step_fixed_cell(before_cell),
        )

        self.assertTrue(predicate.holds, predicate.detail)

    def test_rejection_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_rejection_role_change_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["role"] = "wire"
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
                and result.subject == "recipient-non-init-command-message-rejection"
                for result in results
            ),
            results,
        )

    def test_drifted_uncleared_upstream_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["upstream"] = ["_", "standard-signal", "_"]
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
                and result.subject == "recipient-non-init-command-message-rejection"
                for result in results
            ),
            results,
        )

    def test_drifted_rejection_flow_is_rejected(self):
        drifted = replace(
            self.trace,
            trace=replace(
                self.trace.trace,
                routed_signal_flow=("command[standard-signal] executed",),
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
