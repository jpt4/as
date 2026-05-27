"""Expanded available predecessor certificate coverage for fixed-point cases.

ADR-0310 extends ADR-0308's available predecessor certificate coverage with
the substitution-representability certificate introduced by ADR-0309. The
expanded view updates downstream certificate-support visibility while keeping
all proof cases blocked until proof closure evidence exists.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_available_predecessor_certificate_coverage import (
    load_fixed_point_available_predecessor_certificate_coverage,
    validate_fixed_point_available_predecessor_certificate_coverage,
)
from autarkic_systems.fixed_point_substitution_representability_certificate import (
    load_fixed_point_substitution_representability_certificate,
    validate_fixed_point_substitution_representability_certificate,
)


DEFAULT_COVERAGE = Path(
    "claims/fixed_point_expanded_available_predecessor_certificate_coverage.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_DEFERRED_CASE_KINDS = (
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
REQUIRED_AVAILABLE_CERTIFICATE_SUBJECTS = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
    "substitution-representability-proof",
    "bridge-equality-proof",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "available_predecessor_certificate_coverage_path": (
        "claims/fixed_point_available_predecessor_certificate_coverage.json"
    ),
    "substitution_representability_certificate_path": (
        "claims/fixed_point_substitution_representability_certificate.json"
    ),
}
EXPANDED_COVERAGE_STATUS = "blocked-expanded-certificate-coverage-not-proof"


@dataclass(frozen=True)
class FixedPointExpandedAvailablePredecessorCertificateCoverageManifest:
    """Loaded manifest for expanded predecessor certificate coverage."""

    path: Path
    schema_version: int
    coverage_id: str
    reviewed_at: str
    purpose: str
    available_predecessor_certificate_coverage_path: str
    substitution_representability_certificate_path: str
    expected_deferred_case_count: int
    expected_deferred_case_kinds: tuple[str, ...]
    expected_available_certificate_subjects: tuple[str, ...]
    expected_total_available_certificate_step_count: int
    expected_missing_certificate_predecessors: dict[str, tuple[str, ...]]
    expected_open_proof_blocker_counts: dict[str, int]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointExpandedAvailableCertificateSubject:
    """One available finite predecessor certificate subject."""

    case_kind: str
    certificate_set_id: str
    certificate_id: str
    certificate_step_count: int
    certificate_accepted: bool


@dataclass(frozen=True)
class FixedPointExpandedAvailablePredecessorCertificateCoverageEntry:
    """Expanded certificate coverage for one deferred construction case."""

    coverage_entry_id: str
    deferred_case_kind: str
    coverage_status: str
    predecessor_case_kinds: tuple[str, ...]
    certificate_covered_predecessor_case_kinds: tuple[str, ...]
    missing_certificate_predecessor_case_kinds: tuple[str, ...]
    open_proof_blocker_case_kinds: tuple[str, ...]
    base_coverage_entry_accepted: bool
    proof_boundary_preserved: bool

    @property
    def predecessor_count(self) -> int:
        """Return the number of predecessor proof cases."""

        return len(self.predecessor_case_kinds)

    @property
    def certificate_covered_predecessor_count(self) -> int:
        """Return how many predecessors have available certificate support."""

        return len(self.certificate_covered_predecessor_case_kinds)

    @property
    def missing_certificate_predecessor_count(self) -> int:
        """Return how many predecessors lack available certificate support."""

        return len(self.missing_certificate_predecessor_case_kinds)

    @property
    def open_proof_blocker_count(self) -> int:
        """Return how many predecessor proof cases remain open blockers."""

        return len(self.open_proof_blocker_case_kinds)

    @property
    def accepted(self) -> bool:
        """Return whether this expanded coverage entry accepted."""

        return (
            self.coverage_status == EXPANDED_COVERAGE_STATUS
            and self.base_coverage_entry_accepted
            and self.proof_boundary_preserved
        )


@dataclass(frozen=True)
class FixedPointExpandedAvailablePredecessorCertificateCoverageValidation:
    """One validation result for expanded predecessor certificate coverage."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointExpandedAvailablePredecessorCertificateCoverageReport:
    """Validation report for expanded predecessor certificate coverage."""

    manifest: FixedPointExpandedAvailablePredecessorCertificateCoverageManifest
    available_predecessor_certificate_coverage_path: Path
    substitution_representability_certificate_path: Path
    willard_map_path: Path
    base_coverage_accepted: bool
    substitution_certificate_accepted: bool
    proof_boundary_preserved: bool
    available_certificates: tuple[FixedPointExpandedAvailableCertificateSubject, ...]
    coverage_entries: tuple[
        FixedPointExpandedAvailablePredecessorCertificateCoverageEntry, ...
    ]
    results: tuple[
        FixedPointExpandedAvailablePredecessorCertificateCoverageValidation, ...
    ]

    @property
    def accepted(self) -> bool:
        """Return whether every expanded coverage validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def coverage_entry_count(self) -> int:
        """Return the number of deferred coverage entries."""

        return len(self.coverage_entries)

    @property
    def available_certificate_subjects(self) -> tuple[str, ...]:
        """Return available certificate subjects in manifest order."""

        return tuple(certificate.case_kind for certificate in self.available_certificates)

    @property
    def total_available_certificate_step_count(self) -> int:
        """Return total finite certificate steps across available subjects."""

        return sum(
            certificate.certificate_step_count
            for certificate in self.available_certificates
        )

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
    """Small report shim used when a dependency cannot load."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    available_certificates: tuple[Any, ...] = ()
    coverage_entries: tuple[Any, ...] = ()
    certificates: tuple[Any, ...] = ()
    proof_boundary_preserved: bool = False


