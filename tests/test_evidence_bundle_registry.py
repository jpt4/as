import json
import unittest
from pathlib import Path

from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    validate_evidence_bundle_registry,
)


REGISTRY = Path("evidence/manifest.json")
INIT_BUNDLE = Path("evidence/recipient_init_command_message_bundle.json")
WRITE_BUNDLE = Path("evidence/recipient_write_buffer_command_message_bundle.json")


class EvidenceBundleRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_evidence_bundle_registry(REGISTRY)

    def test_culled_registry_has_two_bundles(self):
        self.assertEqual(len(self.registry.bundles), 2)
        paths = {entry.path for entry in self.registry.bundles}
        self.assertEqual(paths, {INIT_BUNDLE, WRITE_BUNDLE})

    def test_registry_validation_accepts(self):
        results = validate_evidence_bundle_registry(self.registry)
        self.assertTrue(all(r.accepted for r in results), results)

    def test_bundles_reference_proflog_pin(self):
        for path in (INIT_BUNDLE, WRITE_BUNDLE):
            data = json.loads(path.read_text(encoding="utf-8"))
            statuses = data["artifacts"]["source_statuses"]
            self.assertIn("sources/proflog_pin.json", statuses)


if __name__ == "__main__":
    unittest.main()
