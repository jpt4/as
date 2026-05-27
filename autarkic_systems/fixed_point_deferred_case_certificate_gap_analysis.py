"""Gap analysis for deferred fixed-point construction certificate support.

ADR-0307 derives from the deferred-case readiness report. It separates
certificate-support gaps from proof-closure blockers so later work can see
where finite certificate support is still missing without treating readiness
or certificate support as a proof of any construction case.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_deferred_case_certificate_readiness import (
    load_fixed_point_deferred_case_certificate_readiness,
    validate_fixed_point_deferred_case_certificate_readiness,
)


DEFAULT_GAP_ANALYSIS = Path(
    "claims/fixed_point_deferred_case_certificate_gap_analysis.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_DEFERRED_CASE_KINDS = (
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_READINESS_PATH = "claims/fixed_point_deferred_case_certificate_readiness.json"
GAP_STATUS = "blocked-certificate-gap-analysis-not-proof"


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateGapAnalysisManifest:
    """Loaded manifest for deferred-case certificate gap analysis."""

    path: Path
    schema_version: int
    gap_analysis_id: str
    reviewed_at: str
    purpose: str
    deferred_case_certificate_readiness_path: str
    expected_gap_entry_count: int
    expected_deferred_case_kinds: tuple[str, ...]
    expected_certificate_gap_counts: dict[str, int]
    expected_missing_certificate_predecessors: dict[str, tuple[str, ...]]
    expected_open_proof_blocker_counts: dict[str, int]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateGapEntry:
    """One deferred case's certificate gaps and open proof blockers."""

    gap_id: str
    deferred_case_kind: str
    gap_status: str
    predecessor_case_kinds: tuple[str, ...]
    certificate_covered_predecessor_case_kinds: tuple[str, ...]
    missing_certificate_predecessor_case_kinds: tuple[str, ...]
    open_proof_blocker_case_kinds: tuple[str, ...]
    readiness_entry_accepted: bool
    proof_boundary_preserved: bool

    @property
    def predecessor_count(self) -> int:
        """Return the number of predecessor proof cases."""

        return len(self.predecessor_case_kinds)

    @property
    def certificate_covered_predecessor_count(self) -> int:
        """Return how many predecessors have finite certificate coverage."""

        return len(self.certificate_covered_predecessor_case_kinds)

    @property
    def certificate_gap_count(self) -> int:
        """Return how many predecessors still lack certificate coverage."""

        return len(self.missing_certificate_predecessor_case_kinds)

    @property
    def open_proof_blocker_count(self) -> int:
        """Return how many predecessor proof cases remain open blockers."""

        return len(self.open_proof_blocker_case_kinds)

    @property
    def accepted(self) -> bool:
        """Return whether this gap entry is accepted as non-promotional."""

        return (
            self.gap_status == GAP_STATUS
            and self.readiness_entry_accepted
            and self.proof_boundary_preserved
        )


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateGapValidation:
    """One validation result for deferred-case certificate gap analysis."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDeferredCaseCertificateGapReport:
    """Validation report for deferred-case certificate gap analysis."""

    manifest: FixedPointDeferredCaseCertificateGapAnalysisManifest
    deferred_case_certificate_readiness_path: Path
    willard_map_path: Path
    deferred_case_kinds: tuple[str, ...]
    readiness_accepted: bool
    proof_boundary_preserved: bool
    gap_entries: tuple[FixedPointDeferredCaseCertificateGapEntry, ...]
    results: tuple[FixedPointDeferredCaseCertificateGapValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every gap-analysis validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def gap_entry_count(self) -> int:
        """Return the number of deferred gap entries."""

        return len(self.gap_entries)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return compact failure subjects for automation and reports."""

        subjects: list[str] = []
        for result in self.results:
            if result.accepted:
                continue
            subject = _failed_subject_for_result(result.subject)
            if subject not in subjects:
                subjects.append(subject)
        return tuple(subjects)


