"""Operator-facing vertical reports for network-sequence evidence.

Network-sequence artifacts deliberately live in separate files: sequence
claims, proof certificates, an object-language manifest, an executable
witness, a checked trace and SVG, chain evidence, source-status records, and the
evidence bundle that ties them together. This module is a first-run reporting
layer over those artifacts. It delegates acceptance to
``network_sequence_evidence_bundle`` and formats the already-validated path as
a compact claim-to-evidence report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from autarkic_systems.network_sequence_evidence_bundle import (
    load_network_sequence_evidence_bundle,
    load_network_sequence_evidence_bundle_registry,
    network_sequence_evidence_bundle_report_payload,
    network_sequence_registry_validation_report_payload,
    validate_network_sequence_evidence_bundle,
    validate_network_sequence_evidence_bundle_registry,
)


DEFAULT_SEQUENCE_BUNDLE = Path("evidence/sequences/post_handoff_signal_bundle.json")
DEFAULT_SEQUENCE_REGISTRY = Path("evidence/sequences/manifest.json")


def build_network_sequence_demo_report(
    bundle_path: Path | str = DEFAULT_SEQUENCE_BUNDLE,
) -> dict[str, Any]:
    """Build one vertical report over a network-sequence evidence bundle."""

    bundle = load_network_sequence_evidence_bundle(bundle_path)
    results = validate_network_sequence_evidence_bundle(bundle)
    validation = network_sequence_evidence_bundle_report_payload(bundle, results)
    evidence_layers = _evidence_layers(bundle)
    return {
        "accepted": validation["accepted"],
        "bundle_id": bundle.bundle_id,
        "sequence_claim_id": bundle.sequence_claim_id,
        "predicate": bundle.predicate,
        "positive_example": bundle.positive_example,
        "sequence_function": bundle.sequence_function,
        "expected_status": bundle.expected_status,
        "validation": {
            "accepted": validation["accepted"],
            "failed_subjects": validation["failed_subjects"],
            "result_count": validation["result_count"],
            "results": validation["results"],
        },
        "evidence_layers": evidence_layers,
        "missing_evidence_paths": _missing_evidence_paths(evidence_layers),
        "boundaries": list(bundle.boundaries),
    }


def format_network_sequence_demo_report(report: dict[str, Any]) -> str:
    """Format a human-readable vertical network-sequence evidence report."""

    layers = report["evidence_layers"]
    chain_bundles = _paths_for_role(layers, "chain-bundle")
    source_statuses = _paths_for_role(layers, "source-status")
    validation = report["validation"]
    status = "accepted" if report["accepted"] else "rejected"
    failed_subjects = validation["failed_subjects"] or []
    missing_paths = report["missing_evidence_paths"] or []

    lines = [
        f"Vertical network sequence demo: {report['bundle_id']}",
        f"Claim: {report['sequence_claim_id']}",
        f"Predicate: {report['predicate']}",
        f"Example: {report['positive_example']}",
        f"Sequence function: {report['sequence_function']}",
        f"Expected status: {report['expected_status']}",
        f"Validation: {status}",
        f"Validation checks: {validation['result_count']}",
        f"Failed subjects: {', '.join(failed_subjects) if failed_subjects else 'none'}",
        f"Missing evidence paths: {', '.join(missing_paths) if missing_paths else 'none'}",
        f"Claim manifest: {_path_for_role(layers, 'sequence-claim-manifest')}",
        f"Proof certificates: {_path_for_role(layers, 'sequence-proof-certificates')}",
        f"Language: {_path_for_role(layers, 'sequence-language')}",
        f"Claim validator: {_path_for_role(layers, 'sequence-claim-validator')}",
        f"Sequence witness: {_path_for_role(layers, 'sequence-witness')}",
        f"Trace: {_path_for_role(layers, 'sequence-trace')}",
        f"SVG: {_path_for_role(layers, 'sequence-svg')}",
        f"Chain bundles: {len(chain_bundles)}",
    ]
    lines.extend(f"- {path}" for path in chain_bundles)
    lines.append(f"Source-status boundaries: {len(source_statuses)}")
    lines.extend(f"- {path}" for path in source_statuses)
    lines.append("Boundary terms:")
    lines.extend(f"- {boundary}" for boundary in report["boundaries"])
    return "\n".join(lines)


def build_network_sequence_demo_registry_report(
    registry_path: Path | str = DEFAULT_SEQUENCE_REGISTRY,
) -> dict[str, Any]:
    """Build vertical demo reports for every bundle in a sequence registry."""

    registry = load_network_sequence_evidence_bundle_registry(registry_path)
    registry_results = validate_network_sequence_evidence_bundle_registry(registry)
    validation = network_sequence_registry_validation_report_payload(
        registry,
        registry_results,
    )
    bundle_reports = [
        build_network_sequence_demo_report(entry.path)
        for entry in registry.bundles
        if entry.path.exists()
    ]
    missing_paths = sorted({
        str(entry.path) for entry in registry.bundles if not entry.path.exists()
    } | {
        path
        for report in bundle_reports
        for path in report["missing_evidence_paths"]
    })
    accepted_count = sum(1 for report in bundle_reports if report["accepted"])
    return {
        "accepted": validation["accepted"]
        and all(report["accepted"] for report in bundle_reports),
        "registry_id": registry.registry_id,
        "bundle_count": len(registry.bundles),
        "accepted_count": accepted_count,
        "failed_count": len(registry.bundles) - accepted_count,
        "missing_evidence_paths": missing_paths,
        "bundle_failed_subjects": _registry_bundle_failed_subjects(bundle_reports),
        "validation": {
            "accepted": validation["accepted"],
            "failed_subjects": validation["failed_subjects"],
            "result_count": validation["result_count"],
            "results": validation["results"],
        },
        "bundle_reports": bundle_reports,
    }


def format_network_sequence_demo_registry_report(report: dict[str, Any]) -> str:
    """Format a human-readable report for a sequence demo registry."""

    missing_paths = report["missing_evidence_paths"] or []
    lines = [
        f"Vertical network sequence demo registry: {report['registry_id']}",
        f"Bundles: {report['bundle_count']}",
        f"Accepted: {report['accepted_count']}",
        f"Failed: {report['failed_count']}",
        f"Missing evidence paths: {', '.join(missing_paths) if missing_paths else 'none'}",
    ]
    for bundle_report in report["bundle_reports"]:
        status = "accepted" if bundle_report["accepted"] else "rejected"
        failed_subjects = bundle_report["validation"]["failed_subjects"] or []
        lines.extend(
            [
                "",
                f"- {bundle_report['bundle_id']}: {status}",
                f"  Claim: {bundle_report['sequence_claim_id']}",
                f"  Expected status: {bundle_report['expected_status']}",
                "  Missing evidence paths: "
                + (
                    ", ".join(bundle_report["missing_evidence_paths"])
                    if bundle_report["missing_evidence_paths"]
                    else "none"
                ),
            ]
        )
        if failed_subjects:
            lines.append(f"  Failed subjects: {', '.join(failed_subjects)}")
    return "\n".join(lines)


def run_network_sequence_demo_cli(argv: list[str] | None = None) -> int:
    """Run the vertical network-sequence demo report CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.network_sequence_demo",
        description="Render an AS network-sequence evidence demo report.",
    )
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--bundle",
        default=None,
        help="Path to the network-sequence evidence bundle JSON.",
    )
    target_group.add_argument(
        "--registry",
        default=None,
        help="Path to a network-sequence evidence registry JSON.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the demo report.",
    )
    args = parser.parse_args(argv)

    if args.registry is not None:
        report = build_network_sequence_demo_registry_report(args.registry)
        if args.format == "json":
            print(json.dumps(report, sort_keys=True))
        else:
            print(format_network_sequence_demo_registry_report(report))
        return 0 if report["accepted"] else 1

    report = build_network_sequence_demo_report(args.bundle or DEFAULT_SEQUENCE_BUNDLE)
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    else:
        print(format_network_sequence_demo_report(report))
    return 0 if report["accepted"] else 1


