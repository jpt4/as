import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from autarkic_systems.schematic_trace import load_schematic_trace
from autarkic_systems.schematic_svg import (
    RECIPIENT_WRITE_BUFFER_COMMAND_MESSAGE_SVG_ARTIFACT,
    SVG_NAMESPACE,
    render_schematic_svg,
    validate_schematic_svg,
)


TRACE_ARTIFACT = Path("schematics/recipient_write_buffer_command_message_trace.json")


class RecipientWriteBufferCommandMessageSvgTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_schematic_trace(TRACE_ARTIFACT)
        self.svg_text = render_schematic_svg(self.trace)

    def test_svg_is_nonblank_xml_with_trace_metadata(self):
        self.assertGreater(len(self.svg_text), 1000)

        root = ET.fromstring(self.svg_text)

        self.assertEqual(root.tag, f"{{{SVG_NAMESPACE}}}svg")
        self.assertEqual(root.attrib["data-artifact-id"], self.trace.artifact_id)
        self.assertEqual(root.attrib["data-trace-id"], self.trace.trace.trace_id)

    def test_svg_records_recipient_write_buffer_details_and_flow(self):
        self.assertIn("role: wire", self.svg_text)
        self.assertIn("role after: wire", self.svg_text)
        self.assertIn("memory before: right", self.svg_text)
        self.assertIn("memory after: right", self.svg_text)
        self.assertIn(
            "status: recipient-write-buffer-command-message-appended",
            self.svg_text,
        )
        self.assertIn("transition: step_fixed_cell", self.svg_text)
        self.assertIn("upstream before: [write-buf-zero, _, _]", self.svg_text)
        self.assertIn("upstream after: [_, _, _]", self.svg_text)
        self.assertIn("input after: [_, _, _]", self.svg_text)
        self.assertIn("output after: [_, _, _]", self.svg_text)
        self.assertIn("control before: []", self.svg_text)
        self.assertIn("control after: []", self.svg_text)
        self.assertIn("buffer before: [1]", self.svg_text)
        self.assertIn("buffer after: [1, 0]", self.svg_text)
        root = ET.fromstring(self.svg_text)
        visible_text = "\n".join(root.itertext())
        for flow in self.trace.trace.routed_signal_flow:
            with self.subTest(flow=flow):
                self.assertIn(flow, visible_text)

    def test_committed_svg_matches_renderer_output(self):
        committed = RECIPIENT_WRITE_BUFFER_COMMAND_MESSAGE_SVG_ARTIFACT.read_text(
            encoding="utf-8",
        )

        self.assertEqual(committed, self.svg_text)

    def test_svg_validator_accepts_committed_svg(self):
        results = validate_schematic_svg(
            self.trace,
            svg_text=RECIPIENT_WRITE_BUFFER_COMMAND_MESSAGE_SVG_ARTIFACT.read_text(
                encoding="utf-8",
            ),
        )

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_svg_validator_rejects_drifted_buffer(self):
        drifted = self.svg_text.replace(
            "buffer after: [1, 0]",
            "buffer after: [1, 1]",
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
