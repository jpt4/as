import json
import unittest
from pathlib import Path


STATUS = Path("sources/asmsim_process_buffer_status.json")
STANDARD_SIGNAL_STATUS = Path("sources/standard_signal_command_semantics_status.json")
WRITE_BUFFER_STATUS = Path("sources/write_buffer_command_semantics_status.json")
STEM_STATUS = Path("sources/stem_command_execution_source_status.json")
ASMSIM = Path("/home/sean/Projects/_upstream/prc/practice/asmsim.scm")


class AsmsimProcessBufferStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))
        self.source = ASMSIM.read_text(encoding="utf-8")

    def test_status_records_source_only_blocking_decision(self):
        self.assertEqual(self.status["schema_version"], 1)
        self.assertEqual(
            self.status["decision"],
            "do-not-implement-process-buffer-semantics-from-asmsim",
        )
        self.assertEqual(self.status["runtime_change"], "none-source-status-only")
        self.assertEqual(Path(self.status["local_witness"]), ASMSIM)
        self.assertEqual(
            self.status["safe_next_slice"],
            "keep-command-execution-blocked-pending-source-resolution",
        )

    def test_process_buffer_warning_comments_are_recorded(self):
        comments = self.status["warning_comments"]

        self.assertEqual(
            comments,
            [
                {
                    "locus": "lines 170-171",
                    "text": "process-buffer; need documentation here",
                },
                {
                    "locus": "line 256",
                    "text": "process-buffer auxiliaries - XXX CONFIRM MSGLIST CODES",
                },
            ],
        )
        self.assertIn(";need documentation here", self.source)
        self.assertIn(";process-buffer auxiliaries - XXX CONFIRM MSGLIST CODES", self.source)

    def test_process_buffer_branch_families_are_not_formal_named_commands(self):
        branch_status = self.status["process_buffer_branch_status"]

        self.assertEqual(branch_status["locus"], "lines 170-188")
        self.assertEqual(
            branch_status["branch_predicates"],
            [
                "id+msg?",
                "id+10b5?",
                "id+11b5?",
                "tar+0b4?",
                "tar+sic?",
                "id+nop?",
                "tar+nop?",
            ],
        )
        self.assertEqual(
            branch_status["missing_named_tokens"],
            ["standard-signal", "write-buf-zero", "write-buf-one"],
        )
        self.assertNotIn("write-buf-zero", self.source)
        self.assertNotIn("standard-signal", self.source)

    def test_message_code_auxiliaries_record_placeholder_and_special_signal(self):
        message_codes = self.status["message_code_status"]

        self.assertEqual(message_codes["locus"], "lines 260-290")
        self.assertEqual(message_codes["placeholder"], "msg-list")
        self.assertEqual(message_codes["special_input_code_predicate"], "tar+sic?")
        self.assertIn("member msg '(msg-list)", self.source)
        self.assertIn("(define (tar+sic? b)", self.source)

    def test_existing_command_statuses_reference_asmsim_evidence(self):
        standard = json.loads(STANDARD_SIGNAL_STATUS.read_text(encoding="utf-8"))
        write_buffer = json.loads(WRITE_BUFFER_STATUS.read_text(encoding="utf-8"))
        stem = json.loads(STEM_STATUS.read_text(encoding="utf-8"))

        self.assertTrue(
            any(
                item["path"] == "sources/asmsim_process_buffer_status.json"
                for item in standard["additional_source_statuses"]
            )
        )
        self.assertTrue(
            any(
                item["path"] == "sources/asmsim_process_buffer_status.json"
                for item in write_buffer["additional_source_statuses"]
            )
        )
        self.assertTrue(
            any(
                divergence["witness_id"] == "PRACTICE-ASMSIM-PROCESS-BUFFER-CODES"
                for divergence in stem["legacy_divergences"]
            )
        )


if __name__ == "__main__":
    unittest.main()
