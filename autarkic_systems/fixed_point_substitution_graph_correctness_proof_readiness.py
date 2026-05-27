"""Proof-readiness handoff for fixed-point graph correctness.

ADR-0314 composes the compact substitution graph correctness frontier status
with the finite certificate support for the fixed-point graph-correctness
construction case. The resulting surface records that the selected root case
is certificate-ready while preserving that the proof case remains open. It is
not a substitution graph correctness proof, bridge-equality proof,
fixed-point equation proof, arithmetized proof predicate, or self-consistency
theorem.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_substitution_graph_correctness_certificate import (
    load_fixed_point_substitution_graph_correctness_certificate,
    validate_fixed_point_substitution_graph_correctness_certificate,
)
from autarkic_systems.substitution_graph_correctness_frontier_status import (
    load_substitution_graph_correctness_frontier_status,
    validate_substitution_graph_correctness_frontier_status,
)


DEFAULT_READINESS = Path(
    "claims/fixed_point_substitution_graph_correctness_proof_readiness.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_READINESS_ID = (
    "as-fixed-point-substitution-graph-correctness-proof-readiness-v1"
)
REQUIRED_CASE_ID = "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS"
REQUIRED_CASE_KIND = "substitution-graph-correctness-proof"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_CONSTRUCTION_CASE_STATUS = "proof-case-open"
REQUIRED_FRONTIER_STATUS = "blocked"
REQUIRED_FRONTIER_BLOCKER = "substitution-graph-correctness"
REQUIRED_OPEN_PROOF_BLOCKER = "substitution-graph-correctness-proof"
REQUIRED_CERTIFICATE_COUNT = 1
REQUIRED_CERTIFICATE_STEP_COUNT = 7
REQUIRED_CORRECTNESS_CASE_COUNT = 5
REQUIRED_FINITE_DEPENDENCY_COUNT = 5
REQUIRED_NON_CLAIMS = (
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "substitution_graph_correctness_frontier_status_path": (
        "claims/substitution_graph_correctness_frontier_status.json"
    ),
    "substitution_graph_correctness_certificate_path": (
        "claims/fixed_point_substitution_graph_correctness_certificate.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "substitution graph correctness proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofReadinessManifest:
    """Loaded manifest for the graph-correctness proof-readiness handoff."""

    path: Path
    schema_version: int
    readiness_id: str
    reviewed_at: str
    purpose: str
    substitution_graph_correctness_frontier_status_path: str
    substitution_graph_correctness_certificate_path: str
    expected_readiness_case_id: str
    expected_readiness_case_kind: str
    expected_readiness_status: str
    expected_construction_case_status: str
    expected_frontier_status: str
    expected_frontier_blocker: str
    expected_certificate_count: int
    expected_certificate_step_count: int
    expected_correctness_case_count: int
    expected_finite_dependency_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofReadinessEntry:
    """Derived readiness state for substitution graph correctness."""

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
            and self.open_proof_blocker == REQUIRED_OPEN_PROOF_BLOCKER
        )


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofReadinessValidation:
    """One validation result for graph-correctness proof readiness."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofReadinessReport:
    """Validation report for substitution-graph-correctness proof readiness."""

    manifest: FixedPointSubstitutionGraphCorrectnessProofReadinessManifest
    substitution_graph_correctness_frontier_status_path: Path
    substitution_graph_correctness_certificate_path: Path
    willard_map_path: Path
    frontier_accepted: bool
    certificate_accepted: bool
    frontier_status: str
    frontier_blocker: str
    certificate_count: int
    certificate_step_count: int
    correctness_case_count: int
    finite_dependency_count: int
    proof_boundary_preserved: bool
    readiness_entry: FixedPointSubstitutionGraphCorrectnessProofReadinessEntry
    results: tuple[
        FixedPointSubstitutionGraphCorrectnessProofReadinessValidation,
        ...,
    ]

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
    support_surfaces: tuple[Any, ...] = ()
    certificate_count: int = 0
    certificate_step_count: int = 0
    certificates: tuple[Any, ...] = ()


