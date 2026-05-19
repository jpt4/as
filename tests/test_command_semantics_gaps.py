import json
import unittest
from pathlib import Path


GAPS = Path("sources/command_semantics_gaps.json")


class CommandSemanticsGapsTests(unittest.TestCase):
    def test_merged_gaps_block_only_standard_signal_command_token(self):
        gaps = json.loads(GAPS.read_text(encoding="utf-8"))
        self.assertEqual(gaps["blocked_commands"], ["standard-signal"])
        self.assertEqual(len(gaps["gaps"]), 3)


if __name__ == "__main__":
    unittest.main()
