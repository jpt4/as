"""Finite certificate support for fixed-point substitution representability.

ADR-0309 composes the compact substitution-representability frontier status
with the available predecessor certificate coverage from ADR-0308. The result
is a certificate-support surface: it records that the current finite support is
coherent and that both predecessor proof cases have available certificate
support, while preserving that substitution representability remains an open
proof case.
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
from autarkic_systems.fixed_point_substitution_representability_frontier_status import (
    load_fixed_point_substitution_representability_frontier_status,
    validate_fixed_point_substitution_representability_frontier_status,
)


DEFAULT_CERTIFICATE = Path(
    "claims/fixed_point_substitution_representability_certificate.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CERTIFICATE_STEP_IDS = (
    "accept-frontier-status",
    "accept-available-predecessor-coverage",
    "check-construction-case-open",
    "check-predecessor-certificate-coverage",
    "check-frontier-support-surfaces",
    "check-witness-output-code-length",
    "preserve-open-proof-boundary",
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
    "substitution_representability_frontier_status_path": (
        "claims/fixed_point_substitution_representability_frontier_status.json"
    ),
    "available_predecessor_certificate_coverage_path": (
        "claims/fixed_point_available_predecessor_certificate_coverage.json"
    ),
}
REQUIRED_SELECTED_CASE_KIND = "substitution-representability-proof"
REQUIRED_CONSTRUCTION_CASE_ID = (
    "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-REPRESENTABILITY"
)
REQUIRED_CONSTRUCTION_CASE_STATUS = "proof-case-open"
REQUIRED_CERTIFICATE_STATUS = "accepted-finite-certificate-not-proof"


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityCertificateManifest:
    """Loaded manifest for substitution-representability certificate support."""

    path: Path
    schema_version: int
    certificate_set_id: str
    reviewed_at: str
    purpose: str
    substitution_representability_frontier_status_path: str
    available_predecessor_certificate_coverage_path: str
    expected_certificate_count: int
    expected_step_ids: tuple[str, ...]
    expected_selected_case_kind: str
    expected_construction_case_id: str
    expected_covered_predecessor_case_kinds: tuple[str, ...]
    expected_missing_certificate_predecessor_count: int
    expected_frontier_support_surface_count: int
    expected_witness_output_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityCertificateStep:
    """One checked finite certificate-support step."""

    step_id: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityCertificate:
    """One finite certificate support object for substitution representability."""

    certificate_id: str
    construction_case_id: str
    selected_case_kind: str
    construction_case_status: str
    certificate_status: str
    covered_predecessor_case_kinds: tuple[str, ...]
    missing_certificate_predecessor_count: int
    open_proof_blocker_case_kinds: tuple[str, ...]
    frontier_status_accepted: bool
    available_coverage_accepted: bool
    frontier_support_surface_count: int
    accepted_frontier_support_surface_count: int
    witness_output_code_length: int
    proof_boundary_preserved: bool
    steps: tuple[FixedPointSubstitutionRepresentabilityCertificateStep, ...]

    @property
    def all_steps_accepted(self) -> bool:
        """Return whether every named certificate step accepted."""

        return all(step.accepted for step in self.steps)

    @property
    def accepted(self) -> bool:
        """Return whether this certificate-support object accepted."""

        return (
            self.certificate_status == REQUIRED_CERTIFICATE_STATUS
            and self.construction_case_id == REQUIRED_CONSTRUCTION_CASE_ID
            and self.selected_case_kind == REQUIRED_SELECTED_CASE_KIND
            and self.construction_case_status == REQUIRED_CONSTRUCTION_CASE_STATUS
            and self.frontier_status_accepted
            and self.available_coverage_accepted
            and self.missing_certificate_predecessor_count == 0
            and self.frontier_support_surface_count == 5
            and self.accepted_frontier_support_surface_count == 5
            and self.witness_output_code_length == 296
            and self.proof_boundary_preserved
            and self.all_steps_accepted
        )


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityCertificateValidation:
    """One validation result for the certificate support surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionRepresentabilityCertificateReport:
    """Validation report for substitution-representability certificate support."""

    manifest: FixedPointSubstitutionRepresentabilityCertificateManifest
    substitution_representability_frontier_status_path: Path
    available_predecessor_certificate_coverage_path: Path
    willard_map_path: Path
    frontier_status_accepted: bool
    available_coverage_accepted: bool
    certificates: tuple[FixedPointSubstitutionRepresentabilityCertificate, ...]
    results: tuple[
        FixedPointSubstitutionRepresentabilityCertificateValidation, ...
    ]

    @property
    def accepted(self) -> bool:
        """Return whether every validation result accepted."""

        return all(result.accepted for result in self.results)

    @property
    def certificate_count(self) -> int:
        """Return the number of derived certificate support objects."""

        return len(self.certificates)

    @property
    def certificate_step_count(self) -> int:
        """Return the total number of checked certificate steps."""

        return sum(len(certificate.steps) for certificate in self.certificates)

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
    construction_case_id: str = ""
    construction_case_kind: str = ""
    construction_case_status: str = ""
    support_surface_count: int = 0
    support_surfaces: tuple[Any, ...] = ()
    coverage_entries: tuple[Any, ...] = ()
    proof_boundary_preserved: bool = False


