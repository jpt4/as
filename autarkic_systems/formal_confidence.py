"""Formal-confidence integrator boundary for AS.

UC substrate claims are validated locally. SJAS Willard proof machinery is
delegated to pinned autarkenterprises/proflog (see proflog_integration).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.proflog_integration import validate_proflog_pin_recorded
from autarkic_systems.willard_map import (
    load_willard_definition_map,
    validate_willard_definition_map,
)


DEFAULT_BOUNDARY_PATH = Path("claims/formal_confidence_boundary.json")


@dataclass(frozen=True)
class FormalConfidenceReport:
    accepted: bool
    target_id: str
    status: str
    failed_subjects: tuple[str, ...]


def load_formal_confidence_boundary(path: Path | str = DEFAULT_BOUNDARY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_formal_confidence_boundary(
    boundary_path: Path | str = DEFAULT_BOUNDARY_PATH,
    willard_map_path: Path | str = Path("sources/willard_definition_map.json"),
) -> FormalConfidenceReport:
    failed: list[str] = []
    boundary = load_formal_confidence_boundary(boundary_path)
    targets = boundary.get("targets")
    if not isinstance(targets, list) or not targets:
        return FormalConfidenceReport(False, "", "", ("boundary-targets",))

    target = targets[0]
    target_id = target.get("target_id", "")
    status = target.get("status", "")
    if status not in ("integrated",):
        failed.append("boundary-status")

    blocked = target.get("blocked_by") or []
    if blocked:
        failed.append("unexpected-blockers")

    proflog_report = validate_proflog_pin_recorded()
    if not proflog_report.accepted:
        failed.extend(f"proflog-{s}" for s in proflog_report.failed_subjects)

    willard_map = load_willard_definition_map(willard_map_path)
    willard_results = validate_willard_definition_map(
        willard_map, require_existing_witnesses=False
    )
    if not all(r.accepted for r in willard_results):
        failed.append("willard-map")

    known = {anchor.anchor_id for anchor in willard_map.anchors}
    for aid in target.get("willard_anchor_ids") or []:
        if aid not in known:
            failed.append(f"missing-anchor:{aid}")

    sjas = target.get("sjas_proof_apparatus") or {}
    if not sjas.get("pin") or not sjas.get("witness"):
        failed.append("sjas-proof-apparatus-links")

    return FormalConfidenceReport(
        accepted=not failed,
        target_id=target_id,
        status=status,
        failed_subjects=tuple(failed),
    )


def run_formal_confidence_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.formal_confidence",
        description="Validate the formal-confidence integrator boundary.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    report = validate_formal_confidence_boundary()
    if args.format == "json":
        print(
            json.dumps(
                {
                    "accepted": report.accepted,
                    "target_id": report.target_id,
                    "status": report.status,
                    "failed_subjects": list(report.failed_subjects),
                },
                sort_keys=True,
            )
        )
    else:
        state = "accepted" if report.accepted else "rejected"
        print(f"Formal-confidence boundary: {state}")
        print(f"Target: {report.target_id} ({report.status})")
        if report.failed_subjects:
            print("Failed subjects: " + ", ".join(report.failed_subjects))
    return 0 if report.accepted else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_formal_confidence_cli())
