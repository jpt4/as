"""Blocked proof target for substitution representability.

ADR-0322 names the current proof-closure gate for the
``substitution-representability-proof`` predecessor obligation. The target
ties accepted finite certificate support, proof-readiness, and bridge
predecessor readiness coverage to explicit missing proof artifacts. It remains
blocked and does not promote certificate support into proof closure.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_bridge_predecessor_proof_readiness_coverage import (
    load_fixed_point_bridge_predecessor_proof_readiness_coverage,
    validate_fixed_point_bridge_predecessor_proof_readiness_coverage,
)
from autarkic_systems.fixed_point_substitution_representability_certificate import (
    load_fixed_point_substitution_representability_certificate,
    validate_fixed_point_substitution_representability_certificate,
)
from autarkic_systems.fixed_point_substitution_representability_proof_readiness import (
    load_fixed_point_substitution_representability_proof_readiness,
    validate_fixed_point_substitution_representability_proof_readiness,
)


DEFAULT_TARGET = Path(
    "claims/fixed_point_substitution_representability_proof_target.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_TARGET_ID = "as-fixed-point-substitution-representability-proof-target-v1"
REQUIRED_CASE_ID = "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY"
REQUIRED_CASE_KIND = "substitution-representability-proof"
REQUIRED_PROOF_TARGET_STATUS = "blocked-proof-closure-targeted"
REQUIRED_READINESS_STATUS = "blocked-certificate-ready-proof-open"
REQUIRED_COVERED_PREDECESSOR_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
)
REQUIRED_MISSING_CERTIFICATE_PREDECESSOR_COUNT = 0
REQUIRED_SUPPORT_SURFACE_COUNT = 5
REQUIRED_WITNESS_OUTPUT_CODE_LENGTH = 296
REQUIRED_MISSING_PROOF_ARTIFACTS = (
    "formal substitution representability derivation",
    "proof-rule derivation from certificate steps",
    "bridge-predecessor promotion rule",
)
REQUIRED_NON_CLAIMS = (
    "no substitution representability proof",
    "no diagonal-instance closure proof",
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no fixed-point construction proof",
    "no self-consistency theorem",
)
EXPECTED_PATHS = {
    "substitution_representability_certificate_path": (
        "claims/fixed_point_substitution_representability_certificate.json"
    ),
    "substitution_representability_readiness_path": (
        "claims/fixed_point_substitution_representability_proof_readiness.json"
    ),
    "bridge_predecessor_readiness_coverage_path": (
        "claims/fixed_point_bridge_predecessor_proof_readiness_coverage.json"
    ),
}
PROOF_PROMOTION_NON_CLAIMS = {
    "substitution representability proof",
    "diagonal-instance closure proof",
    "substitution graph correctness proof",
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "fixed-point construction proof",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityProofTargetManifest:
    """Loaded manifest for the substitution-representability proof target."""

    path: Path
    schema_version: int
    target_id: str
    reviewed_at: str
    purpose: str
    substitution_representability_certificate_path: str
    substitution_representability_readiness_path: str
    bridge_predecessor_readiness_coverage_path: str
    expected_case_id: str
    expected_case_kind: str
    expected_proof_target_status: str
    expected_readiness_status: str
    expected_certificate_count: int
    expected_certificate_step_count: int
    expected_covered_predecessor_case_kinds: tuple[str, ...]
    expected_missing_certificate_predecessor_count: int
    expected_support_surface_count: int
    expected_witness_output_code_length: int
    expected_missing_proof_artifacts: tuple[str, ...]
    expected_missing_proof_artifact_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityProofTargetValidation:
    """One validation result for the substitution proof target."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityProofTargetReport:
    """Validation report for the substitution-representability proof target."""

    manifest: FixedPointSubstitutionRepresentabilityProofTargetManifest
    substitution_representability_certificate_path: Path
    substitution_representability_readiness_path: Path
    bridge_predecessor_readiness_coverage_path: Path
    willard_map_path: Path
    certificate_accepted: bool
    readiness_accepted: bool
    bridge_predecessor_coverage_accepted: bool
    case_id: str
    case_kind: str
    proof_target_status: str
    readiness_status: str
    certificate_count: int
    certificate_step_count: int
    covered_predecessor_case_kinds: tuple[str, ...]
    missing_certificate_predecessor_count: int
    support_surface_count: int
    witness_output_code_length: int
    missing_proof_artifacts: tuple[str, ...]
    proof_boundary_preserved: bool
    results: tuple[
        FixedPointSubstitutionRepresentabilityProofTargetValidation,
        ...,
    ]

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
    proof_boundary_preserved: bool = False
    certificates: tuple[Any, ...] = ()
    readiness_entry: Any = None
    predecessor_entries: tuple[Any, ...] = ()


