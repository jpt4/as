"""Available predecessor certificate coverage for deferred fixed-point cases.

ADR-0308 widens the certificate coverage view from selected-root certificates
to all currently available finite predecessor certificates. It makes the
bridge-equality certificate visible to the equation-lifting predecessor while
preserving that certificate support is not proof closure.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_bridge_equality_certificate import (
    load_fixed_point_bridge_equality_certificate,
    validate_fixed_point_bridge_equality_certificate,
)
from autarkic_systems.fixed_point_deferred_case_certificate_readiness import (
    load_fixed_point_deferred_case_certificate_readiness,
    validate_fixed_point_deferred_case_certificate_readiness,
)
from autarkic_systems.fixed_point_selected_root_certificate_coverage import (
    load_fixed_point_selected_root_certificate_coverage,
    validate_fixed_point_selected_root_certificate_coverage,
)


DEFAULT_COVERAGE = Path(
    "claims/fixed_point_available_predecessor_certificate_coverage.json"
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
    "bridge-equality-proof",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "deferred_case_certificate_readiness_path": (
        "claims/fixed_point_deferred_case_certificate_readiness.json"
    ),
    "selected_root_certificate_coverage_path": (
        "claims/fixed_point_selected_root_certificate_coverage.json"
    ),
    "bridge_equality_certificate_path": (
        "claims/fixed_point_bridge_equality_certificate.json"
    ),
}
AVAILABLE_COVERAGE_STATUS = "blocked-available-certificate-coverage-not-proof"


@dataclass(frozen=True)
class FixedPointAvailablePredecessorCertificateCoverageManifest:
    """Loaded manifest for available predecessor certificate coverage."""

    path: Path
    schema_version: int
    coverage_id: str
    reviewed_at: str
    purpose: str
    deferred_case_certificate_readiness_path: str
    selected_root_certificate_coverage_path: str
    bridge_equality_certificate_path: str
    expected_deferred_case_count: int
    expected_deferred_case_kinds: tuple[str, ...]
    expected_available_certificate_subjects: tuple[str, ...]
    expected_total_available_certificate_step_count: int
    expected_missing_certificate_predecessors: dict[str, tuple[str, ...]]
    expected_open_proof_blocker_counts: dict[str, int]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointAvailableCertificateSubject:
    """One available finite predecessor certificate subject."""

    case_kind: str
    certificate_set_id: str
    certificate_id: str
    certificate_step_count: int
    certificate_accepted: bool


@dataclass(frozen=True)
class FixedPointAvailablePredecessorCertificateCoverageEntry:
    """Available certificate coverage for one deferred construction case."""

    coverage_entry_id: str
    deferred_case_kind: str
    coverage_status: str
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
        """Return whether this available coverage entry accepted."""

        return (
            self.coverage_status == AVAILABLE_COVERAGE_STATUS
            and self.readiness_entry_accepted
            and self.proof_boundary_preserved
        )


@dataclass(frozen=True)
class FixedPointAvailablePredecessorCertificateCoverageValidation:
    """One validation result for available predecessor coverage."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointAvailablePredecessorCertificateCoverageReport:
    """Validation report for available predecessor certificate coverage."""

    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest
    deferred_case_certificate_readiness_path: Path
    selected_root_certificate_coverage_path: Path
    bridge_equality_certificate_path: Path
    willard_map_path: Path
    readiness_accepted: bool
    selected_root_coverage_accepted: bool
    bridge_equality_certificate_accepted: bool
    proof_boundary_preserved: bool
    available_certificates: tuple[FixedPointAvailableCertificateSubject, ...]
    coverage_entries: tuple[
        FixedPointAvailablePredecessorCertificateCoverageEntry, ...
    ]
    results: tuple[FixedPointAvailablePredecessorCertificateCoverageValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every coverage validation passed."""

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
    readiness_entries: tuple[Any, ...] = ()
    coverage_entries: tuple[Any, ...] = ()
    certificates: tuple[Any, ...] = ()
    proof_boundary_preserved: bool = False
    manifest: Any | None = None


def load_fixed_point_available_predecessor_certificate_coverage(
    path: Path | str = DEFAULT_COVERAGE,
) -> FixedPointAvailablePredecessorCertificateCoverageManifest:
    """Load the available predecessor certificate coverage manifest."""

    coverage_path = Path(path)
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    return FixedPointAvailablePredecessorCertificateCoverageManifest(
        path=coverage_path,
        schema_version=_required_int(data, "schema_version"),
        coverage_id=_required_text(data, "coverage_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        deferred_case_certificate_readiness_path=_required_text(
            data,
            "deferred_case_certificate_readiness_path",
        ),
        selected_root_certificate_coverage_path=_required_text(
            data,
            "selected_root_certificate_coverage_path",
        ),
        bridge_equality_certificate_path=_required_text(
            data,
            "bridge_equality_certificate_path",
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


def validate_fixed_point_available_predecessor_certificate_coverage(
    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointAvailablePredecessorCertificateCoverageReport:
    """Validate available predecessor certificate coverage."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointAvailablePredecessorCertificateCoverageValidation] = [
        _accepted("manifest", f"loaded {manifest.coverage_id}")
    ]
    results.extend(_validate_manifest(manifest))

    readiness_report = _load_readiness(
        paths["deferred_case_certificate_readiness_path"],
        checked_willard_map_path,
    )
    selected_root_report = _load_selected_root_coverage(
        paths["selected_root_certificate_coverage_path"],
        checked_willard_map_path,
    )
    bridge_certificate_report = _load_bridge_certificate(
        paths["bridge_equality_certificate_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            readiness_report,
            selected_root_report,
            bridge_certificate_report,
        )
    )

    available_certificates = _derive_available_certificates(
        selected_root_report,
        bridge_certificate_report,
    )
    proof_boundary_preserved = _proof_boundary_preserved(
        manifest,
        readiness_report,
        selected_root_report,
        bridge_certificate_report,
    )
    coverage_entries = _derive_coverage_entries(
        readiness_report,
        available_certificates,
        proof_boundary_preserved,
    )
    results.extend(
        _validate_coverage(
            manifest,
            readiness_report,
            available_certificates,
            proof_boundary_preserved,
            coverage_entries,
        )
    )

    return FixedPointAvailablePredecessorCertificateCoverageReport(
        manifest=manifest,
        deferred_case_certificate_readiness_path=paths[
            "deferred_case_certificate_readiness_path"
        ],
        selected_root_certificate_coverage_path=paths[
            "selected_root_certificate_coverage_path"
        ],
        bridge_equality_certificate_path=paths["bridge_equality_certificate_path"],
        willard_map_path=checked_willard_map_path,
        readiness_accepted=readiness_report.accepted,
        selected_root_coverage_accepted=selected_root_report.accepted,
        bridge_equality_certificate_accepted=bridge_certificate_report.accepted,
        proof_boundary_preserved=proof_boundary_preserved,
        available_certificates=tuple(available_certificates),
        coverage_entries=tuple(coverage_entries),
        results=tuple(results),
    )


