import unittest
from dataclasses import replace
from pathlib import Path

from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    load_transition_evidence_bundle,
    validate_evidence_bundle_registry,
    validate_transition_evidence_bundle,
)


REGISTRY = Path("evidence/manifest.json")
SELF_MAILBOX_BUNDLE = Path("evidence/self_mailbox_write_buffer_bundle.json")
SELF_MAILBOX_BUNDLE_ID = "self-mailbox-write-buffer-evidence-bundle"
SELF_MAILBOX_CLAIM_ID = "UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED"
SELF_MAILBOX_EXAMPLE = "self mailbox write buffer one appended"
SELF_MAILBOX_STATUS = "self-mailbox-write-buffer-appended"
SELF_MAILBOX_COVERED_EXAMPLES = (
    "self mailbox write buffer zero appended",
    "self mailbox write buffer one appended",
)
SELF_COMMAND_BUFFER_BUNDLE = Path(
    "evidence/self_command_buffer_write_buffer_bundle.json"
)
SELF_COMMAND_BUFFER_BUNDLE_ID = "self-command-buffer-write-buffer-evidence-bundle"
SELF_COMMAND_BUFFER_CLAIM_ID = "UC-STEM-COMMAND-BUFFER-SELF-WRITE-BUFFER-APPENDED"
SELF_COMMAND_BUFFER_EXAMPLE = "self command buffer write buffer one appended"
SELF_COMMAND_BUFFER_STATUS = "stem-command-buffer-self-write-buffer-appended"
SELF_COMMAND_BUFFER_COVERED_EXAMPLES = (
    "self command buffer write buffer zero appended",
    "self command buffer write buffer one appended",
)