def load_fixed_point_substitution_representability_proof_target(
    path: Path | str = DEFAULT_TARGET,
) -> FixedPointSubstitutionRepresentabilityProofTargetManifest:
    """Load the substitution-representability proof-target manifest."""

    target_path = Path(path)
    data = json.loads(target_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionRepresentabilityProofTargetManifest(
        path=target_path,
        schema_version=_required_int(data, "schema_version"),
        target_id=_required_text(data, "target_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        substitution_representability_certificate_path=_required_text(
            data,
            "substitution_representability_certificate_path",
        ),
        substitution_representability_readiness_path=_required_text(
            data,
            "substitution_representability_readiness_path",
        ),
        bridge_predecessor_readiness_coverage_path=_required_text(
            data,
            "bridge_predecessor_readiness_coverage_path",
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
        expected_covered_predecessor_case_kinds=tuple(
            _required_text_list(data, "expected_covered_predecessor_case_kinds")
        ),
        expected_missing_certificate_predecessor_count=_required_int(
            data,
            "expected_missing_certificate_predecessor_count",
        ),
        expected_support_surface_count=_required_int(
            data,
            "expected_support_surface_count",
        ),
        expected_witness_output_code_length=_required_int(
            data,
            "expected_witness_output_code_length",
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


def validate_fixed_point_substitution_representability_proof_target(
    manifest: FixedPointSubstitutionRepresentabilityProofTargetManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionRepresentabilityProofTargetReport:
    """Validate the blocked proof-closure target for substitution."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointSubstitutionRepresentabilityProofTargetValidation] = [
        _accepted("manifest", f"loaded {manifest.target_id}")
    ]
    results.extend(_validate_manifest(manifest))

    certificate_report = _load_certificate(
        paths["substitution_representability_certificate_path"],
        checked_willard_map_path,
    )
    readiness_report = _load_readiness(
        paths["substitution_representability_readiness_path"],
        checked_willard_map_path,
    )
    coverage_report = _load_bridge_predecessor_coverage(
        paths["bridge_predecessor_readiness_coverage_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            certificate_report,
            readiness_report,
            coverage_report,
        )
    )

    certificate = _first_certificate(certificate_report)
    readiness_entry = getattr(readiness_report, "readiness_entry", None)
    coverage_entry = _coverage_entry_for_case(coverage_report, REQUIRED_CASE_KIND)
    case_id = str(getattr(readiness_entry, "case_id", ""))
    case_kind = str(getattr(readiness_entry, "case_kind", ""))
    readiness_status = str(getattr(readiness_entry, "readiness_status", ""))
    covered_predecessors = tuple(
        getattr(certificate, "covered_predecessor_case_kinds", ())
    )
    missing_predecessor_count = int(
        getattr(certificate, "missing_certificate_predecessor_count", 0)
    )
    support_surface_count = int(
        getattr(certificate, "frontier_support_surface_count", 0)
    )
    witness_output_length = int(
        getattr(certificate, "witness_output_code_length", 0)
    )
    proof_boundary_preserved = (
        bool(getattr(certificate_report, "accepted", False))
        and bool(getattr(readiness_report, "accepted", False))
        and bool(getattr(coverage_report, "accepted", False))
        and bool(getattr(certificate, "proof_boundary_preserved", False))
        and bool(getattr(readiness_report, "proof_boundary_preserved", False))
        and bool(getattr(coverage_report, "proof_boundary_preserved", False))
        and bool(getattr(coverage_entry, "accepted", False))
        and case_id == manifest.expected_case_id
        and case_kind == manifest.expected_case_kind
        and readiness_status == manifest.expected_readiness_status
    )

    results.extend(
        _validate_target(
            manifest,
            certificate_report,
            readiness_report,
            coverage_entry,
            case_id,
            case_kind,
            readiness_status,
            covered_predecessors,
            missing_predecessor_count,
            support_surface_count,
            witness_output_length,
            proof_boundary_preserved,
        )
    )

    return FixedPointSubstitutionRepresentabilityProofTargetReport(
        manifest=manifest,
        substitution_representability_certificate_path=paths[
            "substitution_representability_certificate_path"
        ],
        substitution_representability_readiness_path=paths[
            "substitution_representability_readiness_path"
        ],
        bridge_predecessor_readiness_coverage_path=paths[
            "bridge_predecessor_readiness_coverage_path"
        ],
        willard_map_path=checked_willard_map_path,
        certificate_accepted=bool(getattr(certificate_report, "accepted", False)),
        readiness_accepted=bool(getattr(readiness_report, "accepted", False)),
        bridge_predecessor_coverage_accepted=bool(
            getattr(coverage_report, "accepted", False)
        ),
        case_id=case_id,
        case_kind=case_kind,
        proof_target_status=manifest.expected_proof_target_status,
        readiness_status=readiness_status,
        certificate_count=int(getattr(certificate_report, "certificate_count", 0)),
        certificate_step_count=int(
            getattr(certificate_report, "certificate_step_count", 0)
        ),
        covered_predecessor_case_kinds=covered_predecessors,
        missing_certificate_predecessor_count=missing_predecessor_count,
        support_surface_count=support_surface_count,
        witness_output_code_length=witness_output_length,
        missing_proof_artifacts=manifest.expected_missing_proof_artifacts,
        proof_boundary_preserved=proof_boundary_preserved,
        results=tuple(results),
    )


def fixed_point_substitution_representability_proof_target_payload(
    report: FixedPointSubstitutionRepresentabilityProofTargetReport,
) -> dict[str, Any]:
    """Return a JSON-ready substitution proof-target payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "target_manifest": str(report.manifest.path),
        "target_id": report.manifest.target_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "substitution_representability_certificate_path": str(
            report.substitution_representability_certificate_path
        ),
        "substitution_representability_readiness_path": str(
            report.substitution_representability_readiness_path
        ),
        "bridge_predecessor_readiness_coverage_path": str(
            report.bridge_predecessor_readiness_coverage_path
        ),
        "willard_map": str(report.willard_map_path),
        "observed_certificate_accepted": report.certificate_accepted,
        "observed_readiness_accepted": report.readiness_accepted,
        "observed_bridge_predecessor_coverage_accepted": (
            report.bridge_predecessor_coverage_accepted
        ),
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "case_id": report.case_id,
        "case_kind": report.case_kind,
        "proof_target_status": report.proof_target_status,
        "readiness_status": report.readiness_status,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "covered_predecessor_case_kinds": list(
            report.covered_predecessor_case_kinds
        ),
        "missing_certificate_predecessor_count": (
            report.missing_certificate_predecessor_count
        ),
        "support_surface_count": report.support_surface_count,
        "witness_output_code_length": report.witness_output_code_length,
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


def format_fixed_point_substitution_representability_proof_target_report(
    report: FixedPointSubstitutionRepresentabilityProofTargetReport,
) -> str:
    """Format a concise text report for the blocked proof target."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point substitution representability proof target: {status}",
        f"Target: {report.manifest.target_id}",
        f"Construction case: {report.case_id}",
        f"Case kind: {report.case_kind}",
        f"Proof target status: {report.proof_target_status}",
        f"Readiness status: {report.readiness_status}",
        f"Certificate count: {report.certificate_count}",
        f"Certificate steps: {report.certificate_step_count}",
        "Covered predecessors: "
        + _joined_or_none(report.covered_predecessor_case_kinds),
        "Missing certificate predecessors: "
        + str(report.missing_certificate_predecessor_count),
        f"Support surfaces: {report.support_surface_count}",
        f"Witness output code length: {report.witness_output_code_length}",
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


def run_fixed_point_substitution_representability_proof_target_cli(
    argv: list[str] | None = None,
) -> int:
    """Run substitution-representability proof-target validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m autarkic_systems."
            "fixed_point_substitution_representability_proof_target"
        ),
        description=(
            "Validate the blocked proof target for the AS fixed-point "
            "substitution-representability proof case."
        ),
    )
    parser.add_argument(
        "--target",
        default=str(DEFAULT_TARGET),
        help="Path to the substitution-representability proof-target manifest.",
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

    manifest = load_fixed_point_substitution_representability_proof_target(
        args.target
    )
    report = validate_fixed_point_substitution_representability_proof_target(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_substitution_representability_proof_target_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_substitution_representability_proof_target_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointSubstitutionRepresentabilityProofTargetManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "substitution_representability_certificate_path": _resolve_path(
            manifest.path,
            manifest.substitution_representability_certificate_path,
        ),
        "substitution_representability_readiness_path": _resolve_path(
            manifest.path,
            manifest.substitution_representability_readiness_path,
        ),
        "bridge_predecessor_readiness_coverage_path": _resolve_path(
            manifest.path,
            manifest.bridge_predecessor_readiness_coverage_path,
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


def _load_certificate(path: Path, willard_map_path: Path) -> Any:
    """Load and validate substitution-representability certificate support."""

    try:
        manifest = load_fixed_point_substitution_representability_certificate(path)
        return validate_fixed_point_substitution_representability_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-substitution-representability-certificate-load",
            ),
        )


def _load_readiness(path: Path, willard_map_path: Path) -> Any:
    """Load and validate substitution-representability proof readiness."""

    try:
        manifest = load_fixed_point_substitution_representability_proof_readiness(
            path
        )
        return validate_fixed_point_substitution_representability_proof_readiness(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-substitution-representability-proof-readiness-load",
            ),
        )


def _load_bridge_predecessor_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate bridge predecessor proof-readiness coverage."""

    try:
        manifest = load_fixed_point_bridge_predecessor_proof_readiness_coverage(path)
        return validate_fixed_point_bridge_predecessor_proof_readiness_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-bridge-predecessor-proof-readiness-coverage-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointSubstitutionRepresentabilityProofTargetManifest,
) -> list[FixedPointSubstitutionRepresentabilityProofTargetValidation]:
    """Validate manifest-local constants and proof-boundary guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "target_id",
            manifest.target_id == REQUIRED_TARGET_ID,
            "target id matches",
            "unexpected target id",
        ),
        *[
            _check(
                key,
                getattr(manifest, key) == expected,
                f"{expected} referenced",
                f"expected {expected} but found {getattr(manifest, key)}",
            )
            for key, expected in EXPECTED_PATHS.items()
        ],
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
            manifest.expected_proof_target_status == REQUIRED_PROOF_TARGET_STATUS,
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
            "expected_covered_predecessor_case_kinds",
            (
                manifest.expected_covered_predecessor_case_kinds
                == REQUIRED_COVERED_PREDECESSOR_CASE_KINDS
            ),
            "covered predecessor cases match",
        ),
        _check(
            "expected_missing_certificate_predecessor_count",
            (
                manifest.expected_missing_certificate_predecessor_count
                == REQUIRED_MISSING_CERTIFICATE_PREDECESSOR_COUNT
            ),
            "missing predecessor certificate count matches",
        ),
        _check(
            "expected_support_surface_count",
            manifest.expected_support_surface_count == REQUIRED_SUPPORT_SURFACE_COUNT,
            "support surface count matches",
        ),
        _check(
            "expected_witness_output_code_length",
            (
                manifest.expected_witness_output_code_length
                == REQUIRED_WITNESS_OUTPUT_CODE_LENGTH
            ),
            "witness output code length matches",
        ),
        _check(
            "expected_missing_proof_artifacts",
            (
                manifest.expected_missing_proof_artifacts
                == REQUIRED_MISSING_PROOF_ARTIFACTS
            ),
            "missing proof artifacts match",
            "missing proof artifact mismatch",
        ),
        _check(
            "expected_missing_proof_artifact_count",
            (
                manifest.expected_missing_proof_artifact_count
                == len(REQUIRED_MISSING_PROOF_ARTIFACTS)
            ),
            "missing proof artifact count matches",
            "missing proof artifact count mismatch",
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
        _check("next_as_action", bool(manifest.next_as_action), "next action present"),
    ]


def _validate_dependencies(
    certificate_report: Any,
    readiness_report: Any,
    coverage_report: Any,
) -> list[FixedPointSubstitutionRepresentabilityProofTargetValidation]:
    """Validate that dependency reports accepted before target derivation."""

    return [
        _check(
            "substitution_representability_certificate",
            bool(getattr(certificate_report, "accepted", False)),
            "certificate accepted",
            "certificate rejected: "
            + _joined_or_none(getattr(certificate_report, "failed_subjects", ())),
        ),
        _check(
            "substitution_representability_readiness",
            bool(getattr(readiness_report, "accepted", False)),
            "readiness accepted",
            "readiness rejected: "
            + _joined_or_none(getattr(readiness_report, "failed_subjects", ())),
        ),
        _check(
            "bridge_predecessor_readiness_coverage",
            bool(getattr(coverage_report, "accepted", False)),
            "bridge predecessor coverage accepted",
            "bridge predecessor coverage rejected: "
            + _joined_or_none(getattr(coverage_report, "failed_subjects", ())),
        ),
    ]


def _validate_target(
    manifest: FixedPointSubstitutionRepresentabilityProofTargetManifest,
    certificate_report: Any,
    readiness_report: Any,
    coverage_entry: Any,
    case_id: str,
    case_kind: str,
    readiness_status: str,
    covered_predecessors: tuple[str, ...],
    missing_predecessor_count: int,
    support_surface_count: int,
    witness_output_length: int,
    proof_boundary_preserved: bool,
) -> list[FixedPointSubstitutionRepresentabilityProofTargetValidation]:
    """Validate observed target facts against manifest expectations."""

    return [
        _check("case_id", case_id == manifest.expected_case_id, "case id matches"),
        _check(
            "case_kind",
            case_kind == manifest.expected_case_kind,
            "case kind matches",
        ),
        _check(
            "proof_target_status",
            manifest.expected_proof_target_status == REQUIRED_PROOF_TARGET_STATUS,
            "proof target status matches",
        ),
        _check(
            "readiness_status",
            readiness_status == manifest.expected_readiness_status,
            "readiness status matches",
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
            "covered_predecessor_case_kinds",
            covered_predecessors
            == manifest.expected_covered_predecessor_case_kinds,
            "covered predecessor cases match",
            "covered predecessor case mismatch",
        ),
        _check(
            "missing_certificate_predecessor_count",
            (
                missing_predecessor_count
                == manifest.expected_missing_certificate_predecessor_count
            ),
            "missing predecessor certificate count matches",
            "missing predecessor certificate count mismatch",
        ),
        _check(
            "support_surface_count",
            support_surface_count == manifest.expected_support_surface_count,
            "support surface count matches",
            "support surface count mismatch",
        ),
        _check(
            "witness_output_code_length",
            witness_output_length == manifest.expected_witness_output_code_length,
            "witness output code length matches",
            "witness output length mismatch",
        ),
        _check(
            "bridge_predecessor_coverage_entry",
            bool(getattr(coverage_entry, "accepted", False)),
            "bridge predecessor coverage includes accepted substitution target",
            "bridge predecessor coverage missing substitution target",
        ),
        _check(
            "missing_proof_artifacts",
            (
                manifest.expected_missing_proof_artifacts
                == REQUIRED_MISSING_PROOF_ARTIFACTS
                and manifest.expected_missing_proof_artifact_count
                == len(REQUIRED_MISSING_PROOF_ARTIFACTS)
            ),
            "missing proof artifacts match",
            "missing proof artifact mismatch",
        ),
        _check(
            "proof_closure",
            manifest.expected_missing_proof_artifact_count > 0,
            "proof closure remains blocked",
            "proof closure unexpectedly ready",
        ),
        _check(
            "proof_boundary",
            proof_boundary_preserved
            and bool(getattr(readiness_report, "proof_boundary_preserved", False)),
            "proof boundary preserved",
        ),
    ]


def _first_certificate(certificate_report: Any) -> Any:
    """Return the first derived certificate object or an empty shim."""

    certificates = tuple(getattr(certificate_report, "certificates", ()))
    if certificates:
        return certificates[0]
    return _DependencyFailure(False, ())


def _coverage_entry_for_case(coverage_report: Any, case_kind: str) -> Any:
    """Return a bridge predecessor coverage entry for the requested case."""

    for entry in tuple(getattr(coverage_report, "predecessor_entries", ())):
        if getattr(entry, "case_kind", "") == case_kind:
            return entry
    return _DependencyFailure(False, ())


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
) -> FixedPointSubstitutionRepresentabilityProofTargetValidation:
    """Return an accepted validation result."""

    return FixedPointSubstitutionRepresentabilityProofTargetValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointSubstitutionRepresentabilityProofTargetValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointSubstitutionRepresentabilityProofTargetValidation(
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
        "substitution_representability_certificate",
        "substitution_representability_readiness",
        "bridge_predecessor_readiness_coverage",
    }:
        return "fixed-point-substitution-representability-proof-target-dependencies"
    if subject in {"missing_proof_artifacts", "expected_missing_proof_artifacts"}:
        return "fixed-point-substitution-representability-proof-target-artifacts"
    if subject in {"certificate_count", "certificate_step_count"}:
        return "fixed-point-substitution-representability-proof-target-certificate"
    if subject in {
        "case_id",
        "case_kind",
        "proof_target_status",
        "readiness_status",
        "bridge_predecessor_coverage_entry",
    }:
        return "fixed-point-substitution-representability-proof-target-case"
    if subject in {
        "covered_predecessor_case_kinds",
        "missing_certificate_predecessor_count",
    }:
        return (
            "fixed-point-substitution-representability-proof-target-predecessors"
        )
    if subject == "support_surface_count":
        return "fixed-point-substitution-representability-proof-target-support"
    if subject == "witness_output_code_length":
        return "fixed-point-substitution-representability-proof-target-witness"
    if subject in {"proof_boundary", "non_claims", "non_claim_promotion_boundary"}:
        return "fixed-point-substitution-representability-proof-target-boundary"
    if subject.startswith("expected_") or subject in {
        "target_id",
        "schema_version",
        "next_as_action",
    }:
        return "fixed-point-substitution-representability-proof-target-manifest"
    return (
        "fixed-point-substitution-representability-proof-target-"
        + subject.replace("_", "-")
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_substitution_representability_proof_target_cli()


if __name__ == "__main__":
    raise SystemExit(main())
