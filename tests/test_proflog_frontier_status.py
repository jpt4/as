import json
import unittest
from pathlib import Path


STATUS = Path("sources/proflog_frontier_status.json")
PIN = Path("sources/proflog_pin.json")
AUTHORITATIVE_HEAD = "782f620f3aca951816926bd4d8abba0b40558ede"
LEGACY_STUB_HEAD = "77af8481d9f41a439eb42e1d8268a5b39f7c5c33"


class ProflogFrontierStatusTests(unittest.TestCase):
    def setUp(self):
        self.status = json.loads(STATUS.read_text(encoding="utf-8"))
        self.pin = json.loads(PIN.read_text(encoding="utf-8"))

    def test_authoritative_proflog_is_pinned_and_unblocks_frontier(self):
        self.assertEqual(self.status["schema_version"], 2)
        auth = self.status["authoritative_repository"]
        self.assertEqual(auth["repository"], "autarkenterprises/proflog")
        self.assertEqual(auth["decision"], "authoritative-pinned-executable")
        self.assertTrue(auth["implements_sjas_frontier_terms"])
        self.assertEqual(auth["public_remote_head"], AUTHORITATIVE_HEAD)
        self.assertEqual(self.pin["pinned_commit"], AUTHORITATIVE_HEAD)

    def test_legacy_stub_remains_non_dependent(self):
        legacy = self.status["legacy_public_stub"]
        self.assertEqual(legacy["repository"], "jpt4/proflog")
        self.assertEqual(legacy["decision"], "do-not-depend-on-public-main")
        self.assertEqual(legacy["public_remote_head"], LEGACY_STUB_HEAD)


if __name__ == "__main__":
    unittest.main()