def fixed_point_available_predecessor_certificate_coverage_payload(
    report: FixedPointAvailablePredecessorCertificateCoverageReport,
) -> dict[str, Any]:
    """Return a JSON-ready available predecessor coverage payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "coverage_manifest": str(report.manifest.path),
        "coverage_id": report.manifest.coverage_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "deferred_case_certificate_readiness_path": str(
            report.deferred_case_certificate_readiness_path
        ),
        "selected_root_certificate_coverage_path": str(
            report.selected_root_certificate_coverage_path
        ),
        "bridge_equality_certificate_path": str(
            report.bridge_equality_certificate_path
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
        "observed_readiness_accepted": report.readiness_accepted,
        "observed_selected_root_coverage_accepted": (
            report.selected_root_coverage_accepted
        ),
        "observed_bridge_equality_certificate_accepted": (
            report.bridge_equality_certificate_accepted
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


def format_fixed_point_available_predecessor_certificate_coverage_report(
    report: FixedPointAvailablePredecessorCertificateCoverageReport,
) -> str:
    """Format a concise available predecessor certificate coverage report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point available predecessor certificate coverage: {status}",
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


def run_fixed_point_available_predecessor_certificate_coverage_cli(
    argv: list[str] | None = None,
) -> int:
    """Run available predecessor certificate coverage validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_available_predecessor_certificate_coverage"
        ),
        description=(
            "Validate available finite predecessor certificate coverage for "
            "deferred AS fixed-point construction cases."
        ),
    )
    parser.add_argument(
        "--coverage",
        default=str(DEFAULT_COVERAGE),
        help="Path to the available predecessor certificate coverage manifest.",
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

    manifest = load_fixed_point_available_predecessor_certificate_coverage(
        args.coverage
    )
    report = validate_fixed_point_available_predecessor_certificate_coverage(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_available_predecessor_certificate_coverage_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_available_predecessor_certificate_coverage_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest,
) -> dict[str, Path]:
    return {
        "deferred_case_certificate_readiness_path": Path(
            manifest.deferred_case_certificate_readiness_path
        ),
        "selected_root_certificate_coverage_path": Path(
            manifest.selected_root_certificate_coverage_path
        ),
        "bridge_equality_certificate_path": Path(
            manifest.bridge_equality_certificate_path
        ),
    }


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


def _load_selected_root_coverage(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_selected_root_certificate_coverage(path)
        return validate_fixed_point_selected_root_certificate_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-selected-root-certificate-coverage-load",),
        )


def _load_bridge_certificate(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_bridge_equality_certificate(path)
        return validate_fixed_point_bridge_equality_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-bridge-equality-certificate-load",),
        )


def _validate_manifest(
    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest,
) -> list[FixedPointAvailablePredecessorCertificateCoverageValidation]:
    results: list[FixedPointAvailablePredecessorCertificateCoverageValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.coverage_id == "as-fixed-point-available-predecessor-certificate-coverage-v1":
        results.append(_accepted("coverage_id", "coverage id matches"))
    else:
        results.append(_rejected("coverage_id", "unexpected coverage id"))

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.expected_deferred_case_count == 3:
        results.append(_accepted("expected_deferred_case_count", "three cases"))
    else:
        results.append(
            _rejected("expected_deferred_case_count", "expected three cases")
        )

    if manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS:
        results.append(_accepted("expected_deferred_case_kinds", "deferred cases match"))
    else:
        results.append(
            _rejected("expected_deferred_case_kinds", "deferred case mismatch")
        )

    if (
        manifest.expected_available_certificate_subjects
        == REQUIRED_AVAILABLE_CERTIFICATE_SUBJECTS
    ):
        results.append(
            _accepted(
                "expected_available_certificate_subjects",
                "available certificate subjects match",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_available_certificate_subjects",
                "available certificate subject mismatch",
            )
        )

    if manifest.expected_total_available_certificate_step_count == 20:
        results.append(
            _accepted(
                "expected_total_available_certificate_step_count",
                "twenty steps",
            )
        )
    else:
        results.append(
            _rejected(
                "expected_total_available_certificate_step_count",
                "expected twenty certificate steps",
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
) -> list[FixedPointAvailablePredecessorCertificateCoverageValidation]:
    missing = [case_kind for case_kind in REQUIRED_DEFERRED_CASE_KINDS if case_kind not in values]
    if missing:
        return [_rejected(subject, "missing cases: " + ", ".join(missing))]
    return [_accepted(subject, "all cases covered")]


def _validate_dependencies(
    readiness_report: Any,
    selected_root_report: Any,
    bridge_certificate_report: Any,
) -> list[FixedPointAvailablePredecessorCertificateCoverageValidation]:
    checks = (
        ("deferred_case_certificate_readiness", readiness_report, "readiness"),
        (
            "selected_root_certificate_coverage",
            selected_root_report,
            "selected-root certificate coverage",
        ),
        (
            "bridge_equality_certificate",
            bridge_certificate_report,
            "bridge-equality certificate",
        ),
    )
    results: list[FixedPointAvailablePredecessorCertificateCoverageValidation] = []
    for subject, report, label in checks:
        if report.accepted:
            results.append(_accepted(subject, f"{label} accepted"))
        else:
            results.append(
                _rejected(
                    subject,
                    f"{label} rejected: " + _joined_or_none(report.failed_subjects),
                )
            )
    return results


def _derive_available_certificates(
    selected_root_report: Any,
    bridge_certificate_report: Any,
) -> list[FixedPointAvailableCertificateSubject]:
    certificates: list[FixedPointAvailableCertificateSubject] = []
    if selected_root_report.accepted:
        for entry in selected_root_report.coverage_entries:
            if not entry.accepted:
                continue
            certificates.append(
                FixedPointAvailableCertificateSubject(
                    case_kind=entry.selected_case_kind,
                    certificate_set_id=entry.certificate_set_id,
                    certificate_id=entry.certificate_id,
                    certificate_step_count=entry.certificate_step_count,
                    certificate_accepted=entry.accepted,
                )
            )
    if bridge_certificate_report.accepted and bridge_certificate_report.certificates:
        certificate = bridge_certificate_report.certificates[0]
        certificates.append(
            FixedPointAvailableCertificateSubject(
                case_kind="bridge-equality-proof",
                certificate_set_id=bridge_certificate_report.manifest.certificate_set_id,
                certificate_id=certificate.certificate_id,
                certificate_step_count=len(certificate.steps),
                certificate_accepted=certificate.accepted,
            )
        )
    return certificates


def _derive_coverage_entries(
    readiness_report: Any,
    available_certificates: list[FixedPointAvailableCertificateSubject],
    proof_boundary_preserved: bool,
) -> list[FixedPointAvailablePredecessorCertificateCoverageEntry]:
    if not readiness_report.accepted:
        return []
    covered_subjects = {
        certificate.case_kind
        for certificate in available_certificates
        if certificate.certificate_accepted
    }
    entries: list[FixedPointAvailablePredecessorCertificateCoverageEntry] = []
    for readiness in readiness_report.readiness_entries:
        covered_predecessors = tuple(
            predecessor
            for predecessor in readiness.predecessor_case_kinds
            if predecessor in covered_subjects
        )
        missing_predecessors = tuple(
            predecessor
            for predecessor in readiness.predecessor_case_kinds
            if predecessor not in covered_subjects
        )
        entries.append(
            FixedPointAvailablePredecessorCertificateCoverageEntry(
                coverage_entry_id=(
                    "AS-FIXED-POINT-AVAILABLE-PREDECESSOR-CERTIFICATE-"
                    + readiness.deferred_case_kind.upper().replace("-", "_")
                ),
                deferred_case_kind=readiness.deferred_case_kind,
                coverage_status=AVAILABLE_COVERAGE_STATUS,
                predecessor_case_kinds=readiness.predecessor_case_kinds,
                certificate_covered_predecessor_case_kinds=covered_predecessors,
                missing_certificate_predecessor_case_kinds=missing_predecessors,
                open_proof_blocker_case_kinds=(
                    readiness.blocking_open_predecessor_case_kinds
                ),
                readiness_entry_accepted=readiness.accepted,
                proof_boundary_preserved=proof_boundary_preserved,
            )
        )
    return entries


def _proof_boundary_preserved(
    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest,
    readiness_report: Any,
    selected_root_report: Any,
    bridge_certificate_report: Any,
) -> bool:
    readiness_open = all(
        bool(entry.blocking_open_predecessor_case_kinds)
        for entry in readiness_report.readiness_entries
    )
    bridge_non_claims = set(getattr(bridge_certificate_report.manifest, "non_claims", ()))
    selected_non_claims = set(getattr(selected_root_report.manifest, "non_claims", ()))
    return (
        readiness_report.accepted
        and selected_root_report.accepted
        and bridge_certificate_report.accepted
        and readiness_open
        and set(REQUIRED_NON_CLAIMS).issubset(set(manifest.non_claims))
        and "no bridge equality proof" in bridge_non_claims
        and "no fixed-point equation proof" in bridge_non_claims
        and "no self-consistency theorem" in selected_non_claims
    )


def _validate_coverage(
    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest,
    readiness_report: Any,
    available_certificates: list[FixedPointAvailableCertificateSubject],
    proof_boundary_preserved: bool,
    coverage_entries: list[FixedPointAvailablePredecessorCertificateCoverageEntry],
) -> list[FixedPointAvailablePredecessorCertificateCoverageValidation]:
    results: list[FixedPointAvailablePredecessorCertificateCoverageValidation] = []
    deferred_case_kinds = tuple(entry.deferred_case_kind for entry in coverage_entries)
    if deferred_case_kinds == manifest.expected_deferred_case_kinds:
        results.append(_accepted("deferred_case_kinds", "deferred cases match"))
    else:
        results.append(_rejected("deferred_case_kinds", "deferred case mismatch"))

    if len(coverage_entries) == manifest.expected_deferred_case_count:
        results.append(_accepted("coverage_entry_count", "coverage entry count matches"))
    else:
        results.append(
            _rejected(
                "coverage_entry_count",
                "coverage entry count mismatch: expected "
                f"{manifest.expected_deferred_case_count} but found "
                f"{len(coverage_entries)}",
            )
        )

    subjects = tuple(certificate.case_kind for certificate in available_certificates)
    if subjects == manifest.expected_available_certificate_subjects:
        results.append(
            _accepted("available_certificate_subjects", "available subjects match")
        )
    else:
        results.append(
            _rejected(
                "available_certificate_subjects",
                "available subject mismatch",
            )
        )

    step_count = sum(
        certificate.certificate_step_count for certificate in available_certificates
    )
    if step_count == manifest.expected_total_available_certificate_step_count:
        results.append(_accepted("total_available_certificate_step_count", "step count matches"))
    else:
        results.append(
            _rejected(
                "total_available_certificate_step_count",
                "step count mismatch: expected "
                f"{manifest.expected_total_available_certificate_step_count} "
                f"but found {step_count}",
            )
        )

    if proof_boundary_preserved:
        results.append(_accepted("proof_boundary", "proof boundary preserved"))
    else:
        results.append(_rejected("proof_boundary", "proof boundary not preserved"))

    results.extend(_validate_entry_expectations(manifest, coverage_entries))

    rejected_entries = [
        entry.deferred_case_kind for entry in coverage_entries if not entry.accepted
    ]
    if rejected_entries:
        results.append(
            _rejected(
                "coverage_entries",
                "rejected entries: " + ", ".join(rejected_entries),
            )
        )
    else:
        results.append(_accepted("coverage_entries", "all coverage entries blocked"))
    return results


def _validate_entry_expectations(
    manifest: FixedPointAvailablePredecessorCertificateCoverageManifest,
    coverage_entries: list[FixedPointAvailablePredecessorCertificateCoverageEntry],
) -> list[FixedPointAvailablePredecessorCertificateCoverageValidation]:
    missing_mismatches: list[str] = []
    blocker_mismatches: list[str] = []
    for entry in coverage_entries:
        expected_missing = manifest.expected_missing_certificate_predecessors.get(
            entry.deferred_case_kind
        )
        expected_blockers = manifest.expected_open_proof_blocker_counts.get(
            entry.deferred_case_kind
        )
        if expected_missing != entry.missing_certificate_predecessor_case_kinds:
            missing_mismatches.append(
                f"{entry.deferred_case_kind} expected "
                f"{_joined_or_none(expected_missing or ())} found "
                f"{_joined_or_none(entry.missing_certificate_predecessor_case_kinds)}"
            )
        if expected_blockers != entry.open_proof_blocker_count:
            blocker_mismatches.append(
                f"{entry.deferred_case_kind} expected {expected_blockers} "
                f"found {entry.open_proof_blocker_count}"
            )

    results: list[FixedPointAvailablePredecessorCertificateCoverageValidation] = []
    if missing_mismatches:
        results.append(
            _rejected(
                "missing_certificate_predecessors",
                "missing certificate predecessor mismatch: "
                + "; ".join(missing_mismatches),
            )
        )
    else:
        results.append(
            _accepted(
                "missing_certificate_predecessors",
                "missing certificate predecessors match",
            )
        )

    if blocker_mismatches:
        results.append(
            _rejected(
                "open_proof_blocker_counts",
                "open proof blocker count mismatch: "
                + "; ".join(blocker_mismatches),
            )
        )
    else:
        results.append(
            _accepted("open_proof_blocker_counts", "open proof blocker counts match")
        )
    return results


def _available_certificate_payload(
    certificate: FixedPointAvailableCertificateSubject,
) -> dict[str, Any]:
    return {
        "case_kind": certificate.case_kind,
        "certificate_set_id": certificate.certificate_set_id,
        "certificate_id": certificate.certificate_id,
        "certificate_step_count": certificate.certificate_step_count,
        "accepted": certificate.certificate_accepted,
    }


def _coverage_entry_payload(
    entry: FixedPointAvailablePredecessorCertificateCoverageEntry,
) -> dict[str, Any]:
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
        "observed_readiness_entry_accepted": entry.readiness_entry_accepted,
        "observed_proof_boundary_preserved": entry.proof_boundary_preserved,
        "accepted": entry.accepted,
    }


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointAvailablePredecessorCertificateCoverageValidation:
    return FixedPointAvailablePredecessorCertificateCoverageValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointAvailablePredecessorCertificateCoverageValidation:
    return FixedPointAvailablePredecessorCertificateCoverageValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_deferred_case_kinds", "deferred_case_kinds"}:
        return "fixed-point-available-predecessor-certificate-coverage-deferred-cases"
    if subject in {"expected_deferred_case_count", "coverage_entry_count"}:
        return "fixed-point-available-predecessor-certificate-coverage-count"
    if subject in {
        "expected_available_certificate_subjects",
        "available_certificate_subjects",
    }:
        return "fixed-point-available-predecessor-certificate-coverage-subjects"
    if subject in {
        "expected_total_available_certificate_step_count",
        "total_available_certificate_step_count",
    }:
        return "fixed-point-available-predecessor-certificate-coverage-step-count"
    if subject in {
        "expected_missing_certificate_predecessors",
        "missing_certificate_predecessors",
    }:
        return "fixed-point-available-predecessor-certificate-coverage-missing-predecessors"
    if subject in {
        "expected_open_proof_blocker_counts",
        "open_proof_blocker_counts",
    }:
        return "fixed-point-available-predecessor-certificate-coverage-proof-blockers"
    if subject == "non_claims":
        return "fixed-point-available-predecessor-certificate-coverage-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-available-predecessor-certificate-coverage-boundary"
    if subject == "coverage_entries":
        return "fixed-point-available-predecessor-certificate-coverage-entry"
    if subject.endswith("_path"):
        return "fixed-point-available-predecessor-certificate-coverage-path"
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
    raise SystemExit(run_fixed_point_available_predecessor_certificate_coverage_cli())
