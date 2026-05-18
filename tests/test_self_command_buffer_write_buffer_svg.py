import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from autarkic_systems.schematic_trace import load_schematic_trace
from autarkic_systems.schematic_svg import (
    SELF_COMMAND_BUFFER_WRITE_BUFFER_SVG_ARTIFACT,
    SVG_NAMESPACE,
    render_schematic_svg,
    validate_schematic_svg,
)


TRACE_ARTIFACT = Path("schematics/self_command_buffer_write_buffer_trace.json")


class SelfCommandBufferWriteBufferSvgTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(TRACE_ARTIFACT)
        self.svg_text = render_schematic_svg(self.trace)

    def test_svg_is_nonblank_xml_with_write_buffer_command_buffer_metadata(self):
        self.assertGreater(len(self.svg_text), 1000)

        root = ET.fromstring(self.svg_text)

        self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
        self.assertEqual(root.attrib["data-artifact-id"], self.trace.artifact_id)
        self.assertEqual(root.attrib["data-trace-id"], self.trace.trace.trace_id)

    def test_svg_labels_write_buffer_command_buffer_ports_from_trace(self):
        root = ET.fromstring(self.svg_text)
        ports = root.findall(f".//{{{SVG_NAMESPACE}}}g[@class='port']")

        self.assertEqual(len(ports), 3)
        self.assertEqual(
            {port.attrib["data-port-id"] for port in ports},
            {port.port_id for port in self.trace.schematic.ports},
        )
        self.assertEqual(
            {port.attrib["data-orientation"] for port in ports},
            {port.orientation for port in self.trace.schematic.ports},
        )

    def test_svg_records_command_buffer_write_buffer_append_and_flow(self):
        self.assertIn("role: stem", self.svg_text)
        self.assertIn("role after: stem", self.svg_text)
        self.assertIn("memory before: left", self.svg_text)
        self.assertIn("memory after: left", self.svg_text)
        self.assertIn(
            "status: stem-command-buffer-self-write-buffer-appended",
            self.svg_text,
        )
        self.assertIn("self_mailbox before: _", self.svg_text)
        self.assertIn("self_mailbox after: _", self.svg_text)
        self.assertIn("control before: [0, 1, 0]", self.svg_text)
        self.assertIn("control after: [0, 1, 0]", self.svg_text)
        self.assertIn("buffer before: [0, 0, 1, 1]", self.svg_text)
        self.assertIn("buffer after: [1]", self.svg_text)
        root = ET.fromstring(self.svg_text)
        visible_text = "\n".join(root.itertext())
        for flow in self.trace.trace.routed_signal_flow:
            with self.subTest(flow=flow):
                self.assertIn(flow, visible_text)

    def test_committed_command_buffer_write_buffer_svg_matches_renderer_output(self):
        committed = SELF_COMMAND_BUFFER_WRITE_BUFFER_SVG_ARTIFACT.read_text(
            encoding="utf-8"
        )

        self.assertEqual(committed, self.svg_text)

    def test_command_buffer_write_buffer_svg_validator_accepts_committed_svg(self):
        results = validate_schematic_svg(
            self.trace,
            svg_text=SELF_COMMAND_BUFFER_WRITE_BUFFER_SVG_ARTIFACT.read_text(
                encoding="utf-8"
            ),
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_command_buffer_write_buffer_svg_validator_rejects_drifted_control(self):
        drifted = self.svg_text.replace(
            "control after: [0, 1, 0]",
            "control after: []",
        )

        results = validate_schematic_svg(self.trace, svg_text=drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "rendered-svg"
                and "does not match" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
