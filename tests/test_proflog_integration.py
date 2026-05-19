import json
import unittest
from pathlib import Path

from autarkic_systems.proflog_integration import (
    load_proflog_pin,
    validate_proflog_pin_recorded,
)


class ProflogIntegrationTests(unittest.TestCase):
    def test_pin_and_witness_resolve_former_blockers(self):
        report = validate_proflog_pin_recorded()
        self.assertTrue(report.accepted, report.failed_subjects)
        self.assertEqual(
            report.pinned_commit,
            "782f620f3aca951816926bd4d8abba0b40558ede",
        )

    def test_witness_lists_resolved_fork_blockers(self):
        witness = json.loads(
            Path("claims/proflog_sjas_witness.json").read_text(encoding="utf-8")
        )
        ids = {
            item["blocker_id"]
            for item in witness["former_fork_blockers_resolved"]
        }
        self.assertIn("missing-adr-006x-on-jpt4-proflog-main", ids)
        self.assertIn("fixed-point-construction", ids)

    def test_fast_suite_recorded_passed(self):
        pin = load_proflog_pin()
        self.assertEqual(pin["default_fast_suite"]["result"], "passed")


if __name__ == "__main__":
    unittest.main()