def load_fixed_point_substitution_representability_certificate(
    path: Path | str = DEFAULT_CERTIFICATE,
) -> FixedPointSubstitutionRepresentabilityCertificateManifest:
    """Load the substitution-representability certificate manifest."""

    certificate_path = Path(path)
    data = json.loads(certificate_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionRepresentabilityCertificateManifest(
        path=certificate_path,
        schema_version=_required_int(data, "schema_version"),
        certificate_set_id=_required_text(data, "certificate_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        substitution_representability_frontier_status_path=_required_text(
            data,
            "substitution_representability_frontier_status_path",
        ),
        available_predecessor_certificate_coverage_path=_required_text(
            data,
            "available_predecessor_certificate_coverage_path",
        ),
        expected_certificate_count=_required_int(
            data,
            "expected_certificate_count",
        ),
        expected_step_ids=tuple(_required_text_list(data, "expected_step_ids")),
        expected_selected_case_kind=_required_text(
            data,
            "expected_selected_case_kind",
        ),
        expected_construction_case_id=_required_text(
            data,
            "expected_construction_case_id",
        ),
        expected_covered_predecessor_case_kinds=tuple(
            _required_text_list(data, "expected_covered_predecessor_case_kinds")
        ),
        expected_missing_certificate_predecessor_count=_required_int(
            data,
            "expected_missing_certificate_predecessor_count",
        ),
        expected_frontier_support_surface_count=_required_int(
            data,
            "expected_frontier_support_surface_count",
        ),
        expected_witness_output_code_length=_required_int(
            data,
            "expected_witness_output_code_length",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


def validate_fixed_point_substitution_representability_certificate(
    manifest: FixedPointSubstitutionRepresentabilityCertificateManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionRepresentabilityCertificateReport:
    """Validate substitution-representability finite certificate support."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointSubstitutionRepresentabilityCertificateValidation] = [
        _accepted("manifest", f"loaded {manifest.certificate_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    frontier_report = _load_frontier_status(
        paths["substitution_representability_frontier_status_path"]
    )
    coverage_report = _load_available_coverage(
        paths["available_predecessor_certificate_coverage_path"],
        checked_willard_map_path,
    )
    results.extend(_validate_dependencies(frontier_report, coverage_report))

    certificate = _derive_certificate(manifest, frontier_report, coverage_report)
    results.extend(_validate_certificate(manifest, certificate))

    return FixedPointSubstitutionRepresentabilityCertificateReport(
        manifest=manifest,
        substitution_representability_frontier_status_path=paths[
            "substitution_representability_frontier_status_path"
        ],
        available_predecessor_certificate_coverage_path=paths[
            "available_predecessor_certificate_coverage_path"
        ],
        willard_map_path=checked_willard_map_path,
        frontier_status_accepted=frontier_report.accepted,
        available_coverage_accepted=coverage_report.accepted,
        certificates=(certificate,),
        results=tuple(results),
    )


def fixed_point_substitution_representability_certificate_payload(
    report: FixedPointSubstitutionRepresentabilityCertificateReport,
) -> dict[str, Any]:
    """Return a JSON-ready substitution-representability certificate payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "certificate_manifest": str(report.manifest.path),
        "certificate_set_id": report.manifest.certificate_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "substitution_representability_frontier_status_path": str(
            report.substitution_representability_frontier_status_path
        ),
        "available_predecessor_certificate_coverage_path": str(
            report.available_predecessor_certificate_coverage_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_certificate_count": report.manifest.expected_certificate_count,
        "expected_step_ids": list(report.manifest.expected_step_ids),
        "expected_selected_case_kind": (
            report.manifest.expected_selected_case_kind
        ),
        "expected_construction_case_id": (
            report.manifest.expected_construction_case_id
        ),
        "expected_covered_predecessor_case_kinds": list(
            report.manifest.expected_covered_predecessor_case_kinds
        ),
        "expected_missing_certificate_predecessor_count": (
            report.manifest.expected_missing_certificate_predecessor_count
        ),
        "expected_frontier_support_surface_count": (
            report.manifest.expected_frontier_support_surface_count
        ),
        "expected_witness_output_code_length": (
            report.manifest.expected_witness_output_code_length
        ),
        "observed_frontier_status_accepted": report.frontier_status_accepted,
        "observed_available_coverage_accepted": (
            report.available_coverage_accepted
        ),
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "certificates": [
            _certificate_payload(certificate)
            for certificate in report.certificates
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


def format_fixed_point_substitution_representability_certificate_report(
    report: FixedPointSubstitutionRepresentabilityCertificateReport,
) -> str:
    """Format a concise substitution-representability certificate report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point substitution representability certificate: {status}",
        f"Certificate set: {report.manifest.certificate_set_id}",
        f"Certificates: {report.certificate_count}",
        f"Certificate steps: {report.certificate_step_count}",
        "Frontier status accepted: "
        + str(report.frontier_status_accepted).lower(),
        "Available predecessor coverage accepted: "
        + str(report.available_coverage_accepted).lower(),
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for certificate in report.certificates:
        lines.append(
            f"{certificate.selected_case_kind}: {certificate.certificate_status} "
            f"(covered predecessors: "
            f"{_joined_or_none(certificate.covered_predecessor_case_kinds)}; "
            f"missing certificate predecessors: "
            f"{certificate.missing_certificate_predecessor_count}; "
            f"support surfaces: "
            f"{certificate.accepted_frontier_support_surface_count}/"
            f"{certificate.frontier_support_surface_count}; "
            f"witness output length: "
            f"{certificate.witness_output_code_length}; "
            f"open proof blockers: "
            f"{_joined_or_none(certificate.open_proof_blocker_case_kinds)})"
        )
        for step in certificate.steps:
            step_status = "accepted" if step.accepted else "rejected"
            lines.append(f"{step.step_id}: {step_status} ({step.detail})")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_substitution_representability_certificate_cli(
    argv: list[str] | None = None,
) -> int:
    """Run substitution-representability certificate validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_substitution_representability_certificate"
        ),
        description=(
            "Validate finite certificate support for the AS fixed-point "
            "substitution-representability construction case."
        ),
    )
    parser.add_argument(
        "--certificate",
        default=str(DEFAULT_CERTIFICATE),
        help="Path to the substitution-representability certificate manifest.",
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

    manifest = load_fixed_point_substitution_representability_certificate(
        args.certificate
    )
    report = validate_fixed_point_substitution_representability_certificate(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_substitution_representability_certificate_payload(
                    report
                ),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_substitution_representability_certificate_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointSubstitutionRepresentabilityCertificateManifest,
) -> dict[str, Path]:
    """Return dependency paths resolved relative to the manifest location."""

    return {
        "substitution_representability_frontier_status_path": _resolve_path(
            manifest.path,
            manifest.substitution_representability_frontier_status_path,
        ),
        "available_predecessor_certificate_coverage_path": _resolve_path(
            manifest.path,
            manifest.available_predecessor_certificate_coverage_path,
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


def _load_frontier_status(path: Path) -> Any:
    """Load and validate the substitution-representability frontier status."""

    try:
        manifest = load_fixed_point_substitution_representability_frontier_status(
            path
        )
        return validate_fixed_point_substitution_representability_frontier_status(
            manifest
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return _DependencyFailure(
            accepted=False,
            failed_subjects=("fixed-point-substitution-representability-status-load",),
            construction_case_kind=REQUIRED_SELECTED_CASE_KIND,
        )


def _load_available_coverage(path: Path, willard_map_path: Path) -> Any:
    """Load and validate available predecessor certificate coverage."""

    try:
        manifest = load_fixed_point_available_predecessor_certificate_coverage(path)
        return validate_fixed_point_available_predecessor_certificate_coverage(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        return _DependencyFailure(
            accepted=False,
            failed_subjects=(
                "fixed-point-available-predecessor-certificate-coverage-load",
            ),
        )


def _validate_manifest(
    manifest: FixedPointSubstitutionRepresentabilityCertificateManifest,
) -> list[FixedPointSubstitutionRepresentabilityCertificateValidation]:
    """Validate manifest-local constants and non-claim guardrails."""

    return [
        _check("schema_version", manifest.schema_version == 1, "schema version 1"),
        _check(
            "certificate_set_id",
            (
                manifest.certificate_set_id
                == "as-fixed-point-substitution-representability-certificate-v1"
            ),
            "certificate set id matches",
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
            "expected_certificate_count",
            manifest.expected_certificate_count == 1,
            "one certificate",
        ),
        _check(
            "expected_step_ids",
            manifest.expected_step_ids == REQUIRED_CERTIFICATE_STEP_IDS,
            "step ids match",
            "step id mismatch",
        ),
        _check(
            "expected_selected_case_kind",
            manifest.expected_selected_case_kind == REQUIRED_SELECTED_CASE_KIND,
            "selected case kind matches",
        ),
        _check(
            "expected_construction_case_id",
            manifest.expected_construction_case_id == REQUIRED_CONSTRUCTION_CASE_ID,
            "construction case id matches",
        ),
        _check(
            "expected_covered_predecessor_case_kinds",
            manifest.expected_covered_predecessor_case_kinds
            == (
                "diagonal-instance-closure",
                "substitution-graph-correctness-proof",
            ),
            "covered predecessor subjects match",
        ),
        _check(
            "expected_missing_certificate_predecessor_count",
            manifest.expected_missing_certificate_predecessor_count == 0,
            "no missing predecessor certificates",
        ),
        _check(
            "expected_frontier_support_surface_count",
            manifest.expected_frontier_support_surface_count == 5,
            "five frontier support surfaces",
        ),
        _check(
            "expected_witness_output_code_length",
            manifest.expected_witness_output_code_length == 296,
            "296-token witness output",
        ),
        _check(
            "non_claims",
            manifest.non_claims == REQUIRED_NON_CLAIMS,
            "all non-claims preserved",
        ),
    ]


def _validate_dependencies(
    frontier_report: Any,
    coverage_report: Any,
) -> list[FixedPointSubstitutionRepresentabilityCertificateValidation]:
    """Validate that dependency reports accepted before deriving a certificate."""

    return [
        _check(
            "substitution_representability_frontier_status",
            frontier_report.accepted,
            "frontier status accepted",
            "frontier status rejected: "
            + _joined_or_none(getattr(frontier_report, "failed_subjects", ())),
        ),
        _check(
            "available_predecessor_certificate_coverage",
            coverage_report.accepted,
            "available predecessor coverage accepted",
            "available predecessor coverage rejected: "
            + _joined_or_none(getattr(coverage_report, "failed_subjects", ())),
        ),
    ]


def _derive_certificate(
    manifest: FixedPointSubstitutionRepresentabilityCertificateManifest,
    frontier_report: Any,
    coverage_report: Any,
) -> FixedPointSubstitutionRepresentabilityCertificate:
    """Derive the single finite support certificate from dependency reports."""

    coverage_entry = _coverage_entry_for(
        coverage_report,
        manifest.expected_selected_case_kind,
    )
    covered_predecessors = tuple(
        getattr(coverage_entry, "certificate_covered_predecessor_case_kinds", ())
    )
    missing_predecessor_count = int(
        getattr(coverage_entry, "missing_certificate_predecessor_count", 0)
    )
    open_blockers = tuple(
        getattr(coverage_entry, "open_proof_blocker_case_kinds", ())
    )
    support_surfaces = tuple(getattr(frontier_report, "support_surfaces", ()))
    accepted_support_count = sum(
        1 for surface in support_surfaces if getattr(surface, "accepted", False)
    )
    witness_output_length = _witness_output_code_length(support_surfaces)
    proof_boundary_preserved = (
        getattr(frontier_report, "frontier_status", "") == "blocked"
        and getattr(frontier_report, "frontier_blocked_by", "")
        == REQUIRED_SELECTED_CASE_KIND
        and getattr(frontier_report, "construction_case_status", "")
        == REQUIRED_CONSTRUCTION_CASE_STATUS
        and bool(open_blockers)
        and getattr(coverage_entry, "proof_boundary_preserved", False)
    )

    steps = (
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "accept-frontier-status",
            bool(getattr(frontier_report, "accepted", False)),
            "frontier status accepted",
        ),
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "accept-available-predecessor-coverage",
            bool(getattr(coverage_report, "accepted", False)),
            "available predecessor coverage accepted",
        ),
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "check-construction-case-open",
            (
                getattr(frontier_report, "construction_case_id", "")
                == manifest.expected_construction_case_id
                and getattr(frontier_report, "construction_case_kind", "")
                == manifest.expected_selected_case_kind
                and getattr(frontier_report, "construction_case_status", "")
                == REQUIRED_CONSTRUCTION_CASE_STATUS
            ),
            "construction case remains open",
        ),
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "check-predecessor-certificate-coverage",
            (
                covered_predecessors
                == manifest.expected_covered_predecessor_case_kinds
                and missing_predecessor_count
                == manifest.expected_missing_certificate_predecessor_count
            ),
            "predecessor certificate coverage matches",
        ),
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "check-frontier-support-surfaces",
            (
                len(support_surfaces)
                == manifest.expected_frontier_support_surface_count
                and accepted_support_count
                == manifest.expected_frontier_support_surface_count
            ),
            "frontier support surfaces accepted",
        ),
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "check-witness-output-code-length",
            witness_output_length == manifest.expected_witness_output_code_length,
            "witness output length matches",
        ),
        FixedPointSubstitutionRepresentabilityCertificateStep(
            "preserve-open-proof-boundary",
            proof_boundary_preserved,
            "proof boundary preserved",
        ),
    )

    return FixedPointSubstitutionRepresentabilityCertificate(
        certificate_id="AS-FIXED-POINT-SUBSTITUTION-REPRESENTABILITY-CERTIFICATE",
        construction_case_id=getattr(frontier_report, "construction_case_id", ""),
        selected_case_kind=getattr(frontier_report, "construction_case_kind", ""),
        construction_case_status=getattr(
            frontier_report,
            "construction_case_status",
            "",
        ),
        certificate_status=REQUIRED_CERTIFICATE_STATUS,
        covered_predecessor_case_kinds=covered_predecessors,
        missing_certificate_predecessor_count=missing_predecessor_count,
        open_proof_blocker_case_kinds=open_blockers,
        frontier_status_accepted=bool(getattr(frontier_report, "accepted", False)),
        available_coverage_accepted=bool(getattr(coverage_report, "accepted", False)),
        frontier_support_surface_count=len(support_surfaces),
        accepted_frontier_support_surface_count=accepted_support_count,
        witness_output_code_length=witness_output_length,
        proof_boundary_preserved=proof_boundary_preserved,
        steps=steps,
    )


def _coverage_entry_for(coverage_report: Any, case_kind: str) -> Any:
    """Return the available-coverage entry for a deferred case kind."""

    for entry in getattr(coverage_report, "coverage_entries", ()):
        if getattr(entry, "deferred_case_kind", "") == case_kind:
            return entry
    return None


def _witness_output_code_length(support_surfaces: tuple[Any, ...]) -> int:
    """Return the observed witness output code length from support facts."""

    for surface in support_surfaces:
        if getattr(surface, "subject", "") != "substitution_witness_bridge":
            continue
        facts = getattr(surface, "facts", {})
        value = facts.get("expected_witness_output_code_length")
        if isinstance(value, int):
            return value
    return 0


def _validate_certificate(
    manifest: FixedPointSubstitutionRepresentabilityCertificateManifest,
    certificate: FixedPointSubstitutionRepresentabilityCertificate,
) -> list[FixedPointSubstitutionRepresentabilityCertificateValidation]:
    """Validate the derived certificate against manifest expectations."""

    return [
        _check(
            "certificate_count",
            manifest.expected_certificate_count == 1,
            "certificate count matches",
        ),
        _check(
            "certificate_step_ids",
            tuple(step.step_id for step in certificate.steps)
            == manifest.expected_step_ids,
            "step ids match",
            "step id mismatch",
        ),
        _check(
            "certificate_steps",
            certificate.all_steps_accepted,
            "all certificate steps accepted",
            "one or more certificate steps rejected",
        ),
        _check(
            "selected_case_kind",
            certificate.selected_case_kind == manifest.expected_selected_case_kind,
            "selected case kind matches",
        ),
        _check(
            "construction_case_id",
            certificate.construction_case_id == manifest.expected_construction_case_id,
            "construction case id matches",
        ),
        _check(
            "covered_predecessor_case_kinds",
            certificate.covered_predecessor_case_kinds
            == manifest.expected_covered_predecessor_case_kinds,
            "covered predecessor case kinds match",
        ),
        _check(
            "missing_certificate_predecessor_count",
            certificate.missing_certificate_predecessor_count
            == manifest.expected_missing_certificate_predecessor_count,
            "missing certificate predecessor count matches",
        ),
        _check(
            "frontier_support_surface_count",
            certificate.frontier_support_surface_count
            == manifest.expected_frontier_support_surface_count
            and certificate.accepted_frontier_support_surface_count
            == manifest.expected_frontier_support_surface_count,
            "frontier support surface count matches",
        ),
        _check(
            "witness_output_code_length",
            certificate.witness_output_code_length
            == manifest.expected_witness_output_code_length,
            "witness output code length matches",
        ),
        _check(
            "proof_boundary",
            certificate.proof_boundary_preserved,
            "proof boundary preserved",
        ),
        _check(
            "certificate",
            certificate.accepted,
            "certificate accepted",
            "certificate rejected",
        ),
    ]


def _certificate_payload(
    certificate: FixedPointSubstitutionRepresentabilityCertificate,
) -> dict[str, Any]:
    """Return a JSON-ready certificate support object."""

    return {
        "certificate_id": certificate.certificate_id,
        "construction_case_id": certificate.construction_case_id,
        "selected_case_kind": certificate.selected_case_kind,
        "construction_case_status": certificate.construction_case_status,
        "certificate_status": certificate.certificate_status,
        "covered_predecessor_case_kinds": list(
            certificate.covered_predecessor_case_kinds
        ),
        "missing_certificate_predecessor_count": (
            certificate.missing_certificate_predecessor_count
        ),
        "open_proof_blocker_case_kinds": list(
            certificate.open_proof_blocker_case_kinds
        ),
        "observed_frontier_status_accepted": (
            certificate.frontier_status_accepted
        ),
        "observed_available_coverage_accepted": (
            certificate.available_coverage_accepted
        ),
        "observed_frontier_support_surface_count": (
            certificate.frontier_support_surface_count
        ),
        "observed_accepted_frontier_support_surface_count": (
            certificate.accepted_frontier_support_surface_count
        ),
        "observed_witness_output_code_length": (
            certificate.witness_output_code_length
        ),
        "observed_proof_boundary_preserved": (
            certificate.proof_boundary_preserved
        ),
        "all_steps_accepted": certificate.all_steps_accepted,
        "accepted": certificate.accepted,
        "steps": [
            {
                "step_id": step.step_id,
                "accepted": step.accepted,
                "detail": step.detail,
            }
            for step in certificate.steps
        ],
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
) -> FixedPointSubstitutionRepresentabilityCertificateValidation:
    """Return an accepted validation result."""

    return FixedPointSubstitutionRepresentabilityCertificateValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _check(
    subject: str,
    condition: bool,
    accepted_detail: str,
    rejected_detail: str | None = None,
) -> FixedPointSubstitutionRepresentabilityCertificateValidation:
    """Return a validation result from a boolean condition."""

    return FixedPointSubstitutionRepresentabilityCertificateValidation(
        subject=subject,
        accepted=condition,
        detail=accepted_detail if condition else rejected_detail or accepted_detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    """Map verbose result subjects to stable failure subjects."""

    if subject in {"expected_step_ids", "certificate_step_ids"}:
        return "fixed-point-substitution-representability-certificate-steps"
    if subject.startswith("expected_") or subject in {
        "certificate_set_id",
        "schema_version",
    }:
        return "fixed-point-substitution-representability-certificate-manifest"
    if subject == "substitution_representability_frontier_status":
        return "fixed-point-substitution-representability-certificate-frontier"
    if subject == "available_predecessor_certificate_coverage":
        return "fixed-point-substitution-representability-certificate-coverage"
    if subject in {
        "covered_predecessor_case_kinds",
        "missing_certificate_predecessor_count",
    }:
        return "fixed-point-substitution-representability-certificate-predecessors"
    if subject == "proof_boundary":
        return "fixed-point-substitution-representability-certificate-boundary"
    return f"fixed-point-substitution-representability-certificate-{subject.replace('_', '-')}"


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    """Return a comma-joined list or ``none`` for empty sequences."""

    if not values:
        return "none"
    return ", ".join(values)


def main() -> int:
    """Module entrypoint."""

    return run_fixed_point_substitution_representability_certificate_cli()


if __name__ == "__main__":
    raise SystemExit(main())
