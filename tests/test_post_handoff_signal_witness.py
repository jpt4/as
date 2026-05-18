import contextlib
import io
import json
import subprocess
import sys
import unittest

from autarkic_systems.network_sequence import (
    execute_post_handoff_signal_witness,
    format_post_handoff_signal_witness,
    post_handoff_signal_witness_payload,
    run_network_sequence_cli,
)
from autarkic_systems.universal_cell import Cell


class PostHandoffSignalWitnessTests(unittest.TestCase):
    def test_init_delivery_followed_by_standard_signal_routes_through_recipient(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_post_handoff_signal_witness(
            sender,
            recipient,
            followup_input=(1, 0, 0),
        )

        self.assertTrue(witness.accepted, witness.detail)
        self.assertEqual(witness.status, "post-handoff-signal-routed")
        self.assertEqual(witness.delivery_witness.status, "neighbor-delivery-consumed")
        self.assertIsNotNone(witness.recipient_before_followup)
        self.assertEqual(witness.recipient_before_followup.role, "proc")
        self.assertEqual(witness.recipient_before_followup.memory, "left")
        self.assertEqual(witness.recipient_before_followup.input, (1, 0, 0))
        self.assertIsNotNone(witness.followup_result)
        self.assertEqual(witness.followup_result.status, "routed")
        self.assertEqual(witness.recipient_after_followup.output, (0, 0, 1))
        self.assertEqual(witness.recipient_after_followup.memory, "right")

    def test_write_buffer_delivery_is_not_an_init_handoff_for_followup_signal(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(0, 1, 0),
            control=(0, 1, 0),
            buffer=(1, 1, 1, 1),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_post_handoff_signal_witness(sender, recipient)

        self.assertFalse(witness.accepted)
        self.assertEqual(witness.status, "handoff-not-init-consumed")
        self.assertEqual(witness.delivery_witness.status, "neighbor-delivery-consumed")
        self.assertEqual(
            witness.delivery_witness.recipient_result.status,
            "recipient-write-buffer-command-message-appended",
        )
        self.assertIsNone(witness.recipient_before_followup)
        self.assertIsNone(witness.followup_result)

    def test_malformed_followup_input_preserves_delivery_but_rejects_sequence(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        witness = execute_post_handoff_signal_witness(
            sender,
            recipient,
            followup_input=("standard-signal", "_", "_"),
        )

        self.assertFalse(witness.accepted)
        self.assertEqual(witness.status, "followup-not-routed")
        self.assertIsNotNone(witness.recipient_before_followup)
        self.assertIsNotNone(witness.followup_result)
        self.assertEqual(witness.followup_result.status, "rejected-input")
        self.assertEqual(witness.recipient_after_followup.input, ("_", "_", "_"))
        self.assertEqual(witness.recipient_after_followup.output, ("_", "_", "_"))

    def test_payload_records_delivery_and_followup_final_state(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        payload = post_handoff_signal_witness_payload(
            execute_post_handoff_signal_witness(sender, recipient)
        )

        self.assertEqual(payload["schema_version"], 1)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["status"], "post-handoff-signal-routed")
        self.assertEqual(payload["delivery"]["status"], "neighbor-delivery-consumed")
        self.assertEqual(payload["followup_input"], [1, 0, 0])
        self.assertEqual(payload["followup_status"], "routed")
        self.assertEqual(payload["recipient"]["before_followup"]["role"], "proc")
        self.assertEqual(payload["recipient"]["after_followup"]["output"], [0, 0, 1])
        self.assertEqual(payload["recipient"]["after_followup"]["memory"], "right")

    def test_text_report_summarizes_post_handoff_routing(self):
        sender = Cell(
            role="stem",
            memory="right",
            input=(1, 0, 0),
            control=(1, 0, 0),
            buffer=(1, 0, 1, 0),
        )
        recipient = Cell(role="wire", memory="right")

        report = format_post_handoff_signal_witness(
            execute_post_handoff_signal_witness(sender, recipient)
        )

        self.assertIn("Post-handoff signal witness: post-handoff-signal-routed", report)
        self.assertIn("Accepted: yes", report)
        self.assertIn("Delivery: neighbor-delivery-consumed", report)
        self.assertIn("Follow-up status: routed", report)
        self.assertIn("Recipient after follow-up: role=proc memory=right", report)
        self.assertIn("output=0, 0, 1", report)

    def test_cli_emits_json_for_accepted_fixture(self):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "autarkic_systems.network_sequence",
                "--case",
                "init-followup-routed",
                "--format",
                "json",
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(payload["accepted"])
        self.assertEqual(payload["followup_status"], "routed")
        self.assertEqual(payload["recipient"]["after_followup"]["output"], [0, 0, 1])

    def test_cli_returns_failure_for_malformed_followup_fixture(self):
        stdout = io.StringIO()

        with contextlib.redirect_stdout(stdout):
            exit_code = run_network_sequence_cli(
                ["--case", "malformed-followup-rejected"]
            )

        output = stdout.getvalue()
        self.assertEqual(exit_code, 1, output)
        self.assertIn("Post-handoff signal witness: followup-not-routed", output)
        self.assertIn("Accepted: no", output)
        self.assertIn("Follow-up status: rejected-input", output)


if __name__ == "__main__":
    unittest.main()