class WriteBufferExecutionEvidenceBundleTests(unittest.TestCase):
    def setUp(self):
        self.self_mailbox_bundle = load_transition_evidence_bundle(
            SELF_MAILBOX_BUNDLE
        )
        self.self_command_buffer_bundle = load_transition_evidence_bundle(
            SELF_COMMAND_BUFFER_BUNDLE
        )

    def test_self_mailbox_bundle_names_write_buffer_execution(self):
        bundle = self.self_mailbox_bundle

        self.assertEqual(bundle.schema_version, 1)
        self.assertEqual(bundle.bundle_id, SELF_MAILBOX_BUNDLE_ID)
        self.assertEqual(bundle.claim_id, SELF_MAILBOX_CLAIM_ID)
        self.assertEqual(bundle.predicate, "self_mailbox_write_buffer_appends_literal")
        self.assertEqual(bundle.positive_example, SELF_MAILBOX_EXAMPLE)
        self.assertEqual(bundle.covered_positive_examples, SELF_MAILBOX_COVERED_EXAMPLES)
        self.assertEqual(bundle.transition_function, "step_stem_cell")
        self.assertEqual(bundle.expected_status, SELF_MAILBOX_STATUS)

    def test_self_mailbox_bundle_records_artifact_paths(self):
        bundle = self.self_mailbox_bundle

        self.assertEqual(bundle.claim_manifest_path, Path("claims/transition_claims.json"))
        self.assertEqual(
            bundle.proof_certificate_path,
            Path("claims/proof_certificates.json"),
        )
        self.assertEqual(
            bundle.schematic_trace_path,
            Path("schematics/self_mailbox_write_buffer_trace.json"),
        )
        self.assertEqual(
            bundle.schematic_svg_path,
            Path("schematics/self_mailbox_write_buffer_trace.svg"),
        )
        self.assertEqual(
            bundle.hardware_witness_map_path,
            Path("sources/prc_hardware_witness_map.json"),
        )
        self.assertEqual(
            bundle.source_status_paths,
            (
                Path("sources/stem_command_execution_source_status.json"),
                Path("sources/recipient_non_init_command_source_status.json"),
                Path("sources/standard_signal_command_semantics_status.json"),
                Path("sources/write_buffer_command_semantics_status.json"),
            ),
        )

    def test_self_command_buffer_bundle_names_write_buffer_execution(self):
        bundle = self.self_command_buffer_bundle

        self.assertEqual(bundle.schema_version, 1)
        self.assertEqual(bundle.bundle_id, SELF_COMMAND_BUFFER_BUNDLE_ID)
        self.assertEqual(bundle.claim_id, SELF_COMMAND_BUFFER_CLAIM_ID)
        self.assertEqual(
            bundle.predicate,
            "stem_command_buffer_executes_self_write_buffer",
        )
        self.assertEqual(bundle.positive_example, SELF_COMMAND_BUFFER_EXAMPLE)
        self.assertEqual(
            bundle.covered_positive_examples,
            SELF_COMMAND_BUFFER_COVERED_EXAMPLES,
        )
        self.assertEqual(bundle.transition_function, "step_stem_cell")
        self.assertEqual(bundle.expected_status, SELF_COMMAND_BUFFER_STATUS)

    def test_self_command_buffer_bundle_records_artifact_paths(self):
        bundle = self.self_command_buffer_bundle

        self.assertEqual(bundle.claim_manifest_path, Path("claims/transition_claims.json"))
        self.assertEqual(
            bundle.proof_certificate_path,
            Path("claims/proof_certificates.json"),
        )
        self.assertEqual(
            bundle.schematic_trace_path,
            Path("schematics/self_command_buffer_write_buffer_trace.json"),
        )
        self.assertEqual(
            bundle.schematic_svg_path,
            Path("schematics/self_command_buffer_write_buffer_trace.svg"),
        )
        self.assertEqual(
            bundle.hardware_witness_map_path,
            Path("sources/prc_hardware_witness_map.json"),
        )
        self.assertEqual(
            bundle.source_status_paths,
            (
                Path("sources/stem_command_execution_source_status.json"),
                Path("sources/recipient_non_init_command_source_status.json"),
                Path("sources/standard_signal_command_semantics_status.json"),
                Path("sources/write_buffer_command_semantics_status.json"),
            ),
        )

    def test_bundles_validate_claim_proof_trace_svg_and_statuses(self):
        for bundle in (
            self.self_mailbox_bundle,
            self.self_command_buffer_bundle,
        ):
            with self.subTest(bundle=bundle.bundle_id):
                results = validate_transition_evidence_bundle(bundle)

                self.assertTrue(results)
                self.assertTrue(all(result.accepted for result in results), results)
                self.assertEqual(
                    {result.subject for result in results},
                    {
                        "schema",
                        "claim-example",
                        "proof-certificate",
                        "schematic-trace",
                        "schematic-svg",
                        "source-statuses",
                        "boundary",
                    },
                )

    def test_registry_includes_write_buffer_execution_bundles(self):
        registry = load_evidence_bundle_registry(REGISTRY)
        entries = {entry.bundle_id: entry for entry in registry.bundles}

        self.assertEqual(len(entries), 10)
        self.assertIn(SELF_MAILBOX_BUNDLE_ID, entries)
        self.assertIn(SELF_COMMAND_BUFFER_BUNDLE_ID, entries)
        self.assertEqual(entries[SELF_MAILBOX_BUNDLE_ID].path, SELF_MAILBOX_BUNDLE)
        self.assertEqual(
            entries[SELF_COMMAND_BUFFER_BUNDLE_ID].path,
            SELF_COMMAND_BUFFER_BUNDLE,
        )
        self.assertEqual(
            entries[SELF_MAILBOX_BUNDLE_ID].claim_id,
            SELF_MAILBOX_CLAIM_ID,
        )
        self.assertEqual(
            entries[SELF_COMMAND_BUFFER_BUNDLE_ID].claim_id,
            SELF_COMMAND_BUFFER_CLAIM_ID,
        )

        results = validate_evidence_bundle_registry(registry)
        self.assertTrue(all(result.accepted for result in results), results)

    def test_drifted_write_buffer_covered_example_name_is_rejected(self):
        drifted = replace(
            self.self_mailbox_bundle,
            covered_positive_examples=(
                "self mailbox write buffer one appended",
                "not a manifest example",
            ),
        )

        results = validate_transition_evidence_bundle(drifted)

        self.assertTrue(
            any(
                not result.accepted
                and result.subject == "claim-example"
                and "missing covered example" in result.detail
                for result in results
            ),
            results,
        )


if __name__ == "__main__":
    unittest.main()
