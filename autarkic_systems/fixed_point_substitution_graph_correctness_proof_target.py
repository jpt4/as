"""Blocked proof target for fixed-point substitution graph correctness.

ADR-0320 names the current proof-closure gate for the selected
``substitution-graph-correctness-proof`` root obligation. The target ties
accepted finite certificate support, proof-readiness, and selected-root
coverage to explicit missing proof artifacts. It deliberately remains blocked
and does not promote the construction case from ``proof-case-open``.
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
from autarkic_systems.fixed_point_substitution_graph_correctness_proof_readiness import (
    load_fixed_point_substitution_graph_correctness_proof_readiness,
    validate_fixed_point_substitution_graph_correctness_proof_readiness,
)
from autarkic_systems.fixed_point_selected_root_proof_readiness_coverage import (
    load_fixed_point_selected_root_proof_readiness_coverage,
    validate_fixed_point_selected_root_proof_readiness_coverage,
)


DEFAULT_TARGET = Path(
    "claims/fixed_point_substitution_graph_correctness_proof_target.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_TARGET_ID = "as-fixed-point-substitution-graph-correctness-proof-target-v1"
REQUIRED_CASE_ID = "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS"
REQUIRED_CASE_KIND = "substitution-graph-correctness-proof"
REQUIRED_PROOF_TARGET_STATUS = "blocked-proof-closure-targeted"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_MISSING_PROOF_ARTIFACTS = (
    "formal graph-correctness derivation",
    "proof-rule derivation from certificate steps",
    "construction-case promotion rule",
)
REQUIRED_NON_CLAIMS = (
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no fixed-point construction proof",
    "no self-consistency theorem",
)
EXPECTED_PATHS = {
    "substitution_graph_correctness_certificate_path": (
        "claims/fixed_point_substitution_graph_correctness_certificate.json"
    ),
    "substitution_graph_correctness_readiness_path": (
        "claims/fixed_point_substitution_graph_correctness_proof_readiness.json"
    ),
    "selected_root_readiness_coverage_path": (
        "claims/fixed_point_selected_root_proof_readiness_coverage.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "substitution graph correctness proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "fixed-point construction proof",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofTargetManifest:
    """Loaded manifest for the graph-correctness proof target."""

    path: Path
    schema_version: int
    target_id: str
    reviewed_at: str
    purpose: str
    substitution_graph_correctness_certificate_path: str
    substitution_graph_correctness_readiness_path: str
    selected_root_readiness_coverage_path: str
    expected_case_id: str
    expected_case_kind: str
    expected_proof_target_status: str
    expected_readiness_status: str
    expected_certificate_count: int
    expected_certificate_step_count: int
    expected_correctness_case_count: int
    expected_finite_dependency_count: int
    expected_missing_proof_artifacts: tuple[str, ...]
    expected_missing_proof_artifact_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofTargetValidation:
    """One validation result for the graph-correctness proof target."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessProofTargetReport:
    """Validation report for the graph-correctness proof target."""

    manifest: FixedPointSubstitutionGraphCorrectnessProofTargetManifest
    substitution_graph_correctness_certificate_path: Path
    substitution_graph_correctness_readiness_path: Path
    selected_root_readiness_coverage_path: Path
    willard_map_path: Path
    certificate_accepted: bool
    readiness_accepted: bool
    selected_root_coverage_accepted: bool
    case_id: str
    case_kind: str
    proof_target_status: str
    readiness_status: str
    certificate_count: int
    certificate_step_count: int
    correctness_case_count: int
    finite_dependency_count: int
    missing_proof_artifacts: tuple[str, ...]
    proof_boundary_preserved: bool
    results: tuple[FixedPointSubstitutionGraphCorrectnessProofTargetValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether every proof-target validation passed."""

        return all(result.accepted for result in self.results)

    @property
    def missing_proof_artifact_count(self) -> int:
        """Return how many proof artifacts are still missing."""

        return len(self.missing_proof_artifacts)

    @property
    def proof_closure_ready(self) -> bool:
        """Return whether proof closure is ready to be promoted."""

        return self.accepted and self.missing_proof_artifact_count == 0

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
    certificates: tuple[Any, ...] = ()
    readiness_entry: Any = None
    readiness_entries: tuple[Any, ...] = ()
    proof_boundary_preserved: bool = False


def load_fixed_point_substitution_graph_correctness_proof_target(
    path: Path | str = DEFAULT_TARGET,
) -> FixedPointSubstitutionGraphCorrectnessProofTargetManifest:
    """Load the graph-correctness proof-target manifest."""

    target_path = Path(path)
    data = json.loads(target_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionGraphCorrectnessProofTargetManifest(
        path=target_path,
        schema_version=_required_int(data, "schema_version"),
        target_id=_required_text(data, "target_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        substitution_graph_correctness_certificate_path=_required_text(
            data,
            "substitution_graph_correctness_certificate_path",
        ),
        substitution_graph_correctness_readiness_path=_required_text(
            data,
            "substitution_graph_correctness_readiness_path",
        ),
        selected_root_readiness_coverage_path=_required_text(
            data,
            "selected_root_readiness_coverage_path",
        ),
        expected_case_id=_required_text(data, "expected_case_id"),
        expected_case_kind=_required_text(data, "expected_case_kind"),
        expected_proof_target_status=_required_text(
            data,
            "expected_proof_target_status",
        ),
        expected_readiness_status=_required_text(data, "expected_readiness_status"),
        expected_certificate_count=_required_int(data, "expected_certificate_count"),
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
        expected_missing_proof_artifacts=tuple(
            _required_text_list(data, "expected_missing_proof_artifacts")
        ),
        expected_missing_proof_artifact_count=_required_int(
            data,
            "expected_missing_proof_artifact_count",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_substitution_graph_correctness_proof_target(
    manifest: FixedPointSubstitutionGraphCorrectnessProofTargetManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionGraphCorrectnessProofTargetReport:
    """Validate the blocked proof-closure target for the selected root."""

    checked_willard_map_path = Path(willard_map_path)
    certificate_path = _resolve_path(
        manifest.path,
        manifest.substitution_graph_correctness_certificate_path,
    )
    readiness_path = _resolve_path(
        manifest.path,
        manifest.substitution_graph_correctness_readiness_path,
    )
    coverage_path = _resolve_path(
        manifest.path,
        manifest.selected_root_readiness_coverage_path,
    )
    results: list[FixedPointSubstitutionGraphCorrectnessProofTargetValidation] = [
        _accepted("manifest", f"loaded {manifest.target_id}")
    ]
    results.extend(_validate_manifest(manifest))

    certificate_report = _load_certificate(certificate_path, checked_willard_map_path)
    readiness_report = _load_readiness(readiness_path, checked_willard_map_path)
    coverage_report = _load_coverage(coverage_path, checked_willard_map_path)
    results.extend(
        _validate_dependencies(certificate_report, readiness_report, coverage_report)
    )

    certificate = _first(tuple(getattr(certificate_report, "certificates", ())))
    readiness_entry = getattr(readiness_report, "readiness_entry", None)
    case_id = str(getattr(readiness_entry, "case_id", ""))
    case_kind = str(getattr(readiness_entry, "case_kind", ""))
    readiness_status = str(getattr(readiness_entry, "readiness_status", ""))
    certificate_count = int(getattr(certificate_report, "certificate_count", 0))
    certificate_step_count = int(
        getattr(certificate_report, "certificate_step_count", 0)
    )
    correctness_case_count = int(getattr(certificate, "correctness_case_count", 0))
    finite_dependency_count = int(getattr(certificate, "finite_dependency_count", 0))
    missing_proof_artifacts = manifest.expected_missing_proof_artifacts
    proof_target_status = manifest.expected_proof_target_status
    proof_boundary_preserved = (
        bool(getattr(certificate_report, "accepted", False))
        and bool(getattr(readiness_report, "accepted", False))
        and bool(getattr(coverage_report, "accepted", False))
        and bool(getattr(readiness_report, "proof_boundary_preserved", False))
        and bool(getattr(coverage_report, "proof_boundary_preserved", False))
        and case_id == REQUIRED_CASE_ID
        and case_kind == REQUIRED_CASE_KIND
        and readiness_status == REQUIRED_READINESS_STATUS
        and correctness_case_count == manifest.expected_correctness_case_count
        and finite_dependency_count == manifest.expected_finite_dependency_count
        and certificate is not None
        and str(getattr(certificate, "certificate_status", ""))
        == "accepted-finite-certificate-not-proof"
        and missing_proof_artifacts == REQUIRED_MISSING_PROOF_ARTIFACTS
        and _non_claims_are_guarded(manifest.non_claims)
    )
    results.extend(
        _validate_target(
            manifest,
            case_id,
            case_kind,
            proof_target_status,
            readiness_status,
            certificate_count,
            certificate_step_count,
            correctness_case_count,
            finite_dependency_count,
            missing_proof_artifacts,
            proof_boundary_preserved,
        )
    )

    return FixedPointSubstitutionGraphCorrectnessProofTargetReport(
        manifest=manifest,
        substitution_graph_correctness_certificate_path=certificate_path,
        substitution_graph_correctness_readiness_path=readiness_path,
        selected_root_readiness_coverage_path=coverage_path,
        willard_map_path=checked_willard_map_path,
        certificate_accepted=bool(getattr(certificate_report, "accepted", False)),
        readiness_accepted=bool(getattr(readiness_report, "accepted", False)),
        selected_root_coverage_accepted=bool(
            getattr(coverage_report, "accepted", False)
        ),
        case_id=case_id,
        case_kind=case_kind,
        proof_target_status=proof_target_status,
        readiness_status=readiness_status,
        certificate_count=certificate_count,
        certificate_step_count=certificate_step_count,
        correctness_case_count=correctness_case_count,
        finite_dependency_count=finite_dependency_count,
        missing_proof_artifacts=missing_proof_artifacts,
        proof_boundary_preserved=proof_boundary_preserved,
        results=tuple(results),
    )


def fixed_point_substitution_graph_correctness_proof_target_payload(
    report: FixedPointSubstitutionGraphCorrectnessProofTargetReport,
) -> dict[str, Any]:
    """Return a JSON-ready proof-target payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "target_id": report.manifest.target_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "substitution_graph_correctness_certificate_path": str(
            report.substitution_graph_correctness_certificate_path
        ),
        "substitution_graph_correctness_readiness_path": str(
            report.substitution_graph_correctness_readiness_path
        ),
        "selected_root_readiness_coverage_path": str(
            report.selected_root_readiness_coverage_path
        ),
        "willard_map": str(report.willard_map_path),
        "observed_certificate_accepted": report.certificate_accepted,
        "observed_readiness_accepted": report.readiness_accepted,
        "observed_selected_root_coverage_accepted": (
            report.selected_root_coverage_accepted
        ),
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "case_id": report.case_id,
        "case_kind": report.case_kind,
        "proof_target_status": report.proof_target_status,
        "readiness_status": report.readiness_status,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "correctness_case_count": report.correctness_case_count,
        "finite_dependency_count": report.finite_dependency_count,
        "missing_proof_artifacts": list(report.missing_proof_artifacts),
        "missing_proof_artifact_count": report.missing_proof_artifact_count,
        "proof_closure_ready": report.proof_closure_ready,
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


def format_fixed_point_substitution_graph_correctness_proof_target_report(
    report: FixedPointSubstitutionGraphCorrectnessProofTargetReport,
) -> str:
    """Format a concise text report for the proof target."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point substitution graph correctness proof target: {status}",
        f"Target: {report.manifest.target_id}",
        f"Case: {report.case_id} ({report.case_kind})",
        f"Proof target status: {report.proof_target_status}",
        f"Readiness status: {report.readiness_status}",
        f"Certificates: {report.certificate_count}",
        f"Certificate steps: {report.certificate_step_count}",
        f"Correctness cases: {report.correctness_case_count}",
        f"Finite dependencies: {report.finite_dependency_count}",
        "Missing proof artifacts: "
        + _joined_or_none(report.missing_proof_artifacts),
        f"Proof closure ready: {str(report.proof_closure_ready).lower()}",
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


def run_fixed_point_substitution_graph_correctness_proof_target_cli(
    argv: list[str] | None = None,
) -> int:
    """Run graph-correctness proof-target validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_substitution_graph_correctness_proof_target"
        ),
        description=(
            "Validate the blocked proof-closure target for the AS "
            "substitution-graph-correctness root obligation."
        ),
    )
    parser.add_argument(
        "--target",
        default=str(DEFAULT_TARGET),
        help="Path to the graph-correctness proof-target manifest.",
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

    manifest = load_fixed_point_substitution_graph_correctness_proof_target(args.target)
    report = validate_fixed_point_substitution_graph_correctness_proof_target(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_substitution_graph_correctness_proof_target_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_substitution_graph_correctness_proof_target_report(report))
    return 0 if report.accepted else 1


def _resolve_path(base_path: Path, value: str) -> Path:
    """Resolve a manifest-local path while preserving root-relative paths."""

    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    candidate = base_path.parent / path
    if candidate.exists():
        return candidate
    return path


def _load_certificate(path: Path, willard_map_path: Path) -> Any:
    """Load and validate substitution-graph certificate support."""

    try:
        manifest = load_fixed_point_substitution_graph_correctness_certificate(path)
        return validate_fixed_point_substitution_graph_correctness_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-substitution-graph-certificate-load",),
        )


