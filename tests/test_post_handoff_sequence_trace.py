import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.network_sequence_trace import (
    POST_HANDOFF_SIGNAL_SEQUENCE_TRACE_ARTIFACT_ID,
    execute_network_sequence_trace,
    load_network_sequence_trace,
    validate_network_sequence_trace,
)


ARTIFACT = Path("schematics/sequences/post_handoff_signal_sequence_trace.json")
CLAIM_ID = "UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED"


class PostHandoffSequenceTraceTests(unittest.TestCase):
    def setUp(self):
        self.trace = load_network_sequence_trace(ARTIFACT)

    def test_artifact_names_the_post_handoff_sequence(self):
        self.assertEqual(
            POST_HANDOFF_SIGNAL_SEQUENCE_TRACE_ARTIFACT_ID,
            "post-handoff-signal-sequence-trace",
        )
        self.assertEqual(
            self.trace.artifact_id,
            POST_HANDOFF_SIGNAL_SEQUENCE_TRACE_ARTIFACT_ID,
        )
        self.assertEqual(self.trace.sequence_claim_id, CLAIM_ID)
        self.assertEqual(
            self.trace.sequence_helper,
            "execute_post_handoff_signal_witness",
        )
        self.assertEqual(self.trace.expected_status, "post-handoff-signal-routed")
        self.assertEqual(self.trace.expected_delivery_status, "neighbor-delivery-consumed")
        self.assertEqual(self.trace.expected_followup_status, "routed")

    def test_trace_records_sender_delivery_and_followup_cells(self):
        sender = self.trace.sender_initial_cell
        recipient_initial = self.trace.recipient_initial_cell
        before_followup = self.trace.expected_recipient_before_followup
        after_followup = self.trace.expected_recipient_after_followup

        self.assertEqual(sender["role"], "stem")
        self.assertEqual(sender["input"], [1, 0, 0])
        self.assertEqual(sender["control"], [1, 0, 0])
        self.assertEqual(sender["buffer"], [1, 0, 1, 0])
        self.assertEqual(recipient_initial["role"], "wire")
        self.assertEqual(recipient_initial["memory"], "right")
        self.assertEqual(self.trace.expected_delivered_tuple, ("_", "proc-l-init", "_"))
        self.assertEqual(self.trace.followup_input, (1, 0, 0))
        self.assertEqual(before_followup["role"], "proc")
        self.assertEqual(before_followup["memory"], "left")
        self.assertEqual(before_followup["input"], [1, 0, 0])
        self.assertEqual(after_followup["role"], "proc")
        self.assertEqual(after_followup["memory"], "right")
        self.assertEqual(after_followup["output"], [0, 0, 1])
        self.assertEqual(after_followup["input"], ["_", "_", "_"])

    def test_trace_records_followup_signal_flow(self):
        self.assertEqual(
            self.trace.routed_signal_flow,
            (
                "proc-l-init handoff -> recipient proc/left",
                "follow-up input[1,0,0] routes through proc/left",
                "recipient output[2] set to 1",
                "processor memory toggles left -> right",
                "recipient input cleared",
            ),
        )

    def test_trace_executes_against_sequence_helper(self):
        execution = execute_network_sequence_trace(self.trace)

        self.assertTrue(execution.accepted, execution.detail)
        self.assertEqual(execution.status, self.trace.expected_status)
        self.assertEqual(
            execution.delivery_status,
            self.trace.expected_delivery_status,
        )
        self.assertEqual(
            execution.delivered_tuple,
            self.trace.expected_delivered_tuple,
        )
        self.assertEqual(
            execution.recipient_before_followup,
            self.trace.expected_recipient_before_followup,
        )
        self.assertEqual(
            execution.recipient_after_followup,
            self.trace.expected_recipient_after_followup,
        )

    def test_trace_validates_sequence_contract(self):
        results = validate_network_sequence_trace(self.trace)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "schema",
                "participants",
                "delivery",
                "followup-step",
                "sequence-execution",
                "boundary",
            },
        )

    def test_drifted_delivered_tuple_is_rejected(self):
        drifted = replace(
            self.trace,
            expected_delivered_tuple=("proc-l-init", "_", "_"),
        )

        results = validate_network_sequence_trace(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "delivery"
                and "delivered tuple" in result.detail
                for result in results
            ),
            results,
        )

    def test_drifted_expected_status_is_rejected(self):
        drifted = replace(self.trace, expected_status="followup-not-routed")

        results = validate_network_sequence_trace(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "sequence-execution"
                and "status mismatch" in result.detail
                for result in results
            ),
            results,
        )

    def test_drifted_recipient_after_followup_cell_is_rejected(self):
        drifted_after = dict(self.trace.expected_recipient_after_followup)
        drifted_after["memory"] = "left"
        drifted = replace(
            self.trace,
            expected_recipient_after_followup=drifted_after,
        )

        results = validate_network_sequence_trace(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "followup-step"
                and "after-followup cell mismatch" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
