"""Finite certificate support for the fixed-point bridge-equality case.

The bridge-equality evaluation module owns the expensive finite derivation that
evaluates ``substitution_code(quote(seed), quote(seed))``. This module wraps
that accepted route in a compact certificate surface with named steps. It is
certificate support only: it does not prove the general bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_bridge_equality_alignment import (
    load_fixed_point_bridge_equality_alignment,
    validate_fixed_point_bridge_equality_alignment,
)
from autarkic_systems.fixed_point_bridge_equality_evaluation import (
    load_fixed_point_bridge_equality_evaluation,
    validate_fixed_point_bridge_equality_evaluation,
)
from autarkic_systems.fixed_point_equation_bridge import (
    load_fixed_point_equation_bridge_targets,
    validate_fixed_point_equation_bridge_targets,
)
from autarkic_systems.formal_code import (
    load_formal_codebook,
    validate_formal_codebook,
)


DEFAULT_CERTIFICATE = Path("claims/fixed_point_bridge_equality_certificate.json")
DEFAULT_FORMAL_LANGUAGE = Path("language/formal_arithmetic_language.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CERTIFICATE_STEP_IDS = (
    "decode-left-formula",
    "decode-self-argument",
    "evaluate-substitution-code",
    "match-witness-output",
    "match-right-quote",
    "bridge-equation-formed",
)
REQUIRED_NON_CLAIMS = (
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "fixed_point_equation_bridge_targets_path": (
        "claims/fixed_point_equation_bridge_targets.json"
    ),
    "bridge_equality_alignment_path": (
        "claims/fixed_point_bridge_equality_alignment.json"
    ),
    "bridge_equality_evaluation_path": (
        "claims/fixed_point_bridge_equality_evaluation.json"
    ),
    "codebook_path": "language/formal_codebook.json",
}
PROOF_PROMOTION_NON_CLAIMS = {
    "bridge equality proof",
    "fixed-point equation proof",
    "arithmetized proof predicate",
    "self-consistency theorem",
}


@dataclass(frozen=True)
class FixedPointBridgeEqualityCertificateManifest:
    """Loaded manifest for bridge-equality certificate support."""

    path: Path
    schema_version: int
    certificate_set_id: str
    reviewed_at: str
    purpose: str
    fixed_point_equation_bridge_targets_path: str
    bridge_equality_alignment_path: str
    bridge_equality_evaluation_path: str
    codebook_path: str
    expected_certificate_count: int
    expected_step_ids: tuple[str, ...]
    expected_bridge_equation_code_length: int
    expected_evaluation_output_code_length: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityCertificateStep:
    """One checked finite step in the bridge-equality certificate support."""

    step_id: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityCertificate:
    """One finite certificate support object for the bridge-equality case."""

    certificate_id: str
    construction_case_id: str
    target_id: str
    certificate_status: str
    evaluation_id: str
    equation_bridge_id: str
    witness_id: str
    bridge_equality_alignment_id: str
    bridge_equation_code_length: int
    evaluation_output_code_length: int
    evaluation_accepted: bool
    alignment_accepted: bool
    equation_bridge_formed: bool
    steps: tuple[FixedPointBridgeEqualityCertificateStep, ...]

    @property
    def all_steps_accepted(self) -> bool:
        """Return whether all named certificate steps accepted."""

        return all(step.accepted for step in self.steps)

    @property
    def accepted(self) -> bool:
        """Return whether this finite certificate support object accepted."""

        return (
            self.certificate_status == "accepted-finite-certificate-not-proof"
            and self.evaluation_accepted
            and self.alignment_accepted
            and self.equation_bridge_formed
            and self.all_steps_accepted
        )


@dataclass(frozen=True)
class FixedPointBridgeEqualityCertificateValidation:
    """One validation result for the certificate support surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointBridgeEqualityCertificateReport:
    """Validation report for bridge-equality certificate support."""

    manifest: FixedPointBridgeEqualityCertificateManifest
    fixed_point_equation_bridge_targets_path: Path
    bridge_equality_alignment_path: Path
    bridge_equality_evaluation_path: Path
    codebook_path: Path
    formal_language_path: Path
    willard_map_path: Path
    certificates: tuple[FixedPointBridgeEqualityCertificate, ...]
    results: tuple[FixedPointBridgeEqualityCertificateValidation, ...]

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
        """Return the total number of named certificate steps."""

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
    """Small report shim used when a dependency cannot be loaded."""

    accepted: bool
    failed_subjects: tuple[str, ...]
    evaluations: tuple[Any, ...] = ()
    alignments: tuple[Any, ...] = ()
    observations: tuple[Any, ...] = ()