def _load_readiness(path: Path, willard_map_path: Path) -> Any:
    """Load and validate substitution-graph proof-readiness."""

    try:
        manifest = load_fixed_point_substitution_graph_correctness_proof_readiness(path)
        return validate_fixed_point_substitution_graph_correctness_proof_readiness(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-substitution-graph-readiness-load",),
        )


def _load_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate selected-root proof-readiness coverage."""

    try:
        manifest = load_fixed_point_selected_root_proof_readiness_coverage(path)
        return validate_fixed_point_selected_root_proof_readiness_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-selected-root-readiness-coverage-load",),
        )


def _validate_manifest(
    manifest: FixedPointSubstitutionGraphCorrectnessProofTargetManifest,
) -> list[FixedPointSubstitutionGraphCorrectnessProofTargetValidation]:
    """Validate manifest constants and proof-boundary guardrails."""

    results = [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "target_id",
            manifest.target_id == REQUIRED_TARGET_ID,
            "target id matches",
            "unexpected target id",
        ),
    ]
    for field, expected in EXPECTED_PATHS.items():
        results.append(
            _check(
                field,
                getattr(manifest, field) == expected,
                f"{expected} referenced",
                f"{field} mismatch",
            )
        )
    results.extend(
        [
            _check(
                "expected_case_id",
                manifest.expected_case_id == REQUIRED_CASE_ID,
                "case id matches",
            ),
            _check(
                "expected_case_kind",
                manifest.expected_case_kind == REQUIRED_CASE_KIND,
                "case kind matches",
            ),
            _check(
                "expected_proof_target_status",
                manifest.expected_proof_target_status
                == REQUIRED_PROOF_TARGET_STATUS,
                "proof target status matches",
            ),
            _check(
                "expected_readiness_status",
                manifest.expected_readiness_status == REQUIRED_READINESS_STATUS,
                "readiness status matches",
            ),
            _check(
                "expected_certificate_count",
                manifest.expected_certificate_count == 1,
                "certificate count matches",
            ),
            _check(
                "expected_certificate_step_count",
                manifest.expected_certificate_step_count == 7,
                "certificate step count matches",
            ),
            _check(
                "expected_correctness_case_count",
                manifest.expected_correctness_case_count == 5,
                "correctness case count matches",
            ),
            _check(
                "expected_finite_dependency_count",
                manifest.expected_finite_dependency_count == 5,
                "finite dependency count matches",
            ),
            _check(
                "expected_missing_proof_artifacts",
                manifest.expected_missing_proof_artifacts
                == REQUIRED_MISSING_PROOF_ARTIFACTS,
                "missing proof artifacts match",
                "missing proof artifact mismatch",
            ),
            _check(
                "expected_missing_proof_artifact_count",
                manifest.expected_missing_proof_artifact_count
                == len(REQUIRED_MISSING_PROOF_ARTIFACTS),
                "missing proof artifact count matches",
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
            _check(
                "next_as_action",
                bool(manifest.next_as_action),
                "next action present",
            ),
        ]
    )
    return results


def _validate_dependencies(
    certificate_report: Any,
    readiness_report: Any,
    coverage_report: Any,
) -> list[FixedPointSubstitutionGraphCorrectnessProofTargetValidation]:
    """Validate that each dependency accepts."""

    return [
        _check(
            "certificate.accepted",
            bool(getattr(certificate_report, "accepted", False)),
            "certificate accepted",
            "certificate rejected",
        ),
        _check(
            "readiness.accepted",
            bool(getattr(readiness_report, "accepted", False)),
            "readiness accepted",
            "readiness rejected",
        ),
        _check(
            "selected_root_coverage.accepted",
            bool(getattr(coverage_report, "accepted", False)),
            "selected-root coverage accepted",
            "selected-root coverage rejected",
        ),
    ]


def _validate_target(
    manifest: FixedPointSubstitutionGraphCorrectnessProofTargetManifest,
    case_id: str,
    case_kind: str,
    proof_target_status: str,
    readiness_status: str,
    certificate_count: int,
    certificate_step_count: int,
    correctness_case_count: int,
    finite_dependency_count: int,
    missing_proof_artifacts: tuple[str, ...],
    proof_boundary_preserved: bool,
) -> list[FixedPointSubstitutionGraphCorrectnessProofTargetValidation]:
    """Validate observed proof-target facts against the manifest."""

    return [
        _check(
            "target.case_id",
            case_id == manifest.expected_case_id,
            "case id matches",
            "case id mismatch",
        ),
        _check(
            "target.case_kind",
            case_kind == manifest.expected_case_kind,
            "case kind matches",
            "case kind mismatch",
        ),
        _check(
            "target.proof_target_status",
            proof_target_status == manifest.expected_proof_target_status,
            "proof target status matches",
            "proof target status mismatch",
        ),
        _check(
            "target.readiness_status",
            readiness_status == manifest.expected_readiness_status,
            "readiness status matches",
            "readiness status mismatch",
        ),
        _check(
            "target.certificate_count",
            certificate_count == manifest.expected_certificate_count,
            "certificate count matches",
            "certificate count mismatch",
        ),
        _check(
            "target.certificate_step_count",
            certificate_step_count == manifest.expected_certificate_step_count,
            "certificate step count matches",
            "certificate step count mismatch",
        ),
        _check(
            "target.correctness_case_count",
            correctness_case_count == manifest.expected_correctness_case_count,
            "correctness case count matches",
            "correctness case count mismatch",
        ),
        _check(
            "target.finite_dependency_count",
            finite_dependency_count == manifest.expected_finite_dependency_count,
            "finite dependency count matches",
            "finite dependency count mismatch",
        ),
        _check(
            "target.missing_proof_artifacts",
            missing_proof_artifacts == manifest.expected_missing_proof_artifacts,
            "missing proof artifacts match",
            "missing proof artifact mismatch",
        ),
        _check(
            "target.missing_proof_artifact_count",
            len(missing_proof_artifacts)
            == manifest.expected_missing_proof_artifact_count,
            "missing proof artifact count matches",
            "missing proof artifact count mismatch",
        ),
        _check(
            "target.proof_closure_blocked",
            len(missing_proof_artifacts) > 0,
            "proof closure remains blocked",
            "proof closure unexpectedly ready",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
            "proof boundary not preserved",
        ),
    ]


def _first(values: tuple[Any, ...]) -> Any:
    """Return the first tuple item or None."""

    return values[0] if values else None


def _required_text(data: dict[str, Any], key: str) -> str:
    """Return a required non-empty text field from JSON data."""

    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    """Return a required integer field from JSON data."""

    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    """Return a required list of non-empty text values from JSON data."""

    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must contain non-empty text")
    return value


def _non_claims_are_guarded(non_claims: tuple[str, ...]) -> bool:
    """Return whether every proof-sensitive non-claim has an explicit no-prefix."""

    return all(f"no {claim}" in non_claims for claim in PROOF_PROMOTION_NON_CLAIMS)


def _check(
    subject: str,
    accepted: bool,
    ok_detail: str,
    fail_detail: str | None = None,
) -> FixedPointSubstitutionGraphCorrectnessProofTargetValidation:
    """Build a validation result."""

    return FixedPointSubstitutionGraphCorrectnessProofTargetValidation(
        subject=subject,
        accepted=accepted,
        detail=ok_detail if accepted else (fail_detail or ok_detail),
    )


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionGraphCorrectnessProofTargetValidation:
    """Build an accepted validation result."""

    return FixedPointSubstitutionGraphCorrectnessProofTargetValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    """Map detailed validation subjects to compact failure labels."""

    if subject.startswith("certificate.") or subject.startswith("readiness.") or subject.startswith("selected_root_coverage."):
        return "fixed-point-substitution-graph-correctness-proof-target-dependencies"
    if subject.startswith("target.missing_proof_artifact") or subject.startswith(
        "expected_missing_proof_artifact"
    ):
        return "fixed-point-substitution-graph-correctness-proof-target-artifacts"
    if subject.startswith("target.correctness_case") or subject.startswith(
        "expected_correctness_case"
    ):
        return "fixed-point-substitution-graph-correctness-proof-target-cases"
    if subject.startswith("target.finite_dependency") or subject.startswith(
        "expected_finite_dependency"
    ):
        return "fixed-point-substitution-graph-correctness-proof-target-dependencies"
    if subject.startswith("target."):
        return "fixed-point-substitution-graph-correctness-proof-target-status"
    if subject.startswith("proof_boundary") or subject.startswith("non_claim_promotion_boundary"):
        return "fixed-point-substitution-graph-correctness-proof-target-proof-boundary"
    return "fixed-point-substitution-graph-correctness-proof-target-manifest"


def _joined_or_none(values: tuple[str, ...]) -> str:
    """Render a tuple for text output."""

    return ", ".join(values) if values else "none"


def main() -> int:
    """Module entry point."""

    return run_fixed_point_substitution_graph_correctness_proof_target_cli()


if __name__ == "__main__":
    raise SystemExit(main())
