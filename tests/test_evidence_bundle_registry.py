import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    validate_evidence_bundle_registry,
)


REGISTRY = Path("evidence/manifest.json")
BUNDLE = Path("evidence/recipient_init_command_message_bundle.json")
BUNDLE_ID = "recipient-init-command-message-transition-evidence-bundle"
CLAIM_ID = "UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED"
STATUS = "recipient-init-command-message-processed"


class EvidenceBundleRegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_evidence_bundle_registry(REGISTRY)

    def test_registry_names_the_transition_evidence_surface(self):
        self.assertEqual(self.registry.schema_version, 1)
        self.assertEqual(self.registry.registry_id, "transition-evidence-bundle-registry")
        self.assertEqual(self.registry.reviewed_at, "2026-05-17")
        self.assertIn("transition evidence bundles", self.registry.purpose)

    def test_registry_records_the_recipient_init_bundle(self):
        self.assertEqual(len(self.registry.bundles), 1)
        entry = self.registry.bundles[0]

        self.assertEqual(entry.bundle_id, BUNDLE_ID)
        self.assertEqual(entry.path, BUNDLE)
        self.assertEqual(entry.claim_id, CLAIM_ID)
        self.assertEqual(entry.expected_status, STATUS)

    def test_registry_validates_all_registered_bundles(self):
        results = validate_evidence_bundle_registry(self.registry)

        self.assertTrue(results)
        self.assertTrue(all(result.accepted for result in results), results)
        self.assertEqual(
            {result.subject for result in results},
            {
                "registry-schema",
                "registry-entries",
                "registry-bundle-paths",
                "registry-bundle-validation",
            },
        )

    def test_duplicate_bundle_ids_are_rejected(self):
        entry = self.registry.bundles[0]
        drifted = replace(self.registry, bundles=(entry, entry))

        results = validate_evidence_bundle_registry(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-entries"
                and "duplicate bundle ids" in result.detail
                for result in results
            ),
            results,
        )

    def test_missing_bundle_path_is_rejected(self):
        entry = self.registry.bundles[0]
        drifted_entry = replace(entry, path=Path("evidence/missing_bundle.json"))
        drifted = replace(self.registry, bundles=(drifted_entry,))

        results = validate_evidence_bundle_registry(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "registry-bundle-paths"
                and "missing bundle" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
