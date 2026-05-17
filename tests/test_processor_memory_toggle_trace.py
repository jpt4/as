import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.prc_hardware_map import load_prc_hardware_witness_map
from autarkic_systems.schematic_trace import (
    PROCESSOR_MEMORY_TOGGLE_TRACE_ARTIFACT_ID,
    REQUIRED_CELL_FIELDS,
    REQUIRED_INTERPRETIVE_LAYERS,
    execute_schematic_trace,
    load_schematic_trace,
    validate_schematic_trace,
)


ARTIFACT = Path("schematics/processor_memory_toggle_trace.json")
WITNESS_MAP = Path("sources/prc_hardware_witness_map.json")


class ProcessorMemoryToggleTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(ARTIFACT)
        self.witness_map = load_prc_hardware_witness_map(WITNESS_MAP)

    def test_artifact_is_processor_memory_toggle_trace(self):
        self.assertEqual(
            PROCESSOR_MEMORY_TOGGLE_TRACE_ARTIFACT_ID,
            "processor-memory-toggle-schematic-and-uc-transition-trace",
        )
        self.assertEqual(self.trace.artifact_id, PROCESSOR_MEMORY_TOGGLE_TRACE_ARTIFACT_ID)
        self.assertEqual(self.trace.trace.transition_function, "step_fixed_cell")

    def test_processor_trace_uses_existing_schema_vocabulary(self):
        self.assertEqual(REQUIRED_CELL_FIELDS, self.trace.trace.cell_fields)
        self.assertEqual(
            REQUIRED_INTERPRETIVE_LAYERS,
            tuple(layer.layer_id for layer in self.trace.schematic.layers),
        )
        self.assertEqual(len(self.trace.schematic.ports), 3)

    def test_processor_trace_records_memory_toggle(self):
        before = self.trace.trace.before_cell
        after = self.trace.trace.expected_after_cell

        self.assertEqual(before["role"], "proc")
        self.assertEqual(after["role"], "proc")
        self.assertEqual(before["memory"], "left")
        self.assertEqual(after["memory"], "right")
        self.assertEqual(self.trace.schematic.memory_direction, "left")

    def test_processor_trace_records_left_memory_signal_flow(self):
        self.assertEqual(
            self.trace.trace.routed_signal_flow,
            (
                "input[1] -> output[0]",
                "input[2] -> output[1]",
                "input[0] -> output[2]",
            ),
        )

    def test_processor_trace_executes_against_existing_probe(self):
        execution = execute_schematic_trace(self.trace)

        self.assertEqual(execution.status, self.trace.trace.expected_status)
        self.assertEqual(execution.after_cell, self.trace.trace.expected_after_cell)

    def test_processor_trace_validates_against_witness_map(self):
        results = validate_schematic_trace(
            self.trace,
            hardware_witness_map=self.witness_map,
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_processor_memory_toggle_is_rejected(self):
        drifted_after = dict(self.trace.trace.expected_after_cell)
        drifted_after["memory"] = "left"
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
                and result.subject == "processor-memory-toggle"
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
