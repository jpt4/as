"""Validate Sean fork SJAS → Proflog correlation map against AS integration artifacts."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autarkic_systems.proflog_integration import (
    DEFAULT_PIN_PATH,
    DEFAULT_WITNESS_PATH,
    validate_proflog_pin_recorded,
)

DEFAULT_MAP_PATH = Path("docs/correlation/sean-fork-sjas-proflog-map.json")
REQUIRED_TRANSLATION_KEYS = ("status",)
IMPLEMENTED_STATUSES = frozenset(
    {
        "implemented-in-proflog",
        "resolved-via-pin",
        "replaced-by-proflog-codebook",
        "replaced-by-proflog-subst",
        "replaced-do-not-duplicate",
        "sjas-in-proflog-uc-in-as",
        "documented-in-as-only",
    }
)
TERMINAL_STATUSES = frozenset(
    {
        "obsolete-naive-route",
        "not-needed-separate-in-proflog",
    }
)
ALLOWED_STATUSES = IMPLEMENTED_STATUSES | TERMINAL_STATUSES


@dataclass(frozen=True)
class SeanForkSjasCorrelationReport:
    accepted: bool
    translation_count: int
    implemented_count: int
    obsolete_count: int
    failed_subjects: tuple[str, ...]


def load_correlation_map(path: Path | str = DEFAULT_MAP_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_sean_fork_sjas_correlation(
    map_path: Path | str = DEFAULT_MAP_PATH,
    pin_path: Path | str = DEFAULT_PIN_PATH,
    witness_path: Path | str = DEFAULT_WITNESS_PATH,
) -> SeanForkSjasCorrelationReport:
    """Ensure the correlation map aligns with pinned Proflog integration."""

    failed: list[str] = []
    integration = validate_proflog_pin_recorded(pin_path, witness_path)
    if not integration.accepted:
        failed.extend(f"integration:{s}" for s in integration.failed_subjects)

    map_path_p = Path(map_path)
    if not map_path_p.exists():
        return SeanForkSjasCorrelationReport(
            accepted=False,
            translation_count=0,
            implemented_count=0,
            obsolete_count=0,
            failed_subjects=tuple(["map-file"]),
        )

    correlation = load_correlation_map(map_path_p)
    pin_ref = str(correlation.get("proflog_pin", "")).replace("\\", "/")
    if pin_ref != str(pin_path).replace("\\", "/"):
        failed.append("map-pin-path")

    translations = correlation.get("translations")
    if not isinstance(translations, list) or not translations:
        failed.append("translations-empty")
        translations = []

    implemented = 0
    obsolete = 0
    for index, entry in enumerate(translations):
        if not isinstance(entry, dict):
            failed.append(f"translation-{index}-shape")
            continue
        status = entry.get("status")
        if not status:
            failed.append(f"translation-{index}-status")
        elif status in TERMINAL_STATUSES:
            obsolete += 1
        elif status in IMPLEMENTED_STATUSES:
            implemented += 1
        elif status in ALLOWED_STATUSES:
            implemented += 1
        else:
            failed.append(f"translation-{index}-unknown-status")
        for key in REQUIRED_TRANSLATION_KEYS:
            if key not in entry:
                failed.append(f"translation-{index}-missing-{key}")

    contrib = Path("proflog-contrib/test/proflog/as_sean_fork_correlation_test.clj")
    if not contrib.is_file():
        failed.append("proflog-contrib-test")

    witness_path_p = Path(witness_path)
    if witness_path_p.is_file():
        witness = json.loads(witness_path_p.read_text(encoding="utf-8"))
        if witness.get("sean_fork_correlation_map") != str(map_path_p).replace("\\", "/"):
            failed.append("witness-map-link")

    return SeanForkSjasCorrelationReport(
        accepted=not failed,
        translation_count=len(translations),
        implemented_count=implemented,
        obsolete_count=obsolete,
        failed_subjects=tuple(failed),
    )


def run_sean_fork_sjas_correlation_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.sean_fork_sjas_correlation",
        description="Validate Sean fork SJAS correlation with pinned Proflog.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)

    report = validate_sean_fork_sjas_correlation()
    payload = {
        "accepted": report.accepted,
        "translation_count": report.translation_count,
        "implemented_count": report.implemented_count,
        "obsolete_count": report.obsolete_count,
        "failed_subjects": list(report.failed_subjects),
    }
    if args.format == "json":
        print(json.dumps(payload, sort_keys=True))
    else:
        state = "accepted" if report.accepted else "rejected"
        print(f"Sean fork SJAS correlation: {state}")
        print(f"Translations: {report.translation_count}")
        print(
            f"Implemented or delegated: {report.implemented_count}; "
            f"obsolete or AS-only: {report.obsolete_count}"
        )
        if report.failed_subjects:
            print("Failed subjects: " + ", ".join(report.failed_subjects))
    return 0 if report.accepted else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run_sean_fork_sjas_correlation_cli())