def load_fixed_point_bridge_equality_certificate(
    path: Path | str = DEFAULT_CERTIFICATE,
) -> FixedPointBridgeEqualityCertificateManifest:
    """Load the bridge-equality certificate support manifest."""

    certificate_path = Path(path)
    data = json.loads(certificate_path.read_text(encoding="utf-8"))
    return FixedPointBridgeEqualityCertificateManifest(
        path=certificate_path,
        schema_version=_required_int(data, "schema_version"),
        certificate_set_id=_required_text(data, "certificate_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        fixed_point_equation_bridge_targets_path=_required_text(
            data,
            "fixed_point_equation_bridge_targets_path",
        ),
        bridge_equality_alignment_path=_required_text(
            data,
            "bridge_equality_alignment_path",
        ),
        bridge_equality_evaluation_path=_required_text(
            data,
            "bridge_equality_evaluation_path",
        ),
        codebook_path=_required_text(data, "codebook_path"),
        expected_certificate_count=_required_int(
            data,
            "expected_certificate_count",
        ),
        expected_step_ids=tuple(_required_text_list(data, "expected_step_ids")),
        expected_bridge_equation_code_length=_required_int(
            data,
            "expected_bridge_equation_code_length",
        ),
        expected_evaluation_output_code_length=_required_int(
            data,
            "expected_evaluation_output_code_length",
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_bridge_equality_certificate(
    manifest: FixedPointBridgeEqualityCertificateManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
    formal_language_path: Path | str = DEFAULT_FORMAL_LANGUAGE,
) -> FixedPointBridgeEqualityCertificateReport:
    """Validate bridge-equality certificate support against existing surfaces."""

    checked_willard_map_path = Path(willard_map_path)
    checked_formal_language_path = Path(formal_language_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointBridgeEqualityCertificateValidation] = [
        _accepted("manifest", f"loaded {manifest.certificate_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    equation_report = _load_equation_bridge(
        paths["fixed_point_equation_bridge_targets_path"],
        checked_formal_language_path,
        checked_willard_map_path,
    )
    alignment_report = _load_alignment(
        paths["bridge_equality_alignment_path"],
        checked_willard_map_path,
    )
    evaluation_report = _load_evaluation(
        paths["bridge_equality_evaluation_path"],
        checked_willard_map_path,
    )
    codebook_report = _load_codebook(
        paths["codebook_path"],
        checked_formal_language_path,
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            equation_report,
            alignment_report,
            evaluation_report,
            codebook_report,
        )
    )

    certificates = _derive_certificates(
        evaluation_report,
        alignment_report,
        equation_report,
        manifest.expected_bridge_equation_code_length,
        manifest.expected_evaluation_output_code_length,
    )
    results.extend(_validate_certificates(manifest, certificates))

    return FixedPointBridgeEqualityCertificateReport(
        manifest=manifest,
        fixed_point_equation_bridge_targets_path=paths[
            "fixed_point_equation_bridge_targets_path"
        ],
        bridge_equality_alignment_path=paths["bridge_equality_alignment_path"],
        bridge_equality_evaluation_path=paths["bridge_equality_evaluation_path"],
        codebook_path=paths["codebook_path"],
        formal_language_path=checked_formal_language_path,
        willard_map_path=checked_willard_map_path,
        certificates=tuple(certificates),
        results=tuple(results),
    )


def fixed_point_bridge_equality_certificate_payload(
    report: FixedPointBridgeEqualityCertificateReport,
) -> dict[str, Any]:
    """Return a JSON-ready certificate support payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "certificate_manifest": str(report.manifest.path),
        "certificate_set_id": report.manifest.certificate_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "fixed_point_equation_bridge_targets_path": str(
            report.fixed_point_equation_bridge_targets_path
        ),
        "bridge_equality_alignment_path": str(report.bridge_equality_alignment_path),
        "bridge_equality_evaluation_path": str(report.bridge_equality_evaluation_path),
        "codebook_path": str(report.codebook_path),
        "formal_language_path": str(report.formal_language_path),
        "willard_map": str(report.willard_map_path),
        "expected_certificate_count": report.manifest.expected_certificate_count,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "expected_step_ids": list(report.manifest.expected_step_ids),
        "expected_bridge_equation_code_length": (
            report.manifest.expected_bridge_equation_code_length
        ),
        "expected_evaluation_output_code_length": (
            report.manifest.expected_evaluation_output_code_length
        ),
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "certificates": [
            {
                "certificate_id": certificate.certificate_id,
                "construction_case_id": certificate.construction_case_id,
                "target_id": certificate.target_id,
                "certificate_status": certificate.certificate_status,
                "evaluation_id": certificate.evaluation_id,
                "equation_bridge_id": certificate.equation_bridge_id,
                "witness_id": certificate.witness_id,
                "bridge_equality_alignment_id": (
                    certificate.bridge_equality_alignment_id
                ),
                "observed_bridge_equation_code_length": (
                    certificate.bridge_equation_code_length
                ),
                "observed_evaluation_output_code_length": (
                    certificate.evaluation_output_code_length
                ),
                "observed_evaluation_accepted": certificate.evaluation_accepted,
                "observed_alignment_accepted": certificate.alignment_accepted,
                "observed_equation_bridge_formed": certificate.equation_bridge_formed,
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


def format_fixed_point_bridge_equality_certificate_report(
    report: FixedPointBridgeEqualityCertificateReport,
) -> str:
    """Format a concise human-readable certificate support report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point bridge equality certificate: {status}",
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
                f"  Target: {certificate.target_id}",
                f"  Status: {certificate.certificate_status}",
                (
                    "  Bridge equation code length: "
                    f"{certificate.bridge_equation_code_length}"
                ),
                (
                    "  Evaluation output code length: "
                    f"{certificate.evaluation_output_code_length}"
                ),
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


def run_fixed_point_bridge_equality_certificate_cli(
    argv: list[str] | None = None,
) -> int:
    """Run fixed-point bridge-equality certificate support validation."""

    parser = argparse.ArgumentParser(
        prog="python -m autarkic_systems.fixed_point_bridge_equality_certificate",
        description=(
            "Validate AS fixed-point bridge-equality finite certificate support."
        ),
    )
    parser.add_argument(
        "--certificate",
        default=str(DEFAULT_CERTIFICATE),
        help="Path to the fixed-point bridge-equality certificate manifest.",
    )
    parser.add_argument(
        "--willard-map",
        default=str(DEFAULT_WILLARD_MAP),
        help="Path to the Willard definition map.",
    )
    parser.add_argument(
        "--formal-language",
        default=str(DEFAULT_FORMAL_LANGUAGE),
        help="Path to the formal arithmetic language.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for the validation report.",
    )
    args = parser.parse_args(argv)

    manifest = load_fixed_point_bridge_equality_certificate(args.certificate)
    report = validate_fixed_point_bridge_equality_certificate(
        manifest,
        args.willard_map,
        args.formal_language,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_bridge_equality_certificate_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_bridge_equality_certificate_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointBridgeEqualityCertificateManifest,
) -> dict[str, Path]:
    return {
        "fixed_point_equation_bridge_targets_path": Path(
            manifest.fixed_point_equation_bridge_targets_path
        ),
        "bridge_equality_alignment_path": Path(
            manifest.bridge_equality_alignment_path
        ),
        "bridge_equality_evaluation_path": Path(
            manifest.bridge_equality_evaluation_path
        ),
        "codebook_path": Path(manifest.codebook_path),
    }


def _load_equation_bridge(
    path: Path,
    formal_language_path: Path,
    willard_map_path: Path,
) -> Any:
    try:
        manifest = load_fixed_point_equation_bridge_targets(path)
        return validate_fixed_point_equation_bridge_targets(
            manifest,
            formal_language_path,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-equation-bridge-load",))


def _load_alignment(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_bridge_equality_alignment(path)
        return validate_fixed_point_bridge_equality_alignment(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-bridge-equality-alignment-load",),
        )


def _load_evaluation(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_bridge_equality_evaluation(path)
        return validate_fixed_point_bridge_equality_evaluation(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-bridge-equality-evaluation-load",),
        )


def _load_codebook(
    path: Path,
    formal_language_path: Path,
    willard_map_path: Path,
) -> Any:
    try:
        codebook = load_formal_codebook(path)
        return validate_formal_codebook(
            codebook,
            formal_language_path,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("formal-codebook-load",))


def _validate_manifest(
    manifest: FixedPointBridgeEqualityCertificateManifest,
) -> list[FixedPointBridgeEqualityCertificateValidation]:
    results: list[FixedPointBridgeEqualityCertificateValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.certificate_set_id == "as-fixed-point-bridge-equality-certificate-v1":
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

    if manifest.expected_bridge_equation_code_length == 4815:
        results.append(_accepted("expected_bridge_equation_code_length", "4815 checked"))
    else:
        results.append(
            _rejected(
                "expected_bridge_equation_code_length",
                "expected bridge equation length 4815",
            )
        )

    if manifest.expected_evaluation_output_code_length == 296:
        results.append(_accepted("expected_evaluation_output_code_length", "296 checked"))
    else:
        results.append(
            _rejected(
                "expected_evaluation_output_code_length",
                "expected evaluation output length 296",
            )
        )

    missing_non_claims = [
        item for item in REQUIRED_NON_CLAIMS if item not in manifest.non_claims
    ]
    proof_promotions = [
        item for item in manifest.non_claims if item in PROOF_PROMOTION_NON_CLAIMS
    ]
    if missing_non_claims:
        results.append(
            _rejected(
                "non_claims",
                "missing non-claims: " + ", ".join(missing_non_claims),
            )
        )
    elif proof_promotions:
        results.append(
            _rejected(
                "non_claims",
                "proof-promotion non-claims: " + ", ".join(proof_promotions),
            )
        )
    else:
        results.append(_accepted("non_claims", "non-claims are explicit"))

    if manifest.next_as_action.strip():
        results.append(_accepted("next_as_action", "next action present"))
    else:
        results.append(_rejected("next_as_action", "missing next action"))
    return results


def _validate_dependencies(
    equation_report: Any,
    alignment_report: Any,
    evaluation_report: Any,
    codebook_report: Any,
) -> list[FixedPointBridgeEqualityCertificateValidation]:
    checks = (
        ("fixed_point_equation_bridge", equation_report, "fixed-point equation bridge"),
        (
            "bridge_equality_alignment",
            alignment_report,
            "fixed-point bridge equality alignment",
        ),
        (
            "bridge_equality_evaluation",
            evaluation_report,
            "fixed-point bridge equality evaluation",
        ),
        ("codebook", codebook_report, "formal codebook"),
    )
    results: list[FixedPointBridgeEqualityCertificateValidation] = []
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
    evaluation_report: Any,
    alignment_report: Any,
    equation_report: Any,
    expected_bridge_length: int,
    expected_output_length: int,
) -> list[FixedPointBridgeEqualityCertificate]:
    if not (
        getattr(evaluation_report, "accepted", False)
        and getattr(alignment_report, "accepted", False)
        and getattr(equation_report, "accepted", False)
    ):
        return []
    evaluations = tuple(getattr(evaluation_report, "evaluations", ()))
    alignments = tuple(getattr(alignment_report, "alignments", ()))
    observations = tuple(getattr(equation_report, "observations", ()))
    if len(evaluations) != 1 or len(alignments) != 1 or len(observations) != 1:
        return []

    evaluation = evaluations[0]
    alignment = alignments[0]
    observation = observations[0]
    equation_bridge_formed = (
        bool(getattr(observation, "bridge_equation_closed", False))
        and getattr(observation, "bridge_equation_code_length", None)
        == expected_bridge_length
        and getattr(evaluation, "bridge_equation_code_length", None)
        == expected_bridge_length
    )
    steps = (
        FixedPointBridgeEqualityCertificateStep(
            "decode-left-formula",
            bool(getattr(evaluation, "left_formula_decodes_to_seed", False)),
            "left bridge formula quotation decodes to the current diagonal seed",
        ),
        FixedPointBridgeEqualityCertificateStep(
            "decode-self-argument",
            bool(
                getattr(evaluation, "self_application_argument_matches_seed", False)
            ),
            "self-application argument quotation recovers the same seed code",
        ),
        FixedPointBridgeEqualityCertificateStep(
            "evaluate-substitution-code",
            bool(
                getattr(evaluation, "left_term_is_substitution_code", False)
                and getattr(evaluation, "output_code_length", None)
                == expected_output_length
            ),
            "left substitution-code term evaluates to the expected output length",
        ),
        FixedPointBridgeEqualityCertificateStep(
            "match-witness-output",
            bool(getattr(evaluation, "evaluated_output_matches_witness", False)),
            "evaluated output matches the substitution witness output",
        ),
        FixedPointBridgeEqualityCertificateStep(
            "match-right-quote",
            bool(getattr(evaluation, "evaluated_output_matches_right_quote", False)),
            "evaluated output matches the right quoted diagonal-instance term",
        ),
        FixedPointBridgeEqualityCertificateStep(
            "bridge-equation-formed",
            equation_bridge_formed,
            "checked bridge equation is closed at the expected code length",
        ),
    )
    return [
        FixedPointBridgeEqualityCertificate(
            certificate_id="AS-FIXED-POINT-BRIDGE-EQUALITY-CERTIFICATE",
            construction_case_id=getattr(evaluation, "construction_case_id"),
            target_id=getattr(evaluation, "target_id"),
            certificate_status="accepted-finite-certificate-not-proof",
            evaluation_id=getattr(evaluation, "evaluation_id"),
            equation_bridge_id=getattr(evaluation, "equation_bridge_id"),
            witness_id=getattr(evaluation, "witness_id"),
            bridge_equality_alignment_id=getattr(
                evaluation,
                "bridge_equality_alignment_id",
            ),
            bridge_equation_code_length=getattr(
                evaluation,
                "bridge_equation_code_length",
            ),
            evaluation_output_code_length=getattr(evaluation, "output_code_length"),
            evaluation_accepted=bool(
                getattr(evaluation, "all_dependencies_accepted", False)
                and getattr(evaluation, "evaluated_output_matches_right_quote", False)
            ),
            alignment_accepted=bool(
                getattr(alignment, "route_ids_match", False)
                and getattr(alignment, "bridge_equation_matches_schema_instance", False)
            ),
            equation_bridge_formed=equation_bridge_formed,
            steps=steps,
        )
    ]


def _validate_certificates(
    manifest: FixedPointBridgeEqualityCertificateManifest,
    certificates: list[FixedPointBridgeEqualityCertificate],
) -> list[FixedPointBridgeEqualityCertificateValidation]:
    results: list[FixedPointBridgeEqualityCertificateValidation] = []
    if len(certificates) == manifest.expected_certificate_count:
        results.append(_accepted("certificates.count", "certificate count matches"))
    else:
        results.append(
            _rejected(
                "certificates.count",
                "certificate count mismatch: expected "
                + str(manifest.expected_certificate_count)
                + " but found "
                + str(len(certificates)),
            )
        )

    for certificate in certificates:
        observed_step_ids = tuple(step.step_id for step in certificate.steps)
        if observed_step_ids == manifest.expected_step_ids:
            results.append(
                _accepted(
                    f"{certificate.certificate_id}.steps",
                    "certificate step id order matches",
                )
            )
        else:
            results.append(
                _rejected(
                    f"{certificate.certificate_id}.steps",
                    "step id mismatch",
                )
            )
        if certificate.bridge_equation_code_length == (
            manifest.expected_bridge_equation_code_length
        ):
            results.append(
                _accepted(
                    f"{certificate.certificate_id}.bridge_equation_length",
                    "bridge equation length matches",
                )
            )
        else:
            results.append(
                _rejected(
                    f"{certificate.certificate_id}.bridge_equation_length",
                    "bridge equation length mismatch",
                )
            )
        if certificate.evaluation_output_code_length == (
            manifest.expected_evaluation_output_code_length
        ):
            results.append(
                _accepted(
                    f"{certificate.certificate_id}.evaluation_output_length",
                    "evaluation output length matches",
                )
            )
        else:
            results.append(
                _rejected(
                    f"{certificate.certificate_id}.evaluation_output_length",
                    "evaluation output length mismatch",
                )
            )
        if certificate.accepted:
            results.append(_accepted(certificate.certificate_id, "certificate accepted"))
        else:
            results.append(
                _rejected(
                    certificate.certificate_id,
                    "certificate support did not accept",
                )
            )
    return results


def _failed_subject_for_result(subject: str) -> str:
    if subject == "expected_step_ids" or subject.endswith(".steps"):
        return "fixed-point-bridge-equality-certificate-steps"
    if subject == "non_claims":
        return "fixed-point-bridge-equality-certificate-non-claim"
    if subject in EXPECTED_DEPENDENCY_PATHS or subject in {
        "fixed_point_equation_bridge",
        "bridge_equality_alignment",
        "bridge_equality_evaluation",
        "codebook",
    }:
        return "fixed-point-bridge-equality-certificate-dependency"
    if subject.startswith("expected_") or subject.endswith("_length"):
        return "fixed-point-bridge-equality-certificate-length"
    if subject == "certificates.count":
        return "fixed-point-bridge-equality-certificate-count"
    return "fixed-point-bridge-equality-certificate"


def _required_text(item: dict[str, Any], key: str) -> str:
    value = item.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"required text field missing: {key}")
    return value


def _required_int(item: dict[str, Any], key: str) -> int:
    value = item.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"required integer field missing: {key}")
    return value


def _required_list(item: dict[str, Any], key: str) -> list[Any]:
    value = item.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"required list field missing: {key}")
    return value


def _required_text_list(item: dict[str, Any], key: str) -> list[str]:
    values = _required_list(item, key)
    result: list[str] = []
    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{key} contains non-text item")
        result.append(value)
    return result


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityCertificateValidation:
    return FixedPointBridgeEqualityCertificateValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointBridgeEqualityCertificateValidation:
    return FixedPointBridgeEqualityCertificateValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _joined_or_none(values: tuple[str, ...] | list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(values)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_bridge_equality_certificate_cli())