@dataclass(frozen=True)
class _DependencyFailure:
    """Small report shim used when readiness cannot load."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    deferred_case_kinds: tuple[str, ...] = ()
    proof_boundary_preserved: bool = False
    readiness_entries: tuple[Any, ...] = ()


def load_fixed_point_deferred_case_certificate_gap_analysis(
    path: Path | str = DEFAULT_GAP_ANALYSIS,
) -> FixedPointDeferredCaseCertificateGapAnalysisManifest:
    """Load the deferred-case certificate gap-analysis manifest."""

    gap_path = Path(path)
    data = json.loads(gap_path.read_text(encoding="utf-8"))
    return FixedPointDeferredCaseCertificateGapAnalysisManifest(
        path=gap_path,
        schema_version=_required_int(data, "schema_version"),
        gap_analysis_id=_required_text(data, "gap_analysis_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        deferred_case_certificate_readiness_path=_required_text(
            data,
            "deferred_case_certificate_readiness_path",
        ),
        expected_gap_entry_count=_required_int(data, "expected_gap_entry_count"),
        expected_deferred_case_kinds=tuple(
            _required_text_list(data, "expected_deferred_case_kinds")
        ),
        expected_certificate_gap_counts=_required_int_map(
            data,
            "expected_certificate_gap_counts",
        ),
        expected_missing_certificate_predecessors=_required_tuple_map(
            data,
            "expected_missing_certificate_predecessors",
        ),
        expected_open_proof_blocker_counts=_required_int_map(
            data,
            "expected_open_proof_blocker_counts",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_deferred_case_certificate_gap_analysis(
    manifest: FixedPointDeferredCaseCertificateGapAnalysisManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDeferredCaseCertificateGapReport:
    """Validate deferred-case certificate gaps against readiness evidence."""

    checked_willard_map_path = Path(willard_map_path)
    readiness_path = Path(manifest.deferred_case_certificate_readiness_path)
    results: list[FixedPointDeferredCaseCertificateGapValidation] = [
        _accepted("manifest", f"loaded {manifest.gap_analysis_id}")
    ]
    results.extend(_validate_manifest(manifest))

    readiness_report = _load_readiness(readiness_path, checked_willard_map_path)
    results.extend(_validate_readiness_dependency(readiness_report))

    gap_entries = _derive_gap_entries(readiness_report)
    results.extend(
        _validate_gap_entries(
            manifest,
            readiness_report.deferred_case_kinds,
            readiness_report.accepted,
            readiness_report.proof_boundary_preserved,
            gap_entries,
        )
    )

    return FixedPointDeferredCaseCertificateGapReport(
        manifest=manifest,
        deferred_case_certificate_readiness_path=readiness_path,
        willard_map_path=checked_willard_map_path,
        deferred_case_kinds=readiness_report.deferred_case_kinds,
        readiness_accepted=readiness_report.accepted,
        proof_boundary_preserved=readiness_report.proof_boundary_preserved,
        gap_entries=tuple(gap_entries),
        results=tuple(results),
    )


def fixed_point_deferred_case_certificate_gap_analysis_payload(
    report: FixedPointDeferredCaseCertificateGapReport,
) -> dict[str, Any]:
    """Return a JSON-ready deferred-case certificate gap-analysis payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "gap_analysis_manifest": str(report.manifest.path),
        "gap_analysis_id": report.manifest.gap_analysis_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "deferred_case_certificate_readiness_path": str(
            report.deferred_case_certificate_readiness_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_gap_entry_count": report.manifest.expected_gap_entry_count,
        "expected_deferred_case_kinds": list(
            report.manifest.expected_deferred_case_kinds
        ),
        "expected_certificate_gap_counts": dict(
            report.manifest.expected_certificate_gap_counts
        ),
        "expected_missing_certificate_predecessors": {
            case_kind: list(predecessors)
            for case_kind, predecessors in (
                report.manifest.expected_missing_certificate_predecessors.items()
            )
        },
        "expected_open_proof_blocker_counts": dict(
            report.manifest.expected_open_proof_blocker_counts
        ),
        "deferred_case_kinds": list(report.deferred_case_kinds),
        "gap_entry_count": report.gap_entry_count,
        "observed_readiness_accepted": report.readiness_accepted,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "gap_entries": [_gap_entry_payload(entry) for entry in report.gap_entries],
        "result_count": len(report.results),
        "results": [
            {
                "subject": result.subject,
                "accepted": result.accepted,
                "detail": result.detail,
            }
            for result in report.results
        ],
    }


