"""Finite certificate support for the diagonal-instance-closure root.

The current fixed-point frontier selector marks ``diagonal-instance-closure``
as an open root obligation. This module wraps the accepted selector, closure,
and candidate-surface reports in one compact certificate support object. It is
not a proof that the construction case is closed and does not prove a
fixed-point equation or self-consistency theorem.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_diagonal_instance_candidate_surface import (
    load_fixed_point_diagonal_instance_candidate_surface,
    validate_fixed_point_diagonal_instance_candidate_surface,
)
from autarkic_systems.fixed_point_diagonal_instance_closure import (
    load_fixed_point_diagonal_instance_closure,
    validate_fixed_point_diagonal_instance_closure,
)
from autarkic_systems.fixed_point_frontier_selector import (
    load_fixed_point_frontier_selector,
    validate_fixed_point_frontier_selector,
)


DEFAULT_CERTIFICATE = Path(
    "claims/fixed_point_diagonal_instance_closure_certificate.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CERTIFICATE_STEP_IDS = (
    "select-open-root-obligation",
    "accept-closure-report",
    "accept-candidate-surface",
    "check-closed-diagonal-instance",
    "check-codebook-roundtrip",
    "match-candidate-to-closure",
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
    "diagonal_instance_closure_path": (
        "claims/fixed_point_diagonal_instance_closure.json"
    ),
    "diagonal_instance_candidate_surface_path": (
        "claims/fixed_point_diagonal_instance_candidate_surface.json"
    ),
    "frontier_selector_path": "claims/fixed_point_frontier_selector.json",
}
REQUIRED_SELECTED_CASE_KIND = "diagonal-instance-closure"
REQUIRED_CONSTRUCTION_CASE_ID = (
    "AS-FIXED-POINT-CONSTRUCTION-DIAGONAL-INSTANCE-CLOSURE"
)


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureCertificateManifest:
    """Loaded manifest for diagonal-instance closure certificate support."""

    path: Path
    schema_version: int
    certificate_set_id: str
    reviewed_at: str
    purpose: str
    diagonal_instance_closure_path: str
    diagonal_instance_candidate_surface_path: str
    frontier_selector_path: str
    expected_certificate_count: int
    expected_step_ids: tuple[str, ...]
    expected_selected_case_kind: str
    expected_candidate_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureCertificateStep:
    """One checked finite certificate-support step."""

    step_id: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureCertificate:
    """One finite certificate support object for the closure root."""

    certificate_id: str
    construction_case_id: str
    selected_case_kind: str
    target_id: str
    closure_id: str
    candidate_id: str
    certificate_status: str
    candidate_code_length: int
    selector_accepts_root: bool
    closure_accepted: bool
    candidate_surface_accepted: bool
    diagonal_instance_closed: bool
    codebook_roundtrip: bool
    candidate_matches_closure: bool
    proof_boundary_preserved: bool
    steps: tuple[FixedPointDiagonalInstanceClosureCertificateStep, ...]

    @property
    def all_steps_accepted(self) -> bool:
        """Return whether all named certificate steps accepted."""

        return all(step.accepted for step in self.steps)

    @property
    def accepted(self) -> bool:
        """Return whether this finite certificate support object accepted."""

        return (
            self.certificate_status == "accepted-finite-certificate-not-proof"
            and self.selector_accepts_root
            and self.closure_accepted
            and self.candidate_surface_accepted
            and self.diagonal_instance_closed
            and self.codebook_roundtrip
            and self.candidate_matches_closure
            and self.proof_boundary_preserved
            and self.all_steps_accepted
        )


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureCertificateValidation:
    """One validation result for the certificate support surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointDiagonalInstanceClosureCertificateReport:
    """Validation report for diagonal-instance closure certificate support."""

    manifest: FixedPointDiagonalInstanceClosureCertificateManifest
    diagonal_instance_closure_path: Path
    diagonal_instance_candidate_surface_path: Path
    frontier_selector_path: Path
    willard_map_path: Path
    certificates: tuple[FixedPointDiagonalInstanceClosureCertificate, ...]
    results: tuple[FixedPointDiagonalInstanceClosureCertificateValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether the certificate support surface accepted."""

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
    closures: tuple[Any, ...] = ()
    candidates: tuple[Any, ...] = ()
    selected: tuple[Any, ...] = ()


def load_fixed_point_diagonal_instance_closure_certificate(
    path: Path | str = DEFAULT_CERTIFICATE,
) -> FixedPointDiagonalInstanceClosureCertificateManifest:
    """Load the diagonal-instance closure certificate manifest."""

    certificate_path = Path(path)
    data = json.loads(certificate_path.read_text(encoding="utf-8"))
    return FixedPointDiagonalInstanceClosureCertificateManifest(
        path=certificate_path,
        schema_version=_required_int(data, "schema_version"),
        certificate_set_id=_required_text(data, "certificate_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        diagonal_instance_closure_path=_required_text(
            data,
            "diagonal_instance_closure_path",
        ),
        diagonal_instance_candidate_surface_path=_required_text(
            data,
            "diagonal_instance_candidate_surface_path",
        ),
        frontier_selector_path=_required_text(data, "frontier_selector_path"),
        expected_certificate_count=_required_int(
            data,
            "expected_certificate_count",
        ),
        expected_step_ids=tuple(_required_text_list(data, "expected_step_ids")),
        expected_selected_case_kind=_required_text(
            data,
            "expected_selected_case_kind",
        ),
        expected_candidate_code_length=_required_int(
            data,
            "expected_candidate_code_length",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_diagonal_instance_closure_certificate(
    manifest: FixedPointDiagonalInstanceClosureCertificateManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointDiagonalInstanceClosureCertificateReport:
    """Validate finite certificate support for the diagonal-instance root."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointDiagonalInstanceClosureCertificateValidation] = [
        _accepted("manifest", f"loaded {manifest.certificate_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    selector_report = _load_selector(paths["frontier_selector_path"], checked_willard_map_path)
    closure_report = _load_closure(paths["diagonal_instance_closure_path"], checked_willard_map_path)
    candidate_report = _load_candidate(
        paths["diagonal_instance_candidate_surface_path"],
        checked_willard_map_path,
    )
    results.extend(_validate_dependencies(selector_report, closure_report, candidate_report))

    certificates = _derive_certificates(
        manifest,
        selector_report,
        closure_report,
        candidate_report,
    )
    results.extend(_validate_certificates(manifest, certificates))

    return FixedPointDiagonalInstanceClosureCertificateReport(
        manifest=manifest,
        diagonal_instance_closure_path=paths["diagonal_instance_closure_path"],
        diagonal_instance_candidate_surface_path=paths[
            "diagonal_instance_candidate_surface_path"
        ],
        frontier_selector_path=paths["frontier_selector_path"],
        willard_map_path=checked_willard_map_path,
        certificates=tuple(certificates),
        results=tuple(results),
    )


def fixed_point_diagonal_instance_closure_certificate_payload(
    report: FixedPointDiagonalInstanceClosureCertificateReport,
) -> dict[str, Any]:
    """Return a JSON-ready certificate support payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "certificate_manifest": str(report.manifest.path),
        "certificate_set_id": report.manifest.certificate_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "diagonal_instance_closure_path": str(report.diagonal_instance_closure_path),
        "diagonal_instance_candidate_surface_path": str(
            report.diagonal_instance_candidate_surface_path
        ),
        "frontier_selector_path": str(report.frontier_selector_path),
        "willard_map": str(report.willard_map_path),
        "expected_certificate_count": report.manifest.expected_certificate_count,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "expected_step_ids": list(report.manifest.expected_step_ids),
        "expected_selected_case_kind": report.manifest.expected_selected_case_kind,
        "expected_candidate_code_length": (
            report.manifest.expected_candidate_code_length
        ),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "certificates": [
            {
                "certificate_id": certificate.certificate_id,
                "construction_case_id": certificate.construction_case_id,
                "selected_case_kind": certificate.selected_case_kind,
                "target_id": certificate.target_id,
                "closure_id": certificate.closure_id,
                "candidate_id": certificate.candidate_id,
                "certificate_status": certificate.certificate_status,
                "observed_candidate_code_length": certificate.candidate_code_length,
                "observed_selector_accepts_root": certificate.selector_accepts_root,
                "observed_closure_accepted": certificate.closure_accepted,
                "observed_candidate_surface_accepted": (
                    certificate.candidate_surface_accepted
                ),
                "observed_diagonal_instance_closed": (
                    certificate.diagonal_instance_closed
                ),
                "observed_codebook_roundtrip": certificate.codebook_roundtrip,
                "observed_candidate_matches_closure": (
                    certificate.candidate_matches_closure
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


def format_fixed_point_diagonal_instance_closure_certificate_report(
    report: FixedPointDiagonalInstanceClosureCertificateReport,
) -> str:
    """Format a concise human-readable certificate support report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point diagonal instance closure certificate: {status}",
        f"Certificate set: {report.manifest.certificate_set_id}",
        f"Certificates: {report.certificate_count}",
        f"Certificate steps: {report.certificate_step_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for certificate in report.certificates:
        lines.extend(
            (
                f"Certificate {certificate.certificate_id}:",
                f"  Construction case: {certificate.construction_case_id}",
                f"  Selected case kind: {certificate.selected_case_kind}",
                f"  Status: {certificate.certificate_status}",
                f"  Candidate code length: {certificate.candidate_code_length}",
                f"  Accepted: {certificate.accepted}",
                "  Steps:",
            )
        )
        for step in certificate.steps:
            prefix = "accepted" if step.accepted else "rejected"
            lines.append(f"  - {step.step_id}: {prefix} ({step.detail})")
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_diagonal_instance_closure_certificate_cli(
    argv: list[str] | None = None,
) -> int:
    """Run diagonal-instance closure certificate support validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_diagonal_instance_closure_certificate"
        ),
        description=(
            "Validate AS fixed-point diagonal-instance finite certificate support."
        ),
    )
    parser.add_argument(
        "--certificate",
        default=str(DEFAULT_CERTIFICATE),
        help="Path to the diagonal-instance closure certificate manifest.",
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

    manifest = load_fixed_point_diagonal_instance_closure_certificate(
        args.certificate
    )
    report = validate_fixed_point_diagonal_instance_closure_certificate(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_diagonal_instance_closure_certificate_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_diagonal_instance_closure_certificate_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointDiagonalInstanceClosureCertificateManifest,
) -> dict[str, Path]:
    return {
        "diagonal_instance_closure_path": Path(
            manifest.diagonal_instance_closure_path
        ),
        "diagonal_instance_candidate_surface_path": Path(
            manifest.diagonal_instance_candidate_surface_path
        ),
        "frontier_selector_path": Path(manifest.frontier_selector_path),
    }


def _load_selector(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_frontier_selector(path)
        return validate_fixed_point_frontier_selector(manifest, willard_map_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-frontier-selector-load",))


def _load_closure(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_diagonal_instance_closure(path)
        return validate_fixed_point_diagonal_instance_closure(manifest, willard_map_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-diagonal-instance-closure-load",),
        )


def _load_candidate(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_diagonal_instance_candidate_surface(path)
        return validate_fixed_point_diagonal_instance_candidate_surface(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-diagonal-instance-candidate-surface-load",),
        )


def _validate_manifest(
    manifest: FixedPointDiagonalInstanceClosureCertificateManifest,
) -> list[FixedPointDiagonalInstanceClosureCertificateValidation]:
    results: list[FixedPointDiagonalInstanceClosureCertificateValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if (
        manifest.certificate_set_id
        == "as-fixed-point-diagonal-instance-closure-certificate-v1"
    ):
        results.append(_accepted("certificate_set_id", "certificate set id matches"))
    else:
        results.append(_rejected("certificate_set_id", "unexpected certificate set id"))

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.expected_certificate_count == 1:
        results.append(_accepted("expected_certificate_count", "one certificate"))
    else:
        results.append(_rejected("expected_certificate_count", "expected one certificate"))

    if manifest.expected_step_ids == REQUIRED_CERTIFICATE_STEP_IDS:
        results.append(_accepted("expected_step_ids", "certificate step ids match"))
    else:
        results.append(_rejected("expected_step_ids", "step id mismatch"))

    if manifest.expected_selected_case_kind == REQUIRED_SELECTED_CASE_KIND:
        results.append(_accepted("expected_selected_case_kind", "selected root matches"))
    else:
        results.append(
            _rejected(
                "expected_selected_case_kind",
                "expected diagonal-instance-closure selected root",
            )
        )

    if manifest.expected_candidate_code_length == 296:
        results.append(_accepted("expected_candidate_code_length", "296 checked"))
    else:
        results.append(
            _rejected(
                "expected_candidate_code_length",
                "expected candidate code length 296",
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


def _validate_dependencies(
    selector_report: Any,
    closure_report: Any,
    candidate_report: Any,
) -> list[FixedPointDiagonalInstanceClosureCertificateValidation]:
    checks = (
        ("frontier_selector", selector_report, "frontier selector"),
        ("diagonal_instance_closure", closure_report, "diagonal-instance closure"),
        (
            "diagonal_instance_candidate_surface",
            candidate_report,
            "diagonal-instance candidate surface",
        ),
    )
    results: list[FixedPointDiagonalInstanceClosureCertificateValidation] = []
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


def _derive_certificates(
    manifest: FixedPointDiagonalInstanceClosureCertificateManifest,
    selector_report: Any,
    closure_report: Any,
    candidate_report: Any,
) -> list[FixedPointDiagonalInstanceClosureCertificate]:
    if not (selector_report.accepted and closure_report.accepted and candidate_report.accepted):
        return []
    selected_case = _find_case_kind(selector_report.selected, manifest.expected_selected_case_kind)
    if selected_case is None:
        return []
    if not closure_report.closures or not candidate_report.candidates:
        return []

    closure = closure_report.closures[0]
    candidate = candidate_report.candidates[0]
    selector_accepts_root = (
        selected_case.case_kind == REQUIRED_SELECTED_CASE_KIND
        and selected_case.status == "proof-case-open"
    )
    closure_accepted = closure_report.accepted
    candidate_accepted = candidate_report.accepted
    candidate_matches_closure = (
        candidate.closure_id == closure.closure_id
        and candidate.candidate_code_length == closure.diagonal_instance_code_length
        and candidate.candidate_code_prefix == closure.diagonal_instance_code_prefix
        and candidate.target_id == closure.target_id
        and candidate.bridge_id == closure.bridge_id
    )
    candidate_future_work = getattr(
        getattr(candidate_report, "manifest", None),
        "required_future_work",
        (),
    )
    proof_boundary_preserved = (
        selected_case.status == "proof-case-open"
        and "fixed-point-equation-proof" in candidate_future_work
        and "self-consistency-theorem" in candidate_future_work
    )
    steps = (
        _step(
            "select-open-root-obligation",
            selector_accepts_root,
            "selector keeps diagonal-instance-closure as an open root",
        ),
        _step("accept-closure-report", closure_accepted, "closure report accepted"),
        _step(
            "accept-candidate-surface",
            candidate_accepted,
            "candidate-surface report accepted",
        ),
        _step(
            "check-closed-diagonal-instance",
            closure.diagonal_instance_closed,
            "diagonal instance has no free variables",
        ),
        _step(
            "check-codebook-roundtrip",
            closure.codebook_roundtrip and candidate.candidate_codebook_roundtrip,
            "closure and candidate roundtrip through the codebook",
        ),
        _step(
            "match-candidate-to-closure",
            candidate_matches_closure,
            "candidate surface names the accepted closure point",
        ),
        _step(
            "preserve-open-proof-boundary",
            proof_boundary_preserved,
            "construction case remains open with later proof work required",
        ),
    )
    return [
        FixedPointDiagonalInstanceClosureCertificate(
            certificate_id="AS-FIXED-POINT-DIAGONAL-INSTANCE-CLOSURE-CERTIFICATE",
            construction_case_id=REQUIRED_CONSTRUCTION_CASE_ID,
            selected_case_kind=selected_case.case_kind,
            target_id=closure.target_id,
            closure_id=closure.closure_id,
            candidate_id=candidate.candidate_id,
            certificate_status="accepted-finite-certificate-not-proof",
            candidate_code_length=candidate.candidate_code_length,
            selector_accepts_root=selector_accepts_root,
            closure_accepted=closure_accepted,
            candidate_surface_accepted=candidate_accepted,
            diagonal_instance_closed=closure.diagonal_instance_closed,
            codebook_roundtrip=closure.codebook_roundtrip
            and candidate.candidate_codebook_roundtrip,
            candidate_matches_closure=candidate_matches_closure,
            proof_boundary_preserved=proof_boundary_preserved,
            steps=steps,
        )
    ]


def _validate_certificates(
    manifest: FixedPointDiagonalInstanceClosureCertificateManifest,
    certificates: list[FixedPointDiagonalInstanceClosureCertificate],
) -> list[FixedPointDiagonalInstanceClosureCertificateValidation]:
    results: list[FixedPointDiagonalInstanceClosureCertificateValidation] = []
    if len(certificates) == manifest.expected_certificate_count:
        results.append(_accepted("certificate_count", "certificate count matches"))
    else:
        results.append(
            _rejected(
                "certificate_count",
                (
                    "certificate count mismatch: expected "
                    f"{manifest.expected_certificate_count} got {len(certificates)}"
                ),
            )
        )
        return results

    certificate = certificates[0]
    if certificate.accepted:
        results.append(_accepted("certificate", "certificate accepted"))
    else:
        results.append(_rejected("certificate", "certificate rejected"))

    observed_step_ids = tuple(step.step_id for step in certificate.steps)
    if observed_step_ids == manifest.expected_step_ids:
        results.append(_accepted("certificate_steps", "certificate step ids match"))
    else:
        results.append(_rejected("certificate_steps", "step id mismatch"))

    if certificate.candidate_code_length == manifest.expected_candidate_code_length:
        results.append(_accepted("candidate_code_length", "candidate length matches"))
    else:
        results.append(
            _rejected("candidate_code_length", "candidate code length mismatch")
        )
    return results


def _find_case_kind(cases: tuple[Any, ...], case_kind: str) -> Any | None:
    for item in cases:
        if item.case_kind == case_kind:
            return item
    return None


def _step(
    step_id: str,
    accepted: bool,
    detail: str,
) -> FixedPointDiagonalInstanceClosureCertificateStep:
    return FixedPointDiagonalInstanceClosureCertificateStep(step_id, accepted, detail)


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise ValueError(f"{key} must be a non-empty text list")
    return value


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_step_ids", "certificate_steps"}:
        return "fixed-point-diagonal-instance-closure-certificate-steps"
    if subject == "non_claims":
        return "fixed-point-diagonal-instance-closure-certificate-non-claim"
    if subject == "certificate_count":
        return "fixed-point-diagonal-instance-closure-certificate-count"
    if subject == "candidate_code_length":
        return "fixed-point-diagonal-instance-closure-certificate-length"
    if subject == "certificate":
        return "fixed-point-diagonal-instance-closure-certificate"
    return subject.replace("_", "-")


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureCertificateValidation:
    return FixedPointDiagonalInstanceClosureCertificateValidation(subject, True, detail)


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointDiagonalInstanceClosureCertificateValidation:
    return FixedPointDiagonalInstanceClosureCertificateValidation(subject, False, detail)


def _joined_or_none(values: tuple[str, ...]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_diagonal_instance_closure_certificate_cli())
