"""Validate AS integration with pinned autarkenterprises/proflog."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_PIN_PATH = Path("sources/proflog_pin.json")
DEFAULT_WITNESS_PATH = Path("claims/proflog_sjas_witness.json")
DEFAULT_FRONTIER_PATH = Path("sources/proflog_frontier_status.json")


@dataclass(frozen=True)
class ProflogIntegrationReport:
    accepted: bool
    pinned_commit: str
    clone_path: Path | None
    fast_suite_ran: bool
    fast_suite_passed: bool | None
    failed_subjects: tuple[str, ...]


def load_proflog_pin(path: Path | str = DEFAULT_PIN_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_proflog_root(pin: dict[str, Any]) -> Path | None:
    env = pin.get("environment") or {}
    env_name = env.get("clone_path_env", "AS_PROFLOG_ROOT")
    if env_name in os.environ and os.environ[env_name].strip():
        return Path(os.environ[env_name]).expanduser()
    default = env.get("default_clone_path")
    if default:
        candidate = Path(default).expanduser()
        if candidate.is_dir():
            return candidate
    return None


def validate_proflog_pin_recorded(
    pin_path: Path | str = DEFAULT_PIN_PATH,
    witness_path: Path | str = DEFAULT_WITNESS_PATH,
    frontier_path: Path | str = DEFAULT_FRONTIER_PATH,
) -> ProflogIntegrationReport:
    """Validate pin, witness, and frontier status without requiring a local clone."""

    failed: list[str] = []
    pin = load_proflog_pin(pin_path)
    commit = pin.get("pinned_commit", "")
    if not commit or len(commit) < 12:
        failed.append("pin-commit")

    witness_path_p = Path(witness_path)
    if not witness_path_p.exists():
        failed.append("witness-file")
    else:
        witness = json.loads(witness_path_p.read_text(encoding="utf-8"))
        if witness.get("proflog_pin") != str(pin_path).replace("\\", "/"):
            failed.append("witness-pin-link")

    frontier_path_p = Path(frontier_path)
    if not frontier_path_p.exists():
        failed.append("frontier-file")
    else:
        frontier = json.loads(frontier_path_p.read_text(encoding="utf-8"))
        auth = frontier.get("authoritative_repository") or {}
        if auth.get("public_remote_head") != commit:
            failed.append("frontier-head-mismatch")
        if auth.get("implements_sjas_frontier_terms") is not True:
            failed.append("frontier-terms-flag")

    fast = pin.get("default_fast_suite") or {}
    if fast.get("result") != "passed":
        failed.append("fast-suite-not-recorded-passed")

    return ProflogIntegrationReport(
        accepted=not failed,
        pinned_commit=commit,
        clone_path=resolve_proflog_root(pin),
        fast_suite_ran=False,
        fast_suite_passed=None,
        failed_subjects=tuple(failed),
    )


def run_proflog_fast_suite(
    pin_path: Path | str = DEFAULT_PIN_PATH,
    *,
    timeout_seconds: int = 300,
) -> ProflogIntegrationReport:
    """Run lein test-proflog-fast in AS_PROFLOG_ROOT when clone is present."""

    base = validate_proflog_pin_recorded(pin_path)
    if not base.accepted:
        return base

    pin = load_proflog_pin(pin_path)
    root = resolve_proflog_root(pin)
    if root is None:
        return ProflogIntegrationReport(
            accepted=True,
            pinned_commit=base.pinned_commit,
            clone_path=None,
            fast_suite_ran=False,
            fast_suite_passed=None,
            failed_subjects=base.failed_subjects,
        )

    cmd = (pin.get("default_fast_suite") or {}).get("command", "lein test-proflog-fast")
    try:
        completed = subprocess.run(
            cmd,
            shell=True,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ProflogIntegrationReport(
            accepted=False,
            pinned_commit=base.pinned_commit,
            clone_path=root,
            fast_suite_ran=True,
            fast_suite_passed=False,
            failed_subjects=base.failed_subjects + ("fast-suite-timeout",),
        )

    passed = completed.returncode == 0
    failed = list(base.failed_subjects)
    if not passed:
        failed.append("fast-suite-failed")
    return ProflogIntegrationReport(
        accepted=not failed,
        pinned_commit=base.pinned_commit,
        clone_path=root,
        fast_suite_ran=True,
        fast_suite_passed=passed,
        failed_subjects=tuple(failed),
    )


def run_proflog_integration_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.proflog_integration",
        description="Validate or run pinned Proflog integration.",
    )
    parser.add_argument(
        "--run-fast",
        action="store_true",
        help="Run lein test-proflog-fast when AS_PROFLOG_ROOT is set.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    report = (
        run_proflog_fast_suite()
        if args.run_fast
        else validate_proflog_pin_recorded()
    )
    payload = {
        "accepted": report.accepted,
        "pinned_commit": report.pinned_commit,
        "clone_path": str(report.clone_path) if report.clone_path else None,
        "fast_suite_ran": report.fast_suite_ran,
        "fast_suite_passed": report.fast_suite_passed,
        "failed_subjects": list(report.failed_subjects),
    }
    if args.format == "json":
        print(json.dumps(payload, sort_keys=True))
    else:
        state = "accepted" if report.accepted else "rejected"
        print(f"Proflog integration: {state}")
        print(f"Pinned commit: {report.pinned_commit}")
        if report.clone_path:
            print(f"Clone: {report.clone_path}")
        if report.fast_suite_ran:
            print(f"Fast suite: {'passed' if report.fast_suite_passed else 'failed'}")
        if report.failed_subjects:
            print("Failed subjects: " + ", ".join(report.failed_subjects))
    return 0 if report.accepted else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_proflog_integration_cli())