def format_fixed_point_deferred_case_certificate_gap_analysis_report(
    report: FixedPointDeferredCaseCertificateGapReport,
) -> str:
    """Format a concise deferred-case certificate gap-analysis report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point deferred case certificate gap analysis: {status}",
        f"Gap analysis: {report.manifest.gap_analysis_id}",
        f"Deferred cases: {_joined_or_none(report.deferred_case_kinds)}",
        f"Gap entries: {report.gap_entry_count}",
        "Readiness accepted: " + str(report.readiness_accepted).lower(),
        "Proof boundary preserved: " + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for entry in report.gap_entries:
        prefix = "blocked" if entry.accepted else "rejected"
        lines.append(
            f"{entry.deferred_case_kind}: {prefix} "
            f"(certificate gaps: {entry.certificate_gap_count}; "
            f"missing certificate predecessors: "
            f"{_joined_or_none(entry.missing_certificate_predecessor_case_kinds)}; "
            f"open proof blockers: "
            f"{_joined_or_none(entry.open_proof_blocker_case_kinds)})"
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_deferred_case_certificate_gap_analysis_cli(
    argv: list[str] | None = None,
) -> int:
    """Run deferred-case certificate gap-analysis validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_deferred_case_certificate_gap_analysis"
        ),
        description=(
            "Validate certificate-support gaps for deferred AS fixed-point "
            "construction cases."
        ),
    )
    parser.add_argument(
        "--gap-analysis",
        default=str(DEFAULT_GAP_ANALYSIS),
        help="Path to the deferred-case certificate gap-analysis manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_deferred_case_certificate_gap_analysis(
        args.gap_analysis
    )
    report = validate_fixed_point_deferred_case_certificate_gap_analysis(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_deferred_case_certificate_gap_analysis_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_deferred_case_certificate_gap_analysis_report(report))
    return 0 if report.accepted else 1