def load_fixed_point_expanded_available_predecessor_certificate_coverage(
    path: Path | str = DEFAULT_COVERAGE,
) -> FixedPointExpandedAvailablePredecessorCertificateCoverageManifest:
    """Load the expanded available predecessor certificate coverage manifest."""

    coverage_path = Path(path)
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    return FixedPointExpandedAvailablePredecessorCertificateCoverageManifest(
        path=coverage_path,
        schema_version=_required_int(data, "schema_version"),
        coverage_id=_required_text(data, "coverage_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        available_predecessor_certificate_coverage_path=_required_text(
            data,
            "available_predecessor_certificate_coverage_path",
        ),
        substitution_representability_certificate_path=_required_text(
            data,
            "substitution_representability_certificate_path",
        ),
        expected_deferred_case_count=_required_int(
            data,
            "expected_deferred_case_count",
        ),
        expected_deferred_case_kinds=tuple(
            _required_text_list(data, "expected_deferred_case_kinds")
        ),
        expected_available_certificate_subjects=tuple(
            _required_text_list(data, "expected_available_certificate_subjects")
        ),
        expected_total_available_certificate_step_count=_required_int(
            data,
            "expected_total_available_certificate_step_count",
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


def validate_fixed_point_expanded_available_predecessor_certificate_coverage(
    manifest: FixedPointExpandedAvailablePredecessorCertificateCoverageManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointExpandedAvailablePredecessorCertificateCoverageReport:
    """Validate expanded predecessor certificate coverage."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointExpandedAvailablePredecessorCertificateCoverageValidation] = [
        _accepted("manifest", f"loaded {manifest.coverage_id}")
    ]
    results.extend(_validate_manifest(manifest))

    base_coverage_report = _load_base_coverage(
        paths["available_predecessor_certificate_coverage_path"],
        checked_willard_map_path,
    )
    substitution_certificate_report = _load_substitution_certificate(
        paths["substitution_representability_certificate_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(base_coverage_report, substitution_certificate_report)
    )

    available_certificates = _derive_available_certificates(
        base_coverage_report,
        substitution_certificate_report,
    )
    proof_boundary_preserved = (
        bool(getattr(base_coverage_report, "proof_boundary_preserved", False))
        and _substitution_certificate_preserves_boundary(
            substitution_certificate_report
        )
    )
    coverage_entries = _derive_coverage_entries(
        base_coverage_report,
        available_certificates,
        proof_boundary_preserved,
    )
    results.extend(
        _validate_coverage(
            manifest,
            available_certificates,
            proof_boundary_preserved,
            coverage_entries,
        )
    )

    return FixedPointExpandedAvailablePredecessorCertificateCoverageReport(
        manifest=manifest,
        available_predecessor_certificate_coverage_path=paths[
            "available_predecessor_certificate_coverage_path"
        ],
        substitution_representability_certificate_path=paths[
            "substitution_representability_certificate_path"
        ],
        willard_map_path=checked_willard_map_path,
        base_coverage_accepted=base_coverage_report.accepted,
        substitution_certificate_accepted=substitution_certificate_report.accepted,
        proof_boundary_preserved=proof_boundary_preserved,
        available_certificates=tuple(available_certificates),
        coverage_entries=tuple(coverage_entries),
        results=tuple(results),
    )


def fixed_point_expanded_available_predecessor_certificate_coverage_payload(
    report: FixedPointExpandedAvailablePredecessorCertificateCoverageReport,
) -> dict[str, Any]:
    """Return a JSON-ready expanded predecessor coverage payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "coverage_manifest": str(report.manifest.path),
        "coverage_id": report.manifest.coverage_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "available_predecessor_certificate_coverage_path": str(
            report.available_predecessor_certificate_coverage_path
        ),
        "substitution_representability_certificate_path": str(
            report.substitution_representability_certificate_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_deferred_case_count": report.manifest.expected_deferred_case_count,
        "expected_deferred_case_kinds": list(
            report.manifest.expected_deferred_case_kinds
        ),
        "expected_available_certificate_subjects": list(
            report.manifest.expected_available_certificate_subjects
        ),
        "expected_total_available_certificate_step_count": (
            report.manifest.expected_total_available_certificate_step_count
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
        "available_certificate_subjects": list(
            report.available_certificate_subjects
        ),
        "total_available_certificate_step_count": (
            report.total_available_certificate_step_count
        ),
        "coverage_entry_count": report.coverage_entry_count,
        "observed_base_coverage_accepted": report.base_coverage_accepted,
        "observed_substitution_certificate_accepted": (
            report.substitution_certificate_accepted
        ),
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "available_certificates": [
            _available_certificate_payload(certificate)
            for certificate in report.available_certificates
        ],
        "coverage_entries": [
            _coverage_entry_payload(entry) for entry in report.coverage_entries
        ],
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


def format_fixed_point_expanded_available_predecessor_certificate_coverage_report(
    report: FixedPointExpandedAvailablePredecessorCertificateCoverageReport,
) -> str:
    """Format a concise expanded predecessor certificate coverage report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point expanded available predecessor certificate coverage: {status}",
        f"Coverage: {report.manifest.coverage_id}",
        "Available certificate subjects: "
        + _joined_or_none(report.available_certificate_subjects),
        "Total available certificate steps: "
        + str(report.total_available_certificate_step_count),
        f"Coverage entries: {report.coverage_entry_count}",
        "Proof boundary preserved: " + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for entry in report.coverage_entries:
        prefix = "blocked" if entry.accepted else "rejected"
        lines.append(
            f"{entry.deferred_case_kind}: {prefix} "
            f"(covered predecessors: "
            f"{entry.certificate_covered_predecessor_count}/"
            f"{entry.predecessor_count}; "
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


def run_fixed_point_expanded_available_predecessor_certificate_coverage_cli(
    argv: list[str] | None = None,
) -> int:
    """Run expanded predecessor certificate coverage validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_expanded_available_predecessor_certificate_coverage"
        ),
        description=(
            "Validate expanded finite predecessor certificate coverage for "
            "deferred AS fixed-point construction cases."
        ),
    )
    parser.add_argument(
        "--coverage",
        default=str(DEFAULT_COVERAGE),
        help="Path to the expanded predecessor certificate coverage manifest.",
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

    manifest = load_fixed_point_expanded_available_predecessor_certificate_coverage(
        args.coverage
    )
    report = validate_fixed_point_expanded_available_predecessor_certificate_coverage(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_expanded_available_predecessor_certificate_coverage_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_expanded_available_predecessor_certificate_coverage_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointExpandedAvailablePredecessorCertificateCoverageManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "available_predecessor_certificate_coverage_path": _resolve_path(
            manifest.path,
            manifest.available_predecessor_certificate_coverage_path,
        ),
        "substitution_representability_certificate_path": _resolve_path(
            manifest.path,
            manifest.substitution_representability_certificate_path,
        ),
    }


def _resolve_path(base_path: Path, value: str) -> Path:
    """Resolve a manifest-local path while preserving root-relative paths."""

    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    candidate = base_path.parent / path
    if candidate.exists():
        return candidate
    return path


def _load_base_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the prior available predecessor coverage surface."""

    try:
        manifest = load_fixed_point_available_predecessor_certificate_coverage(path)
        return validate_fixed_point_available_predecessor_certificate_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-available-predecessor-coverage-load",),
        )


def _load_substitution_certificate(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the substitution-representability certificate."""

    try:
        manifest = load_fixed_point_substitution_representability_certificate(path)
        return validate_fixed_point_substitution_representability_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-substitution-representability-certificate-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointExpandedAvailablePredecessorCertificateCoverageManifest,
) -> list[FixedPointExpandedAvailablePredecessorCertificateCoverageValidation]:
    """Validate manifest-local constants and non-claim guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "coverage_id",
            (
                manifest.coverage_id
                == "as-fixed-point-expanded-available-predecessor-certificate-coverage-v1"
            ),
            "coverage id matches",
        ),
        *[
            _check(
                key,
                getattr(manifest, key) == expected,
                f"{expected} referenced",
            )
            for key, expected in EXPECTED_DEPENDENCY_PATHS.items()
        ],
        _check(
            "expected_deferred_case_count",
            manifest.expected_deferred_case_count == 3,
            "three cases",
        ),
        _check(
            "expected_deferred_case_kinds",
            manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS,
            "deferred cases match",
        ),
        _check(
            "expected_available_certificate_subjects",
            (
                manifest.expected_available_certificate_subjects
                == REQUIRED_AVAILABLE_CERTIFICATE_SUBJECTS
            ),
            "available certificate subjects match",
        ),
        _check(
            "expected_total_available_certificate_step_count",
            manifest.expected_total_available_certificate_step_count == 27,
            "twenty-seven steps",
        ),
        _check(
            "expected_missing_certificate_predecessors",
            set(manifest.expected_missing_certificate_predecessors)
            == set(REQUIRED_DEFERRED_CASE_KINDS),
            "all cases covered",
        ),
        _check(
            "expected_open_proof_blocker_counts",
            set(manifest.expected_open_proof_blocker_counts)
            == set(REQUIRED_DEFERRED_CASE_KINDS),
            "all cases covered",
        ),
        _check(
            "non_claims",
            manifest.non_claims == REQUIRED_NON_CLAIMS,
            "all non-claims preserved",
        ),
    ]


def _validate_dependencies(
    base_coverage_report: Any,
    substitution_certificate_report: Any,
) -> list[FixedPointExpandedAvailablePredecessorCertificateCoverageValidation]:
    """Validate that dependency reports accepted before expanded derivation."""

    return [
        _check(
            "base_available_predecessor_certificate_coverage",
            base_coverage_report.accepted,
            "base coverage accepted",
            "base coverage rejected: "
            + _joined_or_none(getattr(base_coverage_report, "failed_subjects", ())),
        ),
        _check(
            "substitution_representability_certificate",
            substitution_certificate_report.accepted,
            "substitution certificate accepted",
            "substitution certificate rejected: "
            + _joined_or_none(
                getattr(substitution_certificate_report, "failed_subjects", ())
            ),
        ),
    ]


def _derive_available_certificates(
    base_coverage_report: Any,
    substitution_certificate_report: Any,
) -> list[FixedPointExpandedAvailableCertificateSubject]:
    """Return available certificates in ADR-0310 manifest order."""

    by_subject = {
        certificate.case_kind: FixedPointExpandedAvailableCertificateSubject(
            case_kind=certificate.case_kind,
            certificate_set_id=certificate.certificate_set_id,
            certificate_id=certificate.certificate_id,
            certificate_step_count=certificate.certificate_step_count,
            certificate_accepted=certificate.certificate_accepted,
        )
        for certificate in getattr(base_coverage_report, "available_certificates", ())
    }
    by_subject["substitution-representability-proof"] = (
        _substitution_certificate_subject(substitution_certificate_report)
    )
    return [
        by_subject.get(subject, _missing_certificate_subject(subject))
        for subject in REQUIRED_AVAILABLE_CERTIFICATE_SUBJECTS
    ]


def _missing_certificate_subject(
    case_kind: str,
) -> FixedPointExpandedAvailableCertificateSubject:
    """Build a rejected placeholder when a dependency cannot supply a subject."""

    return FixedPointExpandedAvailableCertificateSubject(
        case_kind=case_kind,
        certificate_set_id="",
        certificate_id="",
        certificate_step_count=0,
        certificate_accepted=False,
    )


def _substitution_certificate_subject(
    substitution_certificate_report: Any,
) -> FixedPointExpandedAvailableCertificateSubject:
    """Build the available subject for ADR-0309 substitution certificate support."""

    certificates = tuple(getattr(substitution_certificate_report, "certificates", ()))
    certificate = certificates[0] if certificates else None
    return FixedPointExpandedAvailableCertificateSubject(
        case_kind="substitution-representability-proof",
        certificate_set_id=getattr(
            getattr(substitution_certificate_report, "manifest", None),
            "certificate_set_id",
            "",
        ),
        certificate_id=getattr(certificate, "certificate_id", ""),
        certificate_step_count=getattr(
            substitution_certificate_report,
            "certificate_step_count",
            0,
        ),
        certificate_accepted=bool(getattr(certificate, "accepted", False)),
    )


def _substitution_certificate_preserves_boundary(
    substitution_certificate_report: Any,
) -> bool:
    """Return whether the substitution certificate kept its proof boundary."""

    certificates = tuple(getattr(substitution_certificate_report, "certificates", ()))
    return bool(certificates) and all(
        bool(getattr(certificate, "proof_boundary_preserved", False))
        for certificate in certificates
    )


def _derive_coverage_entries(
    base_coverage_report: Any,
    available_certificates: list[FixedPointExpandedAvailableCertificateSubject],
    proof_boundary_preserved: bool,
) -> list[FixedPointExpandedAvailablePredecessorCertificateCoverageEntry]:
    """Derive expanded coverage entries from the base predecessor graph."""

    available_subjects = {
        certificate.case_kind
        for certificate in available_certificates
        if certificate.certificate_accepted
    }
    entries: list[FixedPointExpandedAvailablePredecessorCertificateCoverageEntry] = []
    for entry in getattr(base_coverage_report, "coverage_entries", ()):
        predecessors = tuple(getattr(entry, "predecessor_case_kinds", ()))
        covered = tuple(
            predecessor
            for predecessor in predecessors
            if predecessor in available_subjects
        )
        missing = tuple(
            predecessor
            for predecessor in predecessors
            if predecessor not in available_subjects
        )
        case_kind = getattr(entry, "deferred_case_kind", "")
        entries.append(
            FixedPointExpandedAvailablePredecessorCertificateCoverageEntry(
                coverage_entry_id=(
                    "AS-FIXED-POINT-EXPANDED-AVAILABLE-PREDECESSOR-CERTIFICATE-"
                    + case_kind.upper().replace("-", "_")
                ),
                deferred_case_kind=case_kind,
                coverage_status=EXPANDED_COVERAGE_STATUS,
                predecessor_case_kinds=predecessors,
                certificate_covered_predecessor_case_kinds=covered,
                missing_certificate_predecessor_case_kinds=missing,
                open_proof_blocker_case_kinds=tuple(
                    getattr(entry, "open_proof_blocker_case_kinds", ())
                ),
                base_coverage_entry_accepted=bool(getattr(entry, "accepted", False)),
                proof_boundary_preserved=proof_boundary_preserved,
            )
        )
    return entries


def _validate_coverage(
    manifest: FixedPointExpandedAvailablePredecessorCertificateCoverageManifest,
    available_certificates: list[FixedPointExpandedAvailableCertificateSubject],
    proof_boundary_preserved: bool,
    coverage_entries: list[FixedPointExpandedAvailablePredecessorCertificateCoverageEntry],
) -> list[FixedPointExpandedAvailablePredecessorCertificateCoverageValidation]:
    """Validate expanded coverage against manifest expectations."""

    entries_by_kind = {entry.deferred_case_kind: entry for entry in coverage_entries}
    missing_by_kind = {
        entry.deferred_case_kind: entry.missing_certificate_predecessor_case_kinds
        for entry in coverage_entries
    }
    open_counts = {
        entry.deferred_case_kind: entry.open_proof_blocker_count
        for entry in coverage_entries
    }
    return [
        _check(
            "deferred_case_kinds",
            tuple(entries_by_kind) == manifest.expected_deferred_case_kinds,
            "deferred cases match",
        ),
        _check(
            "coverage_entry_count",
            len(coverage_entries) == manifest.expected_deferred_case_count,
            "coverage entry count matches",
        ),
        _check(
            "available_certificate_subjects",
            tuple(certificate.case_kind for certificate in available_certificates)
            == manifest.expected_available_certificate_subjects,
            "available subjects match",
        ),
        _check(
            "total_available_certificate_step_count",
            sum(certificate.certificate_step_count for certificate in available_certificates)
            == manifest.expected_total_available_certificate_step_count,
            "step count matches",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
        ),
        _check(
            "missing_certificate_predecessors",
            missing_by_kind == manifest.expected_missing_certificate_predecessors,
            "missing certificate predecessors match",
            "missing certificate predecessor mismatch",
        ),
        _check(
            "open_proof_blocker_counts",
            open_counts == manifest.expected_open_proof_blocker_counts,
            "open proof blocker counts match",
        ),
        _check(
            "coverage_entries",
            all(entry.accepted for entry in coverage_entries),
            "all coverage entries blocked",
        ),
    ]


def _available_certificate_payload(
    certificate: FixedPointExpandedAvailableCertificateSubject,
) -> dict[str, Any]:
    """Return a JSON-ready available certificate subject."""

    return {
        "case_kind": certificate.case_kind,
        "certificate_set_id": certificate.certificate_set_id,
        "certificate_id": certificate.certificate_id,
        "certificate_step_count": certificate.certificate_step_count,
        "accepted": certificate.certificate_accepted,
    }


def _coverage_entry_payload(
    entry: FixedPointExpandedAvailablePredecessorCertificateCoverageEntry,
) -> dict[str, Any]:
    """Return a JSON-ready expanded coverage entry."""

    return {
        "coverage_entry_id": entry.coverage_entry_id,
        "deferred_case_kind": entry.deferred_case_kind,
        "coverage_status": entry.coverage_status,
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
        "missing_certificate_predecessor_count": (
            entry.missing_certificate_predecessor_count
        ),
        "open_proof_blocker_case_kinds": list(entry.open_proof_blocker_case_kinds),
        "open_proof_blocker_count": entry.open_proof_blocker_count,
        "observed_base_coverage_entry_accepted": entry.base_coverage_entry_accepted,
        "observed_proof_boundary_preserved": entry.proof_boundary_preserved,
        "accepted": entry.accepted,
    }


def _required_text(data: dict[str, Any], key: str) -> str:
    """Return a required non-empty text field."""

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    """Return a required integer field."""

    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    """Return a required list of non-empty text values."""

    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must contain non-empty text")
    return value


def _required_tuple_map(data: dict[str, Any], key: str) -> dict[str, tuple[str, ...]]:
    """Return a required object mapping text keys to text-list tuples."""

    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    result: dict[str, tuple[str, ...]] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"{key} keys must be non-empty text")
        if not isinstance(map_value, list):
            raise ValueError(f"{key}.{map_key} must be a list")
        if not all(isinstance(item, str) and item.strip() for item in map_value):
            raise ValueError(f"{key}.{map_key} must contain non-empty text")
        result[map_key] = tuple(map_value)
    return result


def _required_int_map(data: dict[str, Any], key: str) -> dict[str, int]:
    """Return a required object mapping text keys to integers."""

    value = data.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} must be an object")
    result: dict[str, int] = {}
    for map_key, map_value in value.items():
        if not isinstance(map_key, str) or not map_key.strip():
            raise ValueError(f"{key} keys must be non-empty text")
        if not isinstance(map_value, int):
            raise ValueError(f"{key}.{map_key} must be an integer")
        result[map_key] = map_value
    return result


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointExpandedAvailablePredecessorCertificateCoverageValidation:
    """Return an accepted validation result."""

    return FixedPointExpandedAvailablePredecessorCertificateCoverageValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointExpandedAvailablePredecessorCertificateCoverageValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointExpandedAvailablePredecessorCertificateCoverageValidation(
        subject=subject,
        accepted=condition,
        detail=accepted_detail if condition else rejected_detail or accepted_detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    """Map verbose result subjects to stable failure subjects."""

    if subject == "missing_certificate_predecessors":
        return (
            "fixed-point-expanded-available-predecessor-certificate-coverage-"
            "missing-predecessors"
        )
    if subject == "available_certificate_subjects":
        return (
            "fixed-point-expanded-available-predecessor-certificate-coverage-"
            "subjects"
        )
    if subject == "total_available_certificate_step_count":
        return (
            "fixed-point-expanded-available-predecessor-certificate-coverage-"
            "steps"
        )
    if subject in {
        "base_available_predecessor_certificate_coverage",
        "substitution_representability_certificate",
    }:
        return (
            "fixed-point-expanded-available-predecessor-certificate-coverage-"
            "dependencies"
        )
    if subject.startswith("expected_") or subject in {"coverage_id", "schema_version"}:
        return (
            "fixed-point-expanded-available-predecessor-certificate-coverage-"
            "manifest"
        )
    if subject == "proof_boundary":
        return (
            "fixed-point-expanded-available-predecessor-certificate-coverage-"
            "boundary"
        )
    return (
        "fixed-point-expanded-available-predecessor-certificate-coverage-"
        + subject.replace("_", "-")
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_expanded_available_predecessor_certificate_coverage_cli()


if __name__ == "__main__":
    raise SystemExit(main())
