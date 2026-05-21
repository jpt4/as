"""Focused CLI for the AS command-token source-status frontier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from autarkic_systems.project_status import (
    DEFAULT_SOURCE_STATUS_PATHS,
    _additional_source_status_text_lines,
    _as_boundary_text_lines,
    _blocked_runtime_surface_text_lines,
    _execution_readiness_text_lines,
    _frontier_summary,
    _latest_source_review_text_lines,
    _resolution_question_evidence_text_lines,
    _resolution_question_text_lines,
    _resolved_resolution_question_text_lines,
)


SOURCE_STATUS_SCHEMA_VERSION = 4


def build_source_status_frontier_report(
    source_status_paths: (
        list[Path | str] | tuple[Path | str, ...]
    ) = DEFAULT_SOURCE_STATUS_PATHS,
) -> dict[str, Any]:
    """Build the focused command-token source-status frontier report."""

    frontier = _frontier_summary(source_status_paths)
    accepted = (
        not frontier["missing_source_statuses"]
        and not frontier["invalid_source_statuses"]
    )
    frontier["closure_summary"] = _closure_summary(frontier, accepted)
    return {
        "schema_version": SOURCE_STATUS_SCHEMA_VERSION,
        "accepted": accepted,
        "frontier": frontier,
    }


def format_source_status_frontier_report(report: dict[str, Any]) -> str:
    """Format the focused source-status frontier report."""

    status = "accepted" if report["accepted"] else "rejected"
    frontier = report["frontier"]
    blocked_commands = frontier["blocked_commands"] or []
    failed_subjects = frontier["failed_subjects"] or []
    missing = frontier["missing_source_statuses"] or []
    invalid = [
        f"{item['path']}: {item['subject']}: {item['error']}"
        for item in frontier["invalid_source_statuses"]
    ]
    lines = [
        f"AS source-status frontier: {status}",
        "Failed subjects: "
        + (", ".join(failed_subjects) if failed_subjects else "none"),
        "Blocked commands: "
        + (", ".join(blocked_commands) if blocked_commands else "none"),
        *_source_status_file_text_lines(frontier),
        *_blocked_runtime_surface_text_lines(frontier),
        *_as_boundary_text_lines(frontier),
        *_execution_readiness_text_lines(frontier),
        *_closure_summary_text_lines(frontier),
        *_resolution_question_text_lines(frontier),
        *_resolution_question_evidence_text_lines(frontier),
        *_resolved_resolution_question_text_lines(frontier),
        *_latest_source_review_text_lines(frontier),
        *_additional_source_status_text_lines(frontier),
        f"Safe next slice: {frontier['safe_next_slice'] or 'none'}",
        "Missing source-status files: "
        + (", ".join(missing) if missing else "none"),
        "Invalid source-status files: "
        + (", ".join(invalid) if invalid else "none"),
    ]
    return "\n".join(lines)


def run_source_status_frontier_cli(argv: list[str] | None = None) -> int:
    """Run the focused source-status frontier CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.source_status",
        description="Render the AS command-token source-status frontier.",
    )
    parser.add_argument(
        "--source-status",
        action="append",
        default=None,
        help="Source-status JSON path to include in the frontier summary.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the source-status frontier report.",
    )
    args = parser.parse_args(argv)

    source_status_paths = (
        [Path(path) for path in args.source_status]
        if args.source_status is not None
        else DEFAULT_SOURCE_STATUS_PATHS
    )
    report = build_source_status_frontier_report(source_status_paths)
    if args.format == "json":
        print(json.dumps(report, sort_keys=True))
    else:
        print(format_source_status_frontier_report(report))
    return 0 if report["accepted"] else 1


def _source_status_file_text_lines(frontier: dict[str, Any]) -> list[str]:
    source_statuses = frontier["source_statuses"]
    if not source_statuses:
        return ["Source-status files: none accepted"]
    lines = ["Source-status files:"]
    for source_status in source_statuses:
        decision = source_status["decision"] or "no decision"
        lines.append(f"  {source_status['path']}: {decision}")
    return lines


def _closure_summary(frontier: dict[str, Any], accepted: bool) -> dict[str, Any]:
    """Derive the focused queue-closure state from the accepted frontier payload."""

    if not accepted:
        return {
            "safe_next_slice_state": "unknown",
            "remaining_blocked_commands": [],
            "preserved_unsupported_commands": [],
            "implemented_commands": [],
            "execution_change_allowed": False,
            "reason": "frontier rejected; closure summary unavailable",
        }

    preserved_unsupported_commands: list[str] = []
    implemented_commands: list[str] = []
    execution_change_allowed = False
    for source_status in frontier["source_statuses"]:
        readiness = source_status["execution_readiness"]
        if not readiness:
            continue
        if readiness["execution_change_allowed"]:
            execution_change_allowed = True
        if readiness["decision"] == "preserved-unsupported":
            _append_unique_commands(
                preserved_unsupported_commands,
                source_status["commands"],
            )
        if readiness["decision"] == "implemented":
            _append_unique_commands(implemented_commands, source_status["commands"])

    safe_next_slice_state = "open" if frontier["safe_next_slice"] else "closed"
    reason = _closure_summary_reason(
        safe_next_slice_state=safe_next_slice_state,
        blocked_commands=frontier["blocked_commands"],
        preserved_unsupported_commands=preserved_unsupported_commands,
        execution_change_allowed=execution_change_allowed,
    )
    return {
        "safe_next_slice_state": safe_next_slice_state,
        "remaining_blocked_commands": list(frontier["blocked_commands"]),
        "preserved_unsupported_commands": preserved_unsupported_commands,
        "implemented_commands": implemented_commands,
        "execution_change_allowed": execution_change_allowed,
        "reason": reason,
    }


def _closure_summary_reason(
    *,
    safe_next_slice_state: str,
    blocked_commands: list[str],
    preserved_unsupported_commands: list[str],
    execution_change_allowed: bool,
) -> str:
    """Keep the common closed standard-signal boundary stable for automation."""

    if (
        safe_next_slice_state == "closed"
        and "standard-signal" in blocked_commands
        and "standard-signal" in preserved_unsupported_commands
        and not execution_change_allowed
    ):
        return "standard-signal requires new source evidence"
    if safe_next_slice_state == "closed":
        return "safe-next queue closed"
    return "safe-next slice remains active"


def _append_unique_commands(target: list[str], commands: list[str]) -> None:
    """Preserve source-status command order while removing duplicates."""

    for command in commands:
        if command not in target:
            target.append(command)


def _closure_summary_text_lines(frontier: dict[str, Any]) -> list[str]:
    summary = frontier["closure_summary"]
    allowed = "yes" if summary["execution_change_allowed"] else "no"
    return [
        "Closure summary: "
        f"safe-next queue {summary['safe_next_slice_state']}; "
        "remaining blocked commands: "
        f"{_command_text(summary['remaining_blocked_commands'])}; "
        "preserved unsupported: "
        f"{_command_text(summary['preserved_unsupported_commands'])}; "
        "implemented commands: "
        f"{_command_text(summary['implemented_commands'])}; "
        f"execution changes allowed: {allowed}; "
        f"reason: {summary['reason']}"
    ]


def _command_text(commands: list[str]) -> str:
    return ", ".join(commands) if commands else "none"


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_source_status_frontier_cli())
