"""Compact project status for culled AS main."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from autarkic_systems.evidence_bundle import (
    load_evidence_bundle_registry,
    validate_evidence_bundle_registry,
)
from autarkic_systems.formal_confidence import validate_formal_confidence_boundary
from autarkic_systems.proflog_integration import validate_proflog_pin_recorded


def build_project_status_report() -> dict[str, Any]:
    registry_path = Path("evidence/manifest.json")
    gaps_path = Path("sources/command_semantics_gaps.json")
    blocked: list[str] = []
    if gaps_path.exists():
        gaps = json.loads(gaps_path.read_text(encoding="utf-8"))
        blocked = list(gaps.get("blocked_commands") or [])

    evidence = {"accepted": False, "bundle_count": 0}
    if registry_path.exists():
        reg = load_evidence_bundle_registry(registry_path)
        results = validate_evidence_bundle_registry(reg)
        evidence["bundle_count"] = len(reg.bundles)
        evidence["accepted"] = all(r.accepted for r in results)

    formal = validate_formal_confidence_boundary()
    proflog = validate_proflog_pin_recorded()
    return {
        "schema_version": 1,
        "accepted": evidence["accepted"] and formal.accepted and proflog.accepted,
        "blocked_commands": blocked,
        "transition_evidence": evidence,
        "formal_confidence": {
            "accepted": formal.accepted,
            "target_id": formal.target_id,
            "status": formal.status,
            "failed_subjects": list(formal.failed_subjects),
        },
        "proflog_integration": {
            "accepted": proflog.accepted,
            "pinned_commit": proflog.pinned_commit,
            "failed_subjects": list(proflog.failed_subjects),
        },
        "archive_branch": "archive/sean-fork-full",
    }


def run_project_status_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.project_status",
        description="Render compact AS project status.",
    )
    parser.add_argument("--format", choices=("text", "json", "summary"), default="text")
    args = parser.parse_args(argv)
    report = build_project_status_report()
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    elif args.format == "summary":
        print(
            f"AS status: {'accepted' if report['accepted'] else 'rejected'}; "
            f"evidence bundles: {report['transition_evidence']['bundle_count']}; "
            f"blocked: {', '.join(report['blocked_commands']) or 'none'}"
        )
    else:
        state = "accepted" if report["accepted"] else "rejected"
        print(f"AS project status: {state}")
        print(f"Transition evidence bundles: {report['transition_evidence']['bundle_count']}")
        print(
            "Blocked commands: "
            + (", ".join(report["blocked_commands"]) if report["blocked_commands"] else "none")
        )
        fc = report["formal_confidence"]
        print(f"Formal confidence: {fc['target_id']} ({fc['status']})")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_project_status_cli())
