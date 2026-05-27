"""Proof-readiness handoff for the diagonal-instance-closure root case.

ADR-0312 composes the compact diagonal-instance-closure frontier status with
the finite certificate support for the selected root obligation. The resulting
surface is intentionally modest: it records that the case is certificate-ready
while preserving that the construction case itself remains proof-open. This is
not a diagonal-instance closure proof, substitution proof, bridge-equality
proof, fixed-point equation proof, arithmetized proof predicate, or
self-consistency theorem.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_diagonal_instance_closure_certificate import (
    load_fixed_point_diagonal_instance_closure_certificate,
    validate_fixed_point_diagonal_instance_closure_certificate,
)
from autarkic_systems.fixed_point_diagonal_instance_closure_frontier_status import (
    load_fixed_point_diagonal_instance_closure_frontier_status,
    validate_fixed_point_diagonal_instance_closure_frontier_status,
)


DEFAULT_READINESS = Path(
    "claims/fixed_point_diagonal_instance_closure_proof_readiness.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_READINESS_ID = (
    "as-fixed-point-diagonal-instance-closure-proof-readiness-v1"
)
REQUIRED_CASE_ID = "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE"
REQUIRED_CASE_KIND = "diagonal-instance-closure"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_CONSTRUCTION_CASE_STATUS = "proof-case-open"
REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "diagonal-instance-closure"
REQUIRED_SUPPORT_SURFACE_COUNT = 5
REQUIRED_CERTIFICATE_COUNT = 1
REQUIRED_CERTIFICATE_STEP_COUNT = 7
REQUIRED_DIAGONAL_INSTANCE_CODE_LENGTH = 296
REQUIRED_NON_CLAIMS = (
    "no diagonal-instance closure proof",
    "no substitution representability proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "diagonal_instance_closure_frontier_status_path": (
        "claims/fixed_point_diagonal_instance_closure_frontier_status.json"
    ),
    "diagonal_instance_closure_certificate_path": (
        "claims/fixed_point_diagonal_instance_closure_certificate.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "diagonal-instance closure proof",
    "substitution representability proof",
    "substitution graph correctness proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureProofReadinessManifest:
    """Loaded manifest for the root proof-readiness handoff."""

    path: Path
    schema_version: int
    readiness_id: str
    reviewed_at: str
    purpose: str
    diagonal_instance_closure_frontier_status_path: str
    diagonal_instance_closure_certificate_path: str
    expected_readiness_case_id: str
    expected_readiness_case_kind: str
    expected_readiness_status: str
    expected_construction_case_status: str
    expected_frontier_status: str
    expected_frontier_blocker: str
    expected_support_surface_count: int
    expected_certificate_count: int
    expected_certificate_step_count: int
    expected_diagonal_instance_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureProofReadinessEntry:
    """Derived readiness state for the diagonal-instance-closure root."""

    case_id: str
    case_kind: str
    construction_case_status: str
    readiness_status: str
    certificate_ready: bool
    open_proof_blocker: str

    @property
    def accepted(self) -> bool:
        """Return whether this entry is certificate-ready and proof-open."""

        return (
            self.case_id == REQUIRED_CASE_ID
            and self.case_kind == REQUIRED_CASE_KIND
            and self.construction_case_status == REQUIRED_CONSTRUCTION_CASE_STATUS
            and self.readiness_status == REQUIRED_READINESS_STATUS
            and self.certificate_ready
            and self.open_proof_blocker == REQUIRED_FRONTIER_BLOCKER
        )


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureProofReadinessValidation:
    """One validation result for the proof-readiness handoff."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureProofReadinessReport:
    """Validation report for diagonal-instance-closure proof readiness."""

    manifest: FixedPointDiagonalInstanceClosureProofReadinessManifest
    diagonal_instance_closure_frontier_status_path: Path
    diagonal_instance_closure_certificate_path: Path
    willard_map_path: Path
    frontier_accepted: bool
    certificate_accepted: bool
    frontier_status: str
    frontier_blocker: str
    support_surface_count: int
    certificate_count: int
    certificate_step_count: int
    diagonal_instance_code_length: int
    proof_boundary_preserved: bool
    readiness_entry: FixedPointDiagonalInstanceClosureProofReadinessEntry
    results: tuple[FixedPointDiagonalInstanceClosureProofReadinessValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every readiness validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def failed_subjects(self) -> tuple[str, ...]:
        """Return stable failure subjects for automation and reports."""

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
    frontier_status: str = ""
    frontier_blocked_by: str = ""
    support_surface_count: int = 0
    certificate_count: int = 0
    certificate_step_count: int = 0
    support_facts: dict[str, dict[str, Any]] | None = None
    certificates: tuple[Any, ...] = ()
    construction_case: Any | None = None


def load_fixed_point_diagonal_instance_closure_proof_readiness(
    path: Path | str = DEFAULT_READINESS,
) -> FixedPointDiagonalInstanceClosureProofReadinessManifest:
    """Load the diagonal-instance-closure proof-readiness manifest."""

    readiness_path = Path(path)
    data = json.loads(readiness_path.read_text(encoding="utf-8"))
    return FixedPointDiagonalInstanceClosureProofReadinessManifest(
        path=readiness_path,
        schema_version=_required_int(data, "schema_version"),
        readiness_id=_required_text(data, "readiness_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        diagonal_instance_closure_frontier_status_path=_required_text(
            data,
            "diagonal_instance_closure_frontier_status_path",
        ),
        diagonal_instance_closure_certificate_path=_required_text(
            data,
            "diagonal_instance_closure_certificate_path",
        ),
        expected_readiness_case_id=_required_text(
            data,
            "expected_readiness_case_id",
        ),
        expected_readiness_case_kind=_required_text(
            data,
            "expected_readiness_case_kind",
        ),
        expected_readiness_status=_required_text(
            data,
            "expected_readiness_status",
        ),
        expected_construction_case_status=_required_text(
            data,
            "expected_construction_case_status",
        ),
        expected_frontier_status=_required_text(data, "expected_frontier_status"),
        expected_frontier_blocker=_required_text(data, "expected_frontier_blocker"),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_certificate_count=_required_int(
            data,
            "expected_certificate_count",
        ),
        expected_certificate_step_count=_required_int(
            data,
            "expected_certificate_step_count",
        ),
        expected_diagonal_instance_code_length=_required_int(
            data,
            "expected_diagonal_instance_code_length",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_diagonal_instance_closure_proof_readiness(
    manifest: FixedPointDiagonalInstanceClosureProofReadinessManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDiagonalInstanceClosureProofReadinessReport:
    """Validate certificate-ready/proof-open readiness for the root case."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointDiagonalInstanceClosureProofReadinessValidation] = [
        _accepted("manifest", f"loaded {manifest.readiness_id}")
    ]
    results.extend(_validate_manifest(manifest))

    frontier_report = _load_frontier(
        paths["diagonal_instance_closure_frontier_status_path"],
        checked_willard_map_path,
    )
    certificate_report = _load_certificate(
        paths["diagonal_instance_closure_certificate_path"],
        checked_willard_map_path,
    )
    results.extend(_validate_dependencies(frontier_report, certificate_report))

    diagonal_instance_code_length = _diagonal_instance_code_length(frontier_report)
    readiness_entry = _derive_readiness_entry(
        manifest,
        frontier_report,
        certificate_report,
    )
    proof_boundary_preserved = (
        bool(getattr(frontier_report, "accepted", False))
        and bool(getattr(certificate_report, "accepted", False))
        and readiness_entry.construction_case_status
        == REQUIRED_CONSTRUCTION_CASE_STATUS
        and readiness_entry.open_proof_blocker == REQUIRED_FRONTIER_BLOCKER
    )
    results.extend(
        _validate_readiness(
            manifest,
            frontier_report,
            certificate_report,
            readiness_entry,
            diagonal_instance_code_length,
            proof_boundary_preserved,
        )
    )

    return FixedPointDiagonalInstanceClosureProofReadinessReport(
        manifest=manifest,
        diagonal_instance_closure_frontier_status_path=paths[
            "diagonal_instance_closure_frontier_status_path"
        ],
        diagonal_instance_closure_certificate_path=paths[
            "diagonal_instance_closure_certificate_path"
        ],
        willard_map_path=checked_willard_map_path,
        frontier_accepted=bool(getattr(frontier_report, "accepted", False)),
        certificate_accepted=bool(getattr(certificate_report, "accepted", False)),
        frontier_status=str(getattr(frontier_report, "frontier_status", "")),
        frontier_blocker=str(getattr(frontier_report, "frontier_blocked_by", "")),
        support_surface_count=int(getattr(frontier_report, "support_surface_count", 0)),
        certificate_count=int(getattr(certificate_report, "certificate_count", 0)),
        certificate_step_count=int(
            getattr(certificate_report, "certificate_step_count", 0)
        ),
        diagonal_instance_code_length=diagonal_instance_code_length,
        proof_boundary_preserved=proof_boundary_preserved,
        readiness_entry=readiness_entry,
        results=tuple(results),
    )


def fixed_point_diagonal_instance_closure_proof_readiness_payload(
    report: FixedPointDiagonalInstanceClosureProofReadinessReport,
) -> dict[str, Any]:
    """Return a JSON-ready proof-readiness payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "readiness_manifest": str(report.manifest.path),
        "readiness_id": report.manifest.readiness_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "diagonal_instance_closure_frontier_status_path": str(
            report.diagonal_instance_closure_frontier_status_path
        ),
        "diagonal_instance_closure_certificate_path": str(
            report.diagonal_instance_closure_certificate_path
        ),
        "willard_map": str(report.willard_map_path),
        "observed_frontier_accepted": report.frontier_accepted,
        "observed_certificate_accepted": report.certificate_accepted,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "frontier_status": report.frontier_status,
        "frontier_blocker": report.frontier_blocker,
        "support_surface_count": report.support_surface_count,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "diagonal_instance_code_length": report.diagonal_instance_code_length,
        "readiness_entry": _readiness_entry_payload(report.readiness_entry),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
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


def format_fixed_point_diagonal_instance_closure_proof_readiness_report(
    report: FixedPointDiagonalInstanceClosureProofReadinessReport,
) -> str:
    """Format a concise text report for the proof-readiness handoff."""

    status = "accepted" if report.accepted else "rejected"
    entry = report.readiness_entry
    lines = [
        f"Fixed-point diagonal instance closure proof readiness: {status}",
        f"Readiness: {report.manifest.readiness_id}",
        f"Construction case: {entry.case_id}",
        f"Case kind: {entry.case_kind}",
        f"Readiness status: {entry.readiness_status}",
        f"Frontier: {report.frontier_status} by {report.frontier_blocker}",
        f"Construction case status: {entry.construction_case_status}",
        f"Certificate ready: {str(entry.certificate_ready).lower()}",
        f"Certificate steps: {report.certificate_step_count}",
        f"Diagonal instance code length: {report.diagonal_instance_code_length}",
        "Proof boundary preserved: "
        + str(report.proof_boundary_preserved).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_diagonal_instance_closure_proof_readiness_cli(
    argv: list[str] | None = None,
) -> int:
    """Run diagonal-instance-closure proof-readiness validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_diagonal_instance_closure_proof_readiness"
        ),
        description=(
            "Validate certificate-ready/proof-open readiness for the AS "
            "fixed-point diagonal-instance-closure root case."
        ),
    )
    parser.add_argument(
        "--readiness",
        default=str(DEFAULT_READINESS),
        help="Path to the diagonal-instance-closure proof-readiness manifest.",
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

    manifest = load_fixed_point_diagonal_instance_closure_proof_readiness(
        args.readiness
    )
    report = validate_fixed_point_diagonal_instance_closure_proof_readiness(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_diagonal_instance_closure_proof_readiness_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_diagonal_instance_closure_proof_readiness_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointDiagonalInstanceClosureProofReadinessManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "diagonal_instance_closure_frontier_status_path": _resolve_path(
            manifest.path,
            manifest.diagonal_instance_closure_frontier_status_path,
        ),
        "diagonal_instance_closure_certificate_path": _resolve_path(
            manifest.path,
            manifest.diagonal_instance_closure_certificate_path,
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


def _load_frontier(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the diagonal-instance-closure frontier status."""

    try:
        manifest = load_fixed_point_diagonal_instance_closure_frontier_status(path)
        return validate_fixed_point_diagonal_instance_closure_frontier_status(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-diagonal-instance-closure-frontier-status-load",
            ),
            support_facts={},
        )


def _load_certificate(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the diagonal-instance-closure certificate support."""

    try:
        manifest = load_fixed_point_diagonal_instance_closure_certificate(path)
        return validate_fixed_point_diagonal_instance_closure_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-diagonal-instance-closure-certificate-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointDiagonalInstanceClosureProofReadinessManifest,
) -> list[FixedPointDiagonalInstanceClosureProofReadinessValidation]:
    """Validate manifest-local constants and proof-boundary guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "readiness_id",
            manifest.readiness_id == REQUIRED_READINESS_ID,
            "readiness id matches",
            "unexpected readiness id",
        ),
        *[
            _check(
                key,
                getattr(manifest, key) == expected,
                f"{expected} referenced",
                f"expected {expected} but found {getattr(manifest, key)}",
            )
            for key, expected in EXPECTED_DEPENDENCY_PATHS.items()
        ],
        _check(
            "expected_readiness_case_id",
            manifest.expected_readiness_case_id == REQUIRED_CASE_ID,
            "case id matches",
        ),
        _check(
            "expected_readiness_case_kind",
            manifest.expected_readiness_case_kind == REQUIRED_CASE_KIND,
            "case kind matches",
        ),
        _check(
            "expected_readiness_status",
            manifest.expected_readiness_status == REQUIRED_READINESS_STATUS,
            "readiness status matches",
        ),
        _check(
            "expected_construction_case_status",
            (
                manifest.expected_construction_case_status
                == REQUIRED_CONSTRUCTION_CASE_STATUS
            ),
            "construction case status matches",
        ),
        _check(
            "expected_frontier_status",
            manifest.expected_frontier_status == REQUIRED_FRONTIER_STATUS,
            "frontier status matches",
        ),
        _check(
            "expected_frontier_blocker",
            manifest.expected_frontier_blocker == REQUIRED_FRONTIER_BLOCKER,
            "frontier blocker matches",
        ),
        _check(
            "expected_support_surface_count",
            manifest.expected_support_surface_count == REQUIRED_SUPPORT_SURFACE_COUNT,
            "support surface count matches",
        ),
        _check(
            "expected_certificate_count",
            manifest.expected_certificate_count == REQUIRED_CERTIFICATE_COUNT,
            "certificate count matches",
        ),
        _check(
            "expected_certificate_step_count",
            manifest.expected_certificate_step_count == REQUIRED_CERTIFICATE_STEP_COUNT,
            "certificate step count matches",
        ),
        _check(
            "expected_diagonal_instance_code_length",
            (
                manifest.expected_diagonal_instance_code_length
                == REQUIRED_DIAGONAL_INSTANCE_CODE_LENGTH
            ),
            "diagonal instance code length matches",
        ),
        _check(
            "non_claims",
            manifest.non_claims == REQUIRED_NON_CLAIMS,
            "all non-claims preserved",
            "missing non-claims",
        ),
        _check(
            "non_claim_promotion_boundary",
            _non_claims_are_guarded(manifest.non_claims),
            "non-claims use explicit no-prefix boundary",
            "proof promotion non-claim boundary",
        ),
    ]


def _validate_dependencies(
    frontier_report: Any,
    certificate_report: Any,
) -> list[FixedPointDiagonalInstanceClosureProofReadinessValidation]:
    """Validate that dependency reports accepted before readiness derivation."""

    return [
        _check(
            "diagonal_instance_closure_frontier_status",
            bool(getattr(frontier_report, "accepted", False)),
            "frontier status accepted",
            "frontier status rejected: "
            + _joined_or_none(getattr(frontier_report, "failed_subjects", ())),
        ),
        _check(
            "diagonal_instance_closure_certificate",
            bool(getattr(certificate_report, "accepted", False)),
            "certificate accepted",
            "certificate rejected: "
            + _joined_or_none(getattr(certificate_report, "failed_subjects", ())),
        ),
    ]


def _derive_readiness_entry(
    manifest: FixedPointDiagonalInstanceClosureProofReadinessManifest,
    frontier_report: Any,
    certificate_report: Any,
) -> FixedPointDiagonalInstanceClosureProofReadinessEntry:
    """Derive the root readiness entry from the accepted dependency reports."""

    construction_case = getattr(frontier_report, "construction_case", None)
    certificates = tuple(getattr(certificate_report, "certificates", ()))
    certificate_ready = (
        bool(getattr(certificate_report, "accepted", False))
        and bool(certificates)
        and all(
            bool(getattr(certificate, "accepted", False))
            for certificate in certificates
        )
    )
    return FixedPointDiagonalInstanceClosureProofReadinessEntry(
        case_id=str(getattr(construction_case, "case_id", "")),
        case_kind=str(getattr(construction_case, "case_kind", "")),
        construction_case_status=str(getattr(construction_case, "status", "")),
        readiness_status=manifest.expected_readiness_status,
        certificate_ready=certificate_ready,
        open_proof_blocker=str(getattr(frontier_report, "frontier_blocked_by", "")),
    )


def _validate_readiness(
    manifest: FixedPointDiagonalInstanceClosureProofReadinessManifest,
    frontier_report: Any,
    certificate_report: Any,
    entry: FixedPointDiagonalInstanceClosureProofReadinessEntry,
    diagonal_instance_code_length: int,
    proof_boundary_preserved: bool,
) -> list[FixedPointDiagonalInstanceClosureProofReadinessValidation]:
    """Validate observed readiness values against manifest expectations."""

    return [
        _check(
            "readiness_case_id",
            entry.case_id == manifest.expected_readiness_case_id,
            "readiness case id matches",
        ),
        _check(
            "readiness_case_kind",
            entry.case_kind == manifest.expected_readiness_case_kind,
            "readiness case kind matches",
        ),
        _check(
            "readiness_status",
            entry.readiness_status == manifest.expected_readiness_status,
            "readiness status matches",
        ),
        _check(
            "construction_case_status",
            (
                entry.construction_case_status
                == manifest.expected_construction_case_status
            ),
            "construction case status matches",
        ),
        _check(
            "frontier_status",
            (
                getattr(frontier_report, "frontier_status", "")
                == manifest.expected_frontier_status
            ),
            "frontier status matches",
        ),
        _check(
            "frontier_blocker",
            (
                getattr(frontier_report, "frontier_blocked_by", "")
                == manifest.expected_frontier_blocker
            ),
            "frontier blocker matches",
        ),
        _check(
            "support_surface_count",
            (
                getattr(frontier_report, "support_surface_count", 0)
                == manifest.expected_support_surface_count
            ),
            "support surface count matches",
        ),
        _check(
            "certificate_count",
            (
                getattr(certificate_report, "certificate_count", 0)
                == manifest.expected_certificate_count
            ),
            "certificate count matches",
            "certificate count mismatch",
        ),
        _check(
            "certificate_step_count",
            (
                getattr(certificate_report, "certificate_step_count", 0)
                == manifest.expected_certificate_step_count
            ),
            "certificate step count matches",
            "certificate step count mismatch",
        ),
        _check(
            "diagonal_instance_code_length",
            diagonal_instance_code_length
            == manifest.expected_diagonal_instance_code_length,
            "diagonal instance code length matches",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
        ),
        _check(
            "readiness_entry",
            entry.accepted,
            "readiness entry remains certificate-ready and proof-open",
        ),
    ]


def _diagonal_instance_code_length(frontier_report: Any) -> int:
    """Return the observed diagonal-instance code length from frontier facts."""

    support_facts = getattr(frontier_report, "support_facts", {}) or {}
    closure_facts = support_facts.get("diagonal_instance_closure", {})
    value = closure_facts.get("diagonal_instance_code_length", 0)
    if isinstance(value, int):
        return value
    return 0


def _readiness_entry_payload(
    entry: FixedPointDiagonalInstanceClosureProofReadinessEntry,
) -> dict[str, Any]:
    """Return a JSON-ready readiness entry."""

    return {
        "case_id": entry.case_id,
        "case_kind": entry.case_kind,
        "construction_case_status": entry.construction_case_status,
        "readiness_status": entry.readiness_status,
        "certificate_ready": entry.certificate_ready,
        "open_proof_blocker": entry.open_proof_blocker,
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


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureProofReadinessValidation:
    """Return an accepted validation result."""

    return FixedPointDiagonalInstanceClosureProofReadinessValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointDiagonalInstanceClosureProofReadinessValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointDiagonalInstanceClosureProofReadinessValidation(
        subject=subject,
        accepted=condition,
        detail=accepted_detail if condition else rejected_detail or accepted_detail,
    )


def _non_claims_are_guarded(non_claims: tuple[str, ...]) -> bool:
    """Return whether every proof-promotion phrase is explicitly negated."""

    return all(f"no {claim}" in non_claims for claim in PROOF_PROMOTION_NON_CLAIMS)


def _failed_subject_for_result(subject: str) -> str:
    """Map verbose result subjects to stable failure subjects."""

    if subject in {
        "diagonal_instance_closure_frontier_status",
        "diagonal_instance_closure_certificate",
    }:
        return "fixed-point-diagonal-instance-closure-proof-readiness-dependencies"
    if subject in {"certificate_count", "certificate_step_count"}:
        return "fixed-point-diagonal-instance-closure-proof-readiness-certificate"
    if subject in {"non_claims", "non_claim_promotion_boundary"}:
        return "fixed-point-diagonal-instance-closure-proof-readiness-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-diagonal-instance-closure-proof-readiness-boundary"
    if subject in {
        "readiness_case_id",
        "readiness_case_kind",
        "readiness_status",
        "construction_case_status",
        "frontier_status",
        "frontier_blocker",
        "support_surface_count",
        "diagonal_instance_code_length",
        "readiness_entry",
    }:
        return "fixed-point-diagonal-instance-closure-proof-readiness"
    if subject.startswith("expected_") or subject in {"readiness_id", "schema_version"}:
        return "fixed-point-diagonal-instance-closure-proof-readiness-manifest"
    return (
        "fixed-point-diagonal-instance-closure-proof-readiness-"
        + subject.replace("_", "-")
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_diagonal_instance_closure_proof_readiness_cli()


if __name__ == "__main__":
    raise SystemExit(main())