def _load_readiness(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_deferred_case_certificate_readiness(path)
        return validate_fixed_point_deferred_case_certificate_readiness(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-deferred-case-certificate-readiness-load",),
        )


def _validate_manifest(
    manifest: FixedPointDeferredCaseCertificateGapAnalysisManifest,
) -> list[FixedPointDeferredCaseCertificateGapValidation]:
    results: list[FixedPointDeferredCaseCertificateGapValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.gap_analysis_id == "as-fixed-point-deferred-case-certificate-gap-analysis-v1":
        results.append(_accepted("gap_analysis_id", "gap analysis id matches"))
    else:
        results.append(_rejected("gap_analysis_id", "unexpected gap analysis id"))

    if manifest.deferred_case_certificate_readiness_path == EXPECTED_READINESS_PATH:
        results.append(_accepted("deferred_case_certificate_readiness_path", "readiness referenced"))
    else:
        results.append(
            _rejected(
                "deferred_case_certificate_readiness_path",
                "expected "
                f"{EXPECTED_READINESS_PATH} but found "
                f"{manifest.deferred_case_certificate_readiness_path}",
            )
        )

    if manifest.expected_gap_entry_count == 3:
        results.append(_accepted("expected_gap_entry_count", "three entries"))
    else:
        results.append(_rejected("expected_gap_entry_count", "expected three entries"))

    if manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS:
        results.append(_accepted("expected_deferred_case_kinds", "deferred cases match"))
    else:
        results.append(
            _rejected("expected_deferred_case_kinds", "deferred case mismatch")
        )

    results.extend(
        _validate_required_map_keys(
            manifest.expected_certificate_gap_counts,
            "expected_certificate_gap_counts",
        )
    )
    results.extend(
        _validate_required_map_keys(
            manifest.expected_missing_certificate_predecessors,
            "expected_missing_certificate_predecessors",
        )
    )
    results.extend(
        _validate_required_map_keys(
            manifest.expected_open_proof_blocker_counts,
            "expected_open_proof_blocker_counts",
        )
    )

    missing_non_claims = [
        non_claim
        for non_claim in REQUIRED_NON_CLAIMS
        if non_claim not in manifest.non_claims
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    else:
        results.append(_accepted("non_claims", "all non-claims preserved"))
    return results


def _validate_required_map_keys(
    values: dict[str, Any],
    subject: str,
) -> list[FixedPointDeferredCaseCertificateGapValidation]:
    missing = [case_kind for case_kind in REQUIRED_DEFERRED_CASE_KINDS if case_kind not in values]
    if missing:
        return [_rejected(subject, "missing cases: " + ", ".join(missing))]
    return [_accepted(subject, "all cases covered")]


def _validate_readiness_dependency(
    readiness_report: Any,
) -> list[FixedPointDeferredCaseCertificateGapValidation]:
    if readiness_report.accepted:
        return [_accepted("deferred_case_certificate_readiness", "readiness accepted")]
    return [
        _rejected(
            "deferred_case_certificate_readiness",
            "readiness rejected: " + _joined_or_none(readiness_report.failed_subjects),
        )
    ]


def _derive_gap_entries(
    readiness_report: Any,
) -> list[FixedPointDeferredCaseCertificateGapEntry]:
    if not readiness_report.accepted:
        return []

    entries: list[FixedPointDeferredCaseCertificateGapEntry] = []
    for readiness in readiness_report.readiness_entries:
        covered = set(readiness.certificate_covered_predecessor_case_kinds)
        missing = tuple(
            predecessor
            for predecessor in readiness.predecessor_case_kinds
            if predecessor not in covered
        )
        entries.append(
            FixedPointDeferredCaseCertificateGapEntry(
                gap_id=(
                    "AS-FIXED-POINT-DEFERRED-CASE-CERTIFICATE-GAP-"
                    + readiness.deferred_case_kind.upper().replace("-", "_")
                ),
                deferred_case_kind=readiness.deferred_case_kind,
                gap_status=GAP_STATUS,
                predecessor_case_kinds=readiness.predecessor_case_kinds,
                certificate_covered_predecessor_case_kinds=(
                    readiness.certificate_covered_predecessor_case_kinds
                ),
                missing_certificate_predecessor_case_kinds=missing,
                open_proof_blocker_case_kinds=(
                    readiness.blocking_open_predecessor_case_kinds
                ),
                readiness_entry_accepted=readiness.accepted,
                proof_boundary_preserved=readiness.proof_boundary_preserved,
            )
        )
    return entries


def _validate_gap_entries(
    manifest: FixedPointDeferredCaseCertificateGapAnalysisManifest,
    deferred_case_kinds: tuple[str, ...],
    readiness_accepted: bool,
    proof_boundary_preserved: bool,
    gap_entries: list[FixedPointDeferredCaseCertificateGapEntry],
) -> list[FixedPointDeferredCaseCertificateGapValidation]:
    results: list[FixedPointDeferredCaseCertificateGapValidation] = []
    if deferred_case_kinds == manifest.expected_deferred_case_kinds:
        results.append(_accepted("deferred_case_kinds", "deferred cases match"))
    else:
        results.append(_rejected("deferred_case_kinds", "deferred case mismatch"))

    if len(gap_entries) == manifest.expected_gap_entry_count:
        results.append(_accepted("gap_entry_count", "gap entry count matches"))
    else:
        results.append(
            _rejected(
                "gap_entry_count",
                "gap entry count mismatch: expected "
                f"{manifest.expected_gap_entry_count} but found {len(gap_entries)}",
            )
        )

    if readiness_accepted:
        results.append(_accepted("readiness", "readiness accepted"))
    else:
        results.append(_rejected("readiness", "readiness rejected"))

    if proof_boundary_preserved:
        results.append(_accepted("proof_boundary", "proof boundary preserved"))
    else:
        results.append(_rejected("proof_boundary", "proof boundary not preserved"))

    results.extend(_validate_entry_expectations(manifest, gap_entries))

    rejected_entries = [
        entry.deferred_case_kind for entry in gap_entries if not entry.accepted
    ]
    if rejected_entries:
        results.append(
            _rejected("gap_entries", "rejected entries: " + ", ".join(rejected_entries))
        )
    else:
        results.append(_accepted("gap_entries", "all gap entries blocked"))
    return results


def _validate_entry_expectations(
    manifest: FixedPointDeferredCaseCertificateGapAnalysisManifest,
    gap_entries: list[FixedPointDeferredCaseCertificateGapEntry],
) -> list[FixedPointDeferredCaseCertificateGapValidation]:
    gap_count_mismatches: list[str] = []
    missing_predecessor_mismatches: list[str] = []
    blocker_count_mismatches: list[str] = []
    for entry in gap_entries:
        expected_gap_count = manifest.expected_certificate_gap_counts.get(
            entry.deferred_case_kind
        )
        expected_missing = manifest.expected_missing_certificate_predecessors.get(
            entry.deferred_case_kind
        )
        expected_blockers = manifest.expected_open_proof_blocker_counts.get(
            entry.deferred_case_kind
        )
        if expected_gap_count != entry.certificate_gap_count:
            gap_count_mismatches.append(
                f"{entry.deferred_case_kind} expected {expected_gap_count} "
                f"found {entry.certificate_gap_count}"
            )
        if expected_missing != entry.missing_certificate_predecessor_case_kinds:
            missing_predecessor_mismatches.append(
                f"{entry.deferred_case_kind} expected "
                f"{_joined_or_none(expected_missing or ())} found "
                f"{_joined_or_none(entry.missing_certificate_predecessor_case_kinds)}"
            )
        if expected_blockers != entry.open_proof_blocker_count:
            blocker_count_mismatches.append(
                f"{entry.deferred_case_kind} expected {expected_blockers} "
                f"found {entry.open_proof_blocker_count}"
            )

    results: list[FixedPointDeferredCaseCertificateGapValidation] = []
    if gap_count_mismatches:
        results.append(
            _rejected(
                "certificate_gap_counts",
                "certificate gap count mismatch: " + "; ".join(gap_count_mismatches),
            )
        )
    else:
        results.append(_accepted("certificate_gap_counts", "gap counts match"))

    if missing_predecessor_mismatches:
        results.append(
            _rejected(
                "missing_certificate_predecessors",
                "missing certificate predecessor mismatch: "
                + "; ".join(missing_predecessor_mismatches),
            )
        )
    else:
        results.append(
            _accepted(
                "missing_certificate_predecessors",
                "missing certificate predecessors match",
            )
        )

    if blocker_count_mismatches:
        results.append(
            _rejected(
                "open_proof_blocker_counts",
                "open proof blocker count mismatch: "
                + "; ".join(blocker_count_mismatches),
            )
        )
    else:
        results.append(
            _accepted("open_proof_blocker_counts", "open proof blocker counts match")
        )
    return results


def _gap_entry_payload(entry: FixedPointDeferredCaseCertificateGapEntry) -> dict[str, Any]:
    return {
        "gap_id": entry.gap_id,
        "deferred_case_kind": entry.deferred_case_kind,
        "gap_status": entry.gap_status,
        "predecessor_case_kinds": list(entry.predecessor_case_kinds),
        "predecessor_count": entry.predecessor_count,
        "certificate_covered_predecessor_case_kinds": list(
            entry.certificate_covered_predecessor_case_kinds
        ),
        "certificate_covered_predecessor_count": (
            entry.certificate_covered_predecessor_count
        ),
        "missing_certificate_predecessor_case_kinds": list(
            entry.missing_certificate_predecessor_case_kinds
        ),
        "certificate_gap_count": entry.certificate_gap_count,
        "open_proof_blocker_case_kinds": list(entry.open_proof_blocker_case_kinds),
        "open_proof_blocker_count": entry.open_proof_blocker_count,
        "observed_readiness_entry_accepted": entry.readiness_entry_accepted,
        "observed_proof_boundary_preserved": entry.proof_boundary_preserved,
        "accepted": entry.accepted,
    }


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDeferredCaseCertificateGapValidation:
    return FixedPointDeferredCaseCertificateGapValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointDeferredCaseCertificateGapValidation:
    return FixedPointDeferredCaseCertificateGapValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_deferred_case_kinds", "deferred_case_kinds"}:
        return "fixed-point-deferred-case-certificate-gap-analysis-deferred-cases"
    if subject in {"expected_gap_entry_count", "gap_entry_count"}:
        return "fixed-point-deferred-case-certificate-gap-analysis-count"
    if subject in {"expected_certificate_gap_counts", "certificate_gap_counts"}:
        return "fixed-point-deferred-case-certificate-gap-analysis-gap-counts"
    if subject in {
        "expected_missing_certificate_predecessors",
        "missing_certificate_predecessors",
    }:
        return "fixed-point-deferred-case-certificate-gap-analysis-missing-predecessors"
    if subject in {
        "expected_open_proof_blocker_counts",
        "open_proof_blocker_counts",
    }:
        return "fixed-point-deferred-case-certificate-gap-analysis-proof-blockers"
    if subject == "non_claims":
        return "fixed-point-deferred-case-certificate-gap-analysis-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-deferred-case-certificate-gap-analysis-boundary"
    if subject == "gap_entries":
        return "fixed-point-deferred-case-certificate-gap-analysis-entry"
    if subject.endswith("_path"):
        return "fixed-point-deferred-case-certificate-gap-analysis-path"
    return subject


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return value


def _required_int_map(data: dict[str, Any], key: str) -> dict[str, int]:
    value = data.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{key} must be a non-empty object")
    result: dict[str, int] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError(f"{key} must have non-empty text keys")
        if not isinstance(item_value, int):
            raise ValueError(f"{key} values must be integers")
        result[item_key] = item_value
    return result


def _required_tuple_map(data: dict[str, Any], key: str) -> dict[str, tuple[str, ...]]:
    value = data.get(key)
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{key} must be a non-empty object")
    result: dict[str, tuple[str, ...]] = {}
    for item_key, item_value in value.items():
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError(f"{key} must have non-empty text keys")
        if not isinstance(item_value, list):
            raise ValueError(f"{key} values must be lists")
        if any(not isinstance(item, str) or not item.strip() for item in item_value):
            raise ValueError(f"{key} values must contain only non-empty strings")
        result[item_key] = tuple(item_value)
    return result


def _joined_or_none(items: tuple[str, ...]) -> str:
    if not items:
        return "none"
    return ", ".join(items)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_deferred_case_certificate_gap_analysis_cli())