def _evidence_layers(bundle: Any) -> list[dict[str, Any]]:
    layers = [
        {
            "role": "sequence-claim-manifest",
            "path": str(bundle.sequence_claim_manifest_path),
        },
        {
            "role": "sequence-proof-certificates",
            "path": str(bundle.sequence_proof_certificate_path),
        },
        {
            "role": "sequence-language",
            "path": str(bundle.sequence_language_path),
        },
        {
            "role": "sequence-claim-validator",
            "path": str(bundle.sequence_claim_validator_path),
        },
        {
            "role": "sequence-witness",
            "path": str(bundle.sequence_witness_path),
        },
        {
            "role": "sequence-trace",
            "path": str(bundle.sequence_trace_path),
        },
        {
            "role": "sequence-svg",
            "path": str(bundle.sequence_svg_path),
        },
    ]
    layers.extend(
        {"role": "chain-bundle", "path": str(path)}
        for path in bundle.chain_bundle_paths
    )
    layers.extend(
        {"role": "source-status", "path": str(path)}
        for path in bundle.source_status_paths
    )
    return [_with_presence(layer) for layer in layers]


def _with_presence(layer: dict[str, str]) -> dict[str, Any]:
    return {
        "role": layer["role"],
        "path": layer["path"],
        "exists": Path(layer["path"]).is_file(),
    }


def _missing_evidence_paths(layers: list[dict[str, Any]]) -> list[str]:
    return [layer["path"] for layer in layers if not layer["exists"]]


def _registry_bundle_failed_subjects(
    bundle_reports: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    failed: list[dict[str, Any]] = []
    for report in bundle_reports:
        failed_subjects = report["validation"]["failed_subjects"] or []
        if failed_subjects:
            failed.append({
                "bundle_id": report["bundle_id"],
                "failed_subjects": failed_subjects,
            })
    return failed


def _path_for_role(layers: list[dict[str, Any]], role: str) -> str:
    for layer in layers:
        if layer["role"] == role:
            return layer["path"]
    raise ValueError(f"missing evidence layer role {role}")


def _paths_for_role(layers: list[dict[str, Any]], role: str) -> list[str]:
    return [layer["path"] for layer in layers if layer["role"] == role]


if __name__ == "__main__":
    raise SystemExit(run_network_sequence_demo_cli())
