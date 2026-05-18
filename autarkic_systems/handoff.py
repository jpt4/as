"""End-of-month handoff status for AS.

The handoff report composes the current project evidence summary with the
local GitHub submission evidence. It does not introduce a new authority; it
reuses the existing status commands so the end-of-month handoff can be checked
from one local command.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Callable

from autarkic_systems.github_submission import (
    GitHubSubmissionStatus,
    build_github_submission_status,
    format_github_submission_status,
    github_submission_status_payload,
)
from autarkic_systems.project_status import (
    build_project_status_report,
    format_project_status_summary,
)


ProjectBuilder = Callable[[], dict[str, Any]]
SubmissionBuilder = Callable[[], GitHubSubmissionStatus]


@dataclass(frozen=True)
class HandoffStatus:
    """Combined project and GitHub submission status."""

    project_status: dict[str, Any]
    github_submission: GitHubSubmissionStatus
    project_summary: str

    @property
    def accepted(self) -> bool:
        """Return whether both project evidence and fork submission are green."""

        return bool(self.project_status["accepted"]) and self.github_submission.accepted

    @property
    def handoff_state(self) -> str:
        """Return the compact handoff-state label."""

        if self.accepted:
            return "ready"
        return "not-ready"


def build_handoff_status(
    project_builder: ProjectBuilder = build_project_status_report,
    submission_builder: SubmissionBuilder = build_github_submission_status,
) -> HandoffStatus:
    """Build a handoff report from project and submission status builders."""

    project_status = project_builder()
    return HandoffStatus(
        project_status=project_status,
        github_submission=submission_builder(),
        project_summary=format_project_status_summary(project_status),
    )


def handoff_status_payload(report: HandoffStatus) -> dict[str, Any]:
    """Return a JSON-ready handoff status payload."""

    return {
        "accepted": report.accepted,
        "handoff_state": report.handoff_state,
        "project_summary": report.project_summary,
        "project_status": report.project_status,
        "github_submission": github_submission_status_payload(
            report.github_submission
        ),
    }


def format_handoff_status(report: HandoffStatus) -> str:
    """Format the combined handoff report for operators."""

    return "\n".join([
        f"Autarkic Systems handoff: {report.handoff_state}",
        "",
        "Project status:",
        report.project_summary,
        "",
        "GitHub submission:",
        format_github_submission_status(report.github_submission),
    ])


def run_handoff_cli(
    argv: list[str] | None = None,
    project_builder: ProjectBuilder = build_project_status_report,
    submission_builder: SubmissionBuilder = build_github_submission_status,
) -> int:
    """Run the AS handoff status CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.handoff",
        description="Render the combined AS project and GitHub submission status.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the handoff report.",
    )
    args = parser.parse_args(argv)

    report = build_handoff_status(
        project_builder=project_builder,
        submission_builder=submission_builder,
    )
    if args.format == "json":
        print(json.dumps(handoff_status_payload(report), sort_keys=True))
    else:
        print(format_handoff_status(report))
    return 0 if report.accepted else 1


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_handoff_cli())
