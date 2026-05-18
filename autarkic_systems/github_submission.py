"""Local GitHub submission status for the AS workspace.

This command reports git evidence for the current submission path without
contacting GitHub APIs. It is a handoff aid: the fork remote is the visible
submission target when upstream direct pushes are permission-blocked.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_TRACKING_ISSUE_URL = "https://github.com/jpt4/as/issues/1"


GitRunner = Callable[[list[str]], str]


@dataclass(frozen=True)
class GitHubSubmissionStatus:
    """Local git evidence for the current GitHub submission state."""

    branch: str
    head_commit: str
    head_short: str
    origin_url: str
    fork_url: str
    origin_main_commit: str
    origin_main_short: str
    fork_main_commit: str
    fork_main_short: str
    head_behind_origin_main_by: int
    head_ahead_origin_main_by: int
    tracking_issue_url: str

    @property
    def fork_main_matches_head(self) -> bool:
        """Return whether fork/main points at the current HEAD."""

        return self.fork_main_commit == self.head_commit

    @property
    def origin_main_matches_head(self) -> bool:
        """Return whether origin/main points at the current HEAD."""

        return self.origin_main_commit == self.head_commit

    @property
    def accepted(self) -> bool:
        """Return whether the current HEAD is visible on fork/main."""

        return self.fork_main_matches_head

    @property
    def submission_state(self) -> str:
        """Return the compact submission-state label."""

        if self.fork_main_matches_head:
            return "submitted-to-fork"
        return "not-submitted-to-fork"


def build_github_submission_status(
    runner: GitRunner | None = None,
    tracking_issue_url: str = DEFAULT_TRACKING_ISSUE_URL,
) -> GitHubSubmissionStatus:
    """Build a local GitHub submission report from git commands."""

    git = runner or _run_git
    origin_divergence = _parse_divergence(
        git(["rev-list", "--left-right", "--count", "origin/main...HEAD"])
    )
    return GitHubSubmissionStatus(
        branch=git(["branch", "--show-current"]),
        head_commit=git(["rev-parse", "HEAD"]),
        head_short=git(["rev-parse", "--short", "HEAD"]),
        origin_url=git(["remote", "get-url", "origin"]),
        fork_url=git(["remote", "get-url", "fork"]),
        origin_main_commit=git(["rev-parse", "origin/main"]),
        origin_main_short=git(["rev-parse", "--short", "origin/main"]),
        fork_main_commit=git(["rev-parse", "fork/main"]),
        fork_main_short=git(["rev-parse", "--short", "fork/main"]),
        head_behind_origin_main_by=origin_divergence[0],
        head_ahead_origin_main_by=origin_divergence[1],
        tracking_issue_url=tracking_issue_url,
    )


def github_submission_status_payload(
    report: GitHubSubmissionStatus,
) -> dict[str, Any]:
    """Return a JSON-ready submission status payload."""

    return {
        "accepted": report.accepted,
        "submission_state": report.submission_state,
        "branch": report.branch,
        "head": {
            "commit": report.head_commit,
            "short": report.head_short,
        },
        "remotes": {
            "origin": report.origin_url,
            "fork": report.fork_url,
        },
        "fork_main": {
            "commit": report.fork_main_commit,
            "short": report.fork_main_short,
            "matches_head": report.fork_main_matches_head,
        },
        "origin_main": {
            "commit": report.origin_main_commit,
            "short": report.origin_main_short,
            "matches_head": report.origin_main_matches_head,
            "head_behind_by": report.head_behind_origin_main_by,
            "head_ahead_by": report.head_ahead_origin_main_by,
        },
        "tracking_issue": {
            "url": report.tracking_issue_url,
        },
    }


def format_github_submission_status(report: GitHubSubmissionStatus) -> str:
    """Format the local GitHub submission status for operators."""

    fork_line = (
        f"matches HEAD ({report.fork_main_short})"
        if report.fork_main_matches_head
        else f"not submitted to fork HEAD ({report.fork_main_short})"
    )
    return "\n".join([
        f"GitHub submission status: {report.submission_state}",
        f"Branch: {report.branch}",
        f"HEAD: {report.head_short}",
        f"fork/main: {fork_line}",
        (
            "origin/main: HEAD ahead by "
            f"{report.head_ahead_origin_main_by} commits, behind by "
            f"{report.head_behind_origin_main_by} commits"
        ),
        f"Origin: {report.origin_url}",
        f"Fork: {report.fork_url}",
        f"Tracking issue: {report.tracking_issue_url}",
    ])


def run_github_submission_cli(
    argv: list[str] | None = None,
    runner: GitRunner | None = None,
) -> int:
    """Run the GitHub submission status CLI."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.github_submission",
        description="Report local git evidence for AS GitHub submission status.",
    )
    parser.add_argument(
        "--tracking-issue",
        default=DEFAULT_TRACKING_ISSUE_URL,
        help="Tracking issue URL for upstream submission notes.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the submission status report.",
    )
    args = parser.parse_args(argv)

    report = build_github_submission_status(
        runner=runner,
        tracking_issue_url=args.tracking_issue,
    )
    if args.format == "json":
        print(json.dumps(github_submission_status_payload(report), sort_keys=True))
    else:
        print(format_github_submission_status(report))
    return 0 if report.accepted else 1


def _run_git(args: list[str]) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=Path.cwd(),
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _parse_divergence(value: str) -> tuple[int, int]:
    parts = value.replace("\t", " ").split()
    if len(parts) != 2:
        raise ValueError(f"malformed git divergence count: {value!r}")
    return int(parts[0]), int(parts[1])


if __name__ == "__main__":  # pragma: no cover - exercised by subprocess tests.
    raise SystemExit(run_github_submission_cli())