def load_fixed_point_substitution_graph_correctness_proof_readiness(
    path: Path | str = DEFAULT_READINESS,
) -> FixedPointSubstitutionGraphCorrectnessProofReadinessManifest:
    """Load the substitution-graph-correctness proof-readiness manifest."""

    readiness_path = Path(path)
    data = json.loads(readiness_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionGraphCorrectnessProofReadinessManifest(
        path=readiness_path,
        schema_version=_required_int(data, "schema_version"),
        readiness_id=_required_text(data, "readiness_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        substitution_graph_correctness_frontier_status_path=_required_text(
            data,
            "substitution_graph_correctness_frontier_status_path",
        ),
        substitution_graph_correctness_certificate_path=_required_text(
            data,
            "substitution_graph_correctness_certificate_path",
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
        expected_certificate_count=_required_int(
            data,
            "expected_certificate_count",
        ),
        expected_certificate_step_count=_required_int(
            data,
            "expected_certificate_step_count",
        ),
        expected_correctness_case_count=_required_int(
            data,
            "expected_correctness_case_count",
        ),
        expected_finite_dependency_count=_required_int(
            data,
            "expected_finite_dependency_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_substitution_graph_correctness_proof_readiness(
    manifest: FixedPointSubstitutionGraphCorrectnessProofReadinessManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionGraphCorrectnessProofReadinessReport:
    """Validate certificate-ready/proof-open readiness for graph correctness."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointSubstitutionGraphCorrectnessProofReadinessValidation] = [
        _accepted("manifest", f"loaded {manifest.readiness_id}")
    ]
    results.extend(_validate_manifest(manifest))

    frontier_report = _load_frontier(
        paths["substitution_graph_correctness_frontier_status_path"]
    )
    certificate_report = _load_certificate(
        paths["substitution_graph_correctness_certificate_path"],
        checked_willard_map_path,
    )
    results.extend(_validate_dependencies(frontier_report, certificate_report))

    certificate = _first_certificate(certificate_report)
    readiness_entry = _derive_readiness_entry(
        manifest,
        frontier_report,
        certificate_report,
        certificate,
    )
    correctness_case_count = int(getattr(certificate, "correctness_case_count", 0))
    finite_dependency_count = int(getattr(certificate, "finite_dependency_count", 0))
    proof_boundary_preserved = (
        bool(getattr(frontier_report, "accepted", False))
        and bool(getattr(certificate_report, "accepted", False))
        and bool(getattr(certificate, "proof_boundary_preserved", False))
        and readiness_entry.construction_case_status
        == REQUIRED_CONSTRUCTION_CASE_STATUS
        and readiness_entry.open_proof_blocker == REQUIRED_OPEN_PROOF_BLOCKER
    )
    results.extend(
        _validate_readiness(
            manifest,
            frontier_report,
            certificate_report,
            readiness_entry,
            correctness_case_count,
            finite_dependency_count,
            proof_boundary_preserved,
        )
    )

    return FixedPointSubstitutionGraphCorrectnessProofReadinessReport(
        manifest=manifest,
        substitution_graph_correctness_frontier_status_path=paths[
            "substitution_graph_correctness_frontier_status_path"
        ],
        substitution_graph_correctness_certificate_path=paths[
            "substitution_graph_correctness_certificate_path"
        ],
        willard_map_path=checked_willard_map_path,
        frontier_accepted=bool(getattr(frontier_report, "accepted", False)),
        certificate_accepted=bool(getattr(certificate_report, "accepted", False)),
        frontier_status=str(getattr(frontier_report, "frontier_status", "")),
        frontier_blocker=str(getattr(frontier_report, "frontier_blocked_by", "")),
        certificate_count=int(getattr(certificate_report, "certificate_count", 0)),
        certificate_step_count=int(
            getattr(certificate_report, "certificate_step_count", 0)
        ),
        correctness_case_count=correctness_case_count,
        finite_dependency_count=finite_dependency_count,
        proof_boundary_preserved=proof_boundary_preserved,
        readiness_entry=readiness_entry,
        results=tuple(results),
    )


def fixed_point_substitution_graph_correctness_proof_readiness_payload(
    report: FixedPointSubstitutionGraphCorrectnessProofReadinessReport,
) -> dict[str, Any]:
    """Return a JSON-ready proof-readiness payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "readiness_manifest": str(report.manifest.path),
        "readiness_id": report.manifest.readiness_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "substitution_graph_correctness_frontier_status_path": str(
            report.substitution_graph_correctness_frontier_status_path
        ),
        "substitution_graph_correctness_certificate_path": str(
            report.substitution_graph_correctness_certificate_path
        ),
        "willard_map": str(report.willard_map_path),
        "observed_frontier_accepted": report.frontier_accepted,
        "observed_certificate_accepted": report.certificate_accepted,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "frontier_status": report.frontier_status,
        "frontier_blocker": report.frontier_blocker,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "correctness_case_count": report.correctness_case_count,
        "finite_dependency_count": report.finite_dependency_count,
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


def format_fixed_point_substitution_graph_correctness_proof_readiness_report(
    report: FixedPointSubstitutionGraphCorrectnessProofReadinessReport,
) -> str:
    """Format a concise text report for the proof-readiness handoff."""

    status = "accepted" if report.accepted else "rejected"
    entry = report.readiness_entry
    lines = [
        f"Fixed-point substitution graph correctness proof readiness: {status}",
        f"Readiness: {report.manifest.readiness_id}",
        f"Construction case: {entry.case_id}",
        f"Case kind: {entry.case_kind}",
        f"Readiness status: {entry.readiness_status}",
        f"Frontier: {report.frontier_status} by {report.frontier_blocker}",
        f"Construction case status: {entry.construction_case_status}",
        f"Certificate ready: {str(entry.certificate_ready).lower()}",
        f"Certificate steps: {report.certificate_step_count}",
        f"Correctness cases: {report.correctness_case_count}",
        f"Finite dependencies: {report.finite_dependency_count}",
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


def run_fixed_point_substitution_graph_correctness_proof_readiness_cli(
    argv: list[str] | None = None,
) -> int:
    """Run substitution-graph-correctness proof-readiness validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_substitution_graph_correctness_proof_readiness"
        ),
        description=(
            "Validate certificate-ready/proof-open readiness for the AS "
            "fixed-point substitution-graph-correctness proof case."
        ),
    )
    parser.add_argument(
        "--readiness",
        default=str(DEFAULT_READINESS),
        help="Path to the substitution-graph-correctness readiness manifest.",
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

    manifest = load_fixed_point_substitution_graph_correctness_proof_readiness(
        args.readiness
    )
    report = validate_fixed_point_substitution_graph_correctness_proof_readiness(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_substitution_graph_correctness_proof_readiness_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_substitution_graph_correctness_proof_readiness_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointSubstitutionGraphCorrectnessProofReadinessManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "substitution_graph_correctness_frontier_status_path": _resolve_path(
            manifest.path,
            manifest.substitution_graph_correctness_frontier_status_path,
        ),
        "substitution_graph_correctness_certificate_path": _resolve_path(
            manifest.path,
            manifest.substitution_graph_correctness_certificate_path,
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


def _load_frontier(path: Path) -> Any:
    """Load and validate the substitution-graph-correctness frontier status."""

    try:
        manifest = load_substitution_graph_correctness_frontier_status(path)
        return validate_substitution_graph_correctness_frontier_status(manifest)
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("substitution-graph-correctness-frontier-status-load",),
        )


def _load_certificate(path: Path, willard_map_path: Path) -> Any:
    """Load and validate the substitution-graph-correctness certificate support."""

    try:
        manifest = load_fixed_point_substitution_graph_correctness_certificate(path)
        return validate_fixed_point_substitution_graph_correctness_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-substitution-graph-correctness-certificate-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointSubstitutionGraphCorrectnessProofReadinessManifest,
) -> list[FixedPointSubstitutionGraphCorrectnessProofReadinessValidation]:
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
            "expected_correctness_case_count",
            (
                manifest.expected_correctness_case_count
                == REQUIRED_CORRECTNESS_CASE_COUNT
            ),
            "correctness case count matches",
        ),
        _check(
            "expected_finite_dependency_count",
            (
                manifest.expected_finite_dependency_count
                == REQUIRED_FINITE_DEPENDENCY_COUNT
            ),
            "finite dependency count matches",
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
) -> list[FixedPointSubstitutionGraphCorrectnessProofReadinessValidation]:
    """Validate that dependency reports accepted before readiness derivation."""

    return [
        _check(
            "substitution_graph_correctness_frontier_status",
            bool(getattr(frontier_report, "accepted", False)),
            "frontier status accepted",
            "frontier status rejected: "
            + _joined_or_none(getattr(frontier_report, "failed_subjects", ())),
        ),
        _check(
            "substitution_graph_correctness_certificate",
            bool(getattr(certificate_report, "accepted", False)),
            "certificate accepted",
            "certificate rejected: "
            + _joined_or_none(getattr(certificate_report, "failed_subjects", ())),
        ),
    ]


def _derive_readiness_entry(
    manifest: FixedPointSubstitutionGraphCorrectnessProofReadinessManifest,
    frontier_report: Any,
    certificate_report: Any,
    certificate: Any,
) -> FixedPointSubstitutionGraphCorrectnessProofReadinessEntry:
    """Derive the readiness entry from the accepted dependency reports."""

    certificate_ready = (
        bool(getattr(certificate_report, "accepted", False))
        and bool(getattr(certificate, "accepted", False))
    )
    return FixedPointSubstitutionGraphCorrectnessProofReadinessEntry(
        case_id=str(getattr(certificate, "construction_case_id", "")),
        case_kind=str(getattr(certificate, "selected_case_kind", "")),
        construction_case_status=(
            REQUIRED_CONSTRUCTION_CASE_STATUS if certificate_ready else ""
        ),
        readiness_status=manifest.expected_readiness_status,
        certificate_ready=certificate_ready,
        open_proof_blocker=REQUIRED_OPEN_PROOF_BLOCKER if certificate_ready else "",
    )


def _validate_readiness(
    manifest: FixedPointSubstitutionGraphCorrectnessProofReadinessManifest,
    frontier_report: Any,
    certificate_report: Any,
    entry: FixedPointSubstitutionGraphCorrectnessProofReadinessEntry,
    correctness_case_count: int,
    finite_dependency_count: int,
    proof_boundary_preserved: bool,
) -> list[FixedPointSubstitutionGraphCorrectnessProofReadinessValidation]:
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
            "correctness_case_count",
            correctness_case_count == manifest.expected_correctness_case_count,
            "correctness case count matches",
            "correctness case count mismatch",
        ),
        _check(
            "finite_dependency_count",
            finite_dependency_count == manifest.expected_finite_dependency_count,
            "finite dependency count matches",
            "finite dependency count mismatch",
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


def _first_certificate(certificate_report: Any) -> Any:
    """Return the first derived certificate object or an empty shim."""

    certificates = tuple(getattr(certificate_report, "certificates", ()))
    if certificates:
        return certificates[0]
    return _DependencyFailure(False, ())


def _readiness_entry_payload(
    entry: FixedPointSubstitutionGraphCorrectnessProofReadinessEntry,
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
) -> FixedPointSubstitutionGraphCorrectnessProofReadinessValidation:
    """Return an accepted validation result."""

    return FixedPointSubstitutionGraphCorrectnessProofReadinessValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointSubstitutionGraphCorrectnessProofReadinessValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointSubstitutionGraphCorrectnessProofReadinessValidation(
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
        "substitution_graph_correctness_frontier_status",
        "substitution_graph_correctness_certificate",
    }:
        return "fixed-point-substitution-graph-correctness-proof-readiness-dependencies"
    if subject in {"certificate_count", "certificate_step_count"}:
        return "fixed-point-substitution-graph-correctness-proof-readiness-certificate"
    if subject in {"non_claims", "non_claim_promotion_boundary"}:
        return "fixed-point-substitution-graph-correctness-proof-readiness-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-substitution-graph-correctness-proof-readiness-boundary"
    if subject in {
        "readiness_case_id",
        "readiness_case_kind",
        "readiness_status",
        "construction_case_status",
        "frontier_status",
        "frontier_blocker",
        "correctness_case_count",
        "finite_dependency_count",
        "readiness_entry",
    }:
        return "fixed-point-substitution-graph-correctness-proof-readiness"
    if subject.startswith("expected_") or subject in {"readiness_id", "schema_version"}:
        return "fixed-point-substitution-graph-correctness-proof-readiness-manifest"
    return (
        "fixed-point-substitution-graph-correctness-proof-readiness-"
        + subject.replace("_", "-")
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_substitution_graph_correctness_proof_readiness_cli()


if __name__ == "__main__":
    raise SystemExit(main())
