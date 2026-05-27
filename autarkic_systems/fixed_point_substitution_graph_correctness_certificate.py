"""Finite certificate support for the substitution-graph-correctness root.

The current fixed-point frontier selector marks
``substitution-graph-correctness-proof`` as an open root obligation. This
module wraps the accepted selector, graph-correctness target, correctness case
rollup, and fixed-point graph-correctness bridge in one compact certificate
support object. It is not a proof that graph correctness has been established
and does not prove a fixed-point equation or self-consistency theorem.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_frontier_selector import (
    load_fixed_point_frontier_selector,
    validate_fixed_point_frontier_selector,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_bridge import (
    load_fixed_point_substitution_graph_correctness_bridge,
    validate_fixed_point_substitution_graph_correctness_bridge,
)
from autarkic_systems.substitution_graph_correctness import (
    load_substitution_graph_correctness_targets,
    validate_substitution_graph_correctness_targets,
)
from autarkic_systems.substitution_graph_correctness_cases import (
    load_substitution_graph_correctness_cases,
    validate_substitution_graph_correctness_cases,
)


DEFAULT_CERTIFICATE = Path(
    "claims/fixed_point_substitution_graph_correctness_certificate.json"
)
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_CERTIFICATE_STEP_IDS = (
    "select-open-root-obligation",
    "accept-correctness-target",
    "accept-correctness-case-rollup",
    "accept-bridge-report",
    "check-correctness-case-count",
    "check-finite-dependency-coverage",
    "preserve-open-proof-boundary",
)
REQUIRED_NON_CLAIMS = (
    "no substitution graph correctness proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "substitution_graph_correctness_targets_path": (
        "claims/substitution_graph_correctness_targets.json"
    ),
    "substitution_graph_correctness_cases_path": (
        "claims/substitution_graph_correctness_cases.json"
    ),
    "substitution_graph_correctness_bridge_path": (
        "claims/fixed_point_substitution_graph_correctness_bridge.json"
    ),
    "frontier_selector_path": "claims/fixed_point_frontier_selector.json",
}
REQUIRED_SELECTED_CASE_KIND = "substitution-graph-correctness-proof"
REQUIRED_CONSTRUCTION_CASE_ID = (
    "AS-FIXED-POINT-CONSTRUCTION-SUBSTITUTION-GRAPH-CORRECTNESS"
)
REQUIRED_TARGET_STATUS = "correctness-proof-not-constructed"
REQUIRED_CASE_STATUS = "proof-case-open"


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessCertificateManifest:
    """Loaded manifest for graph-correctness certificate support."""

    path: Path
    schema_version: int
    certificate_set_id: str
    reviewed_at: str
    purpose: str
    substitution_graph_correctness_targets_path: str
    substitution_graph_correctness_cases_path: str
    substitution_graph_correctness_bridge_path: str
    frontier_selector_path: str
    expected_certificate_count: int
    expected_step_ids: tuple[str, ...]
    expected_selected_case_kind: str
    expected_correctness_case_count: int
    expected_finite_dependency_count: int
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessCertificateStep:
    """One checked finite certificate-support step."""

    step_id: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessCertificate:
    """One finite certificate support object for graph correctness."""

    certificate_id: str
    construction_case_id: str
    selected_case_kind: str
    target_id: str
    correctness_case_set_id: str
    bridge_id: str
    certificate_status: str
    correctness_case_count: int
    finite_dependency_count: int
    selector_accepts_root: bool
    correctness_target_accepted: bool
    correctness_cases_accepted: bool
    bridge_report_accepted: bool
    bridge_links_construction_case: bool
    all_correctness_cases_open: bool
    proof_boundary_preserved: bool
    steps: tuple[FixedPointSubstitutionGraphCorrectnessCertificateStep, ...]

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
            and self.correctness_target_accepted
            and self.correctness_cases_accepted
            and self.bridge_report_accepted
            and self.bridge_links_construction_case
            and self.correctness_case_count == 5
            and self.finite_dependency_count == 5
            and self.all_correctness_cases_open
            and self.proof_boundary_preserved
            and self.all_steps_accepted
        )


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessCertificateValidation:
    """One validation result for the certificate support surface."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSubstitutionGraphCorrectnessCertificateReport:
    """Validation report for graph-correctness certificate support."""

    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest
    substitution_graph_correctness_targets_path: Path
    substitution_graph_correctness_cases_path: Path
    substitution_graph_correctness_bridge_path: Path
    frontier_selector_path: Path
    willard_map_path: Path
    certificates: tuple[FixedPointSubstitutionGraphCorrectnessCertificate, ...]
    results: tuple[FixedPointSubstitutionGraphCorrectnessCertificateValidation, ...]

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
    targets: tuple[Any, ...] = ()
    cases: tuple[Any, ...] = ()
    bridges: tuple[Any, ...] = ()
    selected: tuple[Any, ...] = ()


def load_fixed_point_substitution_graph_correctness_certificate(
    path: Path | str = DEFAULT_CERTIFICATE,
) -> FixedPointSubstitutionGraphCorrectnessCertificateManifest:
    """Load the substitution graph correctness certificate manifest."""

    certificate_path = Path(path)
    data = json.loads(certificate_path.read_text(encoding="utf-8"))
    return FixedPointSubstitutionGraphCorrectnessCertificateManifest(
        path=certificate_path,
        schema_version=_required_int(data, "schema_version"),
        certificate_set_id=_required_text(data, "certificate_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        substitution_graph_correctness_targets_path=_required_text(
            data,
            "substitution_graph_correctness_targets_path",
        ),
        substitution_graph_correctness_cases_path=_required_text(
            data,
            "substitution_graph_correctness_cases_path",
        ),
        substitution_graph_correctness_bridge_path=_required_text(
            data,
            "substitution_graph_correctness_bridge_path",
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


@lru_cache(maxsize=32)
def validate_fixed_point_substitution_graph_correctness_certificate(
    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSubstitutionGraphCorrectnessCertificateReport:
    """Validate finite certificate support for the graph-correctness root."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointSubstitutionGraphCorrectnessCertificateValidation] = [
        _accepted("manifest", f"loaded {manifest.certificate_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    selector_report = _load_selector(
        paths["frontier_selector_path"],
        checked_willard_map_path,
    )
    correctness_report = _load_correctness_targets(
        paths["substitution_graph_correctness_targets_path"],
        checked_willard_map_path,
    )
    correctness_case_report = _load_correctness_cases(
        paths["substitution_graph_correctness_cases_path"],
        checked_willard_map_path,
    )
    bridge_report = _load_bridge(
        paths["substitution_graph_correctness_bridge_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            selector_report,
            correctness_report,
            correctness_case_report,
            bridge_report,
        )
    )

    certificates = _derive_certificates(
        manifest,
        selector_report,
        correctness_report,
        correctness_case_report,
        bridge_report,
    )
    results.extend(_validate_certificates(manifest, certificates))

    return FixedPointSubstitutionGraphCorrectnessCertificateReport(
        manifest=manifest,
        substitution_graph_correctness_targets_path=paths[
            "substitution_graph_correctness_targets_path"
        ],
        substitution_graph_correctness_cases_path=paths[
            "substitution_graph_correctness_cases_path"
        ],
        substitution_graph_correctness_bridge_path=paths[
            "substitution_graph_correctness_bridge_path"
        ],
        frontier_selector_path=paths["frontier_selector_path"],
        willard_map_path=checked_willard_map_path,
        certificates=tuple(certificates),
        results=tuple(results),
    )


def fixed_point_substitution_graph_correctness_certificate_payload(
    report: FixedPointSubstitutionGraphCorrectnessCertificateReport,
) -> dict[str, Any]:
    """Return a JSON-ready certificate support payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "certificate_manifest": str(report.manifest.path),
        "certificate_set_id": report.manifest.certificate_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "substitution_graph_correctness_targets_path": str(
            report.substitution_graph_correctness_targets_path
        ),
        "substitution_graph_correctness_cases_path": str(
            report.substitution_graph_correctness_cases_path
        ),
        "substitution_graph_correctness_bridge_path": str(
            report.substitution_graph_correctness_bridge_path
        ),
        "frontier_selector_path": str(report.frontier_selector_path),
        "willard_map": str(report.willard_map_path),
        "expected_certificate_count": report.manifest.expected_certificate_count,
        "certificate_count": report.certificate_count,
        "certificate_step_count": report.certificate_step_count,
        "expected_step_ids": list(report.manifest.expected_step_ids),
        "expected_selected_case_kind": report.manifest.expected_selected_case_kind,
        "expected_correctness_case_count": (
            report.manifest.expected_correctness_case_count
        ),
        "expected_finite_dependency_count": (
            report.manifest.expected_finite_dependency_count
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
                "correctness_case_set_id": certificate.correctness_case_set_id,
                "bridge_id": certificate.bridge_id,
                "certificate_status": certificate.certificate_status,
                "observed_correctness_case_count": (
                    certificate.correctness_case_count
                ),
                "observed_finite_dependency_count": (
                    certificate.finite_dependency_count
                ),
                "observed_selector_accepts_root": certificate.selector_accepts_root,
                "observed_correctness_target_accepted": (
                    certificate.correctness_target_accepted
                ),
                "observed_correctness_cases_accepted": (
                    certificate.correctness_cases_accepted
                ),
                "observed_bridge_report_accepted": (
                    certificate.bridge_report_accepted
                ),
                "observed_bridge_links_construction_case": (
                    certificate.bridge_links_construction_case
                ),
                "observed_all_correctness_cases_open": (
                    certificate.all_correctness_cases_open
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


def format_fixed_point_substitution_graph_correctness_certificate_report(
    report: FixedPointSubstitutionGraphCorrectnessCertificateReport,
) -> str:
    """Format a concise human-readable certificate support report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point substitution graph correctness certificate: {status}",
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
                f"  Correctness cases: {certificate.correctness_case_count}",
                f"  Finite dependencies: {certificate.finite_dependency_count}",
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


def run_fixed_point_substitution_graph_correctness_certificate_cli(
    argv: list[str] | None = None,
) -> int:
    """Run graph-correctness certificate support validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_substitution_graph_correctness_certificate"
        ),
        description=(
            "Validate AS fixed-point substitution graph correctness finite "
            "certificate support."
        ),
    )
    parser.add_argument(
        "--certificate",
        default=str(DEFAULT_CERTIFICATE),
        help="Path to the graph-correctness certificate manifest.",
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

    manifest = load_fixed_point_substitution_graph_correctness_certificate(
        args.certificate
    )
    report = validate_fixed_point_substitution_graph_correctness_certificate(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_substitution_graph_correctness_certificate_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(
            format_fixed_point_substitution_graph_correctness_certificate_report(
                report
            )
        )
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest,
) -> dict[str, Path]:
    return {
        "substitution_graph_correctness_targets_path": Path(
            manifest.substitution_graph_correctness_targets_path
        ),
        "substitution_graph_correctness_cases_path": Path(
            manifest.substitution_graph_correctness_cases_path
        ),
        "substitution_graph_correctness_bridge_path": Path(
            manifest.substitution_graph_correctness_bridge_path
        ),
        "frontier_selector_path": Path(manifest.frontier_selector_path),
    }


def _load_selector(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_frontier_selector(path)
        return validate_fixed_point_frontier_selector(manifest, willard_map_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-frontier-selector-load",))


def _load_correctness_targets(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_substitution_graph_correctness_targets(path)
        return validate_substitution_graph_correctness_targets(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("substitution-graph-correctness-target-load",),
        )


def _load_correctness_cases(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_substitution_graph_correctness_cases(path)
        return validate_substitution_graph_correctness_cases(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("substitution-graph-correctness-cases-load",),
        )


def _load_bridge(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_substitution_graph_correctness_bridge(path)
        return validate_fixed_point_substitution_graph_correctness_bridge(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-substitution-graph-correctness-bridge-load",),
        )


def _validate_manifest(
    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest,
) -> list[FixedPointSubstitutionGraphCorrectnessCertificateValidation]:
    results: list[FixedPointSubstitutionGraphCorrectnessCertificateValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if (
        manifest.certificate_set_id
        == "as-fixed-point-substitution-graph-correctness-certificate-v1"
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
        results.append(
            _rejected("expected_certificate_count", "expected one certificate")
        )

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
                "expected substitution-graph-correctness-proof selected root",
            )
        )

    if manifest.expected_correctness_case_count == 5:
        results.append(_accepted("expected_correctness_case_count", "five cases"))
    else:
        results.append(
            _rejected(
                "expected_correctness_case_count",
                "expected five correctness cases",
            )
        )

    if manifest.expected_finite_dependency_count == 5:
        results.append(_accepted("expected_finite_dependency_count", "five finite dependencies"))
    else:
        results.append(
            _rejected(
                "expected_finite_dependency_count",
                "expected five finite dependencies",
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
    correctness_report: Any,
    correctness_case_report: Any,
    bridge_report: Any,
) -> list[FixedPointSubstitutionGraphCorrectnessCertificateValidation]:
    checks = (
        ("frontier_selector", selector_report, "frontier selector"),
        (
            "substitution_graph_correctness",
            correctness_report,
            "substitution graph correctness target",
        ),
        (
            "substitution_graph_correctness_cases",
            correctness_case_report,
            "substitution graph correctness cases",
        ),
        (
            "substitution_graph_correctness_bridge",
            bridge_report,
            "fixed-point graph-correctness bridge",
        ),
    )
    results: list[FixedPointSubstitutionGraphCorrectnessCertificateValidation] = []
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
    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest,
    selector_report: Any,
    correctness_report: Any,
    correctness_case_report: Any,
    bridge_report: Any,
) -> list[FixedPointSubstitutionGraphCorrectnessCertificate]:
    if not (
        selector_report.accepted
        and correctness_report.accepted
        and correctness_case_report.accepted
        and bridge_report.accepted
    ):
        return []
    selected_case = _find_case_kind(
        selector_report.selected,
        manifest.expected_selected_case_kind,
    )
    if selected_case is None:
        return []
    if not correctness_report.manifest.targets:
        return []
    if not correctness_case_report.manifest.cases:
        return []
    if not bridge_report.bridges:
        return []

    target = correctness_report.manifest.targets[0]
    bridge = bridge_report.bridges[0]
    selector_accepts_root = (
        selected_case.case_kind == REQUIRED_SELECTED_CASE_KIND
        and selected_case.case_id == REQUIRED_CONSTRUCTION_CASE_ID
        and selected_case.status == REQUIRED_CASE_STATUS
    )
    correctness_target_accepted = (
        correctness_report.accepted
        and target.status == REQUIRED_TARGET_STATUS
    )
    correctness_cases_accepted = correctness_case_report.accepted
    bridge_report_accepted = bridge_report.accepted
    bridge_links_construction_case = (
        bridge.construction_case_id == selected_case.case_id
        and bridge.correctness_target_id == target.target_id
    )
    correctness_case_count = correctness_case_report.case_count
    finite_dependency_count = bridge.finite_dependency_count
    all_correctness_cases_open = all(
        case.status == REQUIRED_CASE_STATUS
        for case in correctness_case_report.manifest.cases
    )
    proof_boundary_preserved = _proof_boundary_preserved(
        manifest,
        selected_case,
        target,
        correctness_case_report.manifest.cases,
        bridge,
        bridge_report,
    )
    steps = _certificate_steps(
        selector_accepts_root=selector_accepts_root,
        correctness_target_accepted=correctness_target_accepted,
        correctness_cases_accepted=correctness_cases_accepted,
        bridge_report_accepted=bridge_report_accepted,
        correctness_case_count=correctness_case_count,
        expected_case_count=manifest.expected_correctness_case_count,
        finite_dependency_count=finite_dependency_count,
        expected_dependency_count=manifest.expected_finite_dependency_count,
        proof_boundary_preserved=proof_boundary_preserved,
    )

    return [
        FixedPointSubstitutionGraphCorrectnessCertificate(
            certificate_id=(
                "AS-FIXED-POINT-SUBSTITUTION-GRAPH-CORRECTNESS-CERTIFICATE"
            ),
            construction_case_id=selected_case.case_id,
            selected_case_kind=selected_case.case_kind,
            target_id=target.target_id,
            correctness_case_set_id=correctness_case_report.manifest.case_set_id,
            bridge_id=bridge.bridge_id,
            certificate_status="accepted-finite-certificate-not-proof",
            correctness_case_count=correctness_case_count,
            finite_dependency_count=finite_dependency_count,
            selector_accepts_root=selector_accepts_root,
            correctness_target_accepted=correctness_target_accepted,
            correctness_cases_accepted=correctness_cases_accepted,
            bridge_report_accepted=bridge_report_accepted,
            bridge_links_construction_case=bridge_links_construction_case,
            all_correctness_cases_open=all_correctness_cases_open,
            proof_boundary_preserved=proof_boundary_preserved,
            steps=steps,
        )
    ]


def _certificate_steps(
    *,
    selector_accepts_root: bool,
    correctness_target_accepted: bool,
    correctness_cases_accepted: bool,
    bridge_report_accepted: bool,
    correctness_case_count: int,
    expected_case_count: int,
    finite_dependency_count: int,
    expected_dependency_count: int,
    proof_boundary_preserved: bool,
) -> tuple[FixedPointSubstitutionGraphCorrectnessCertificateStep, ...]:
    step_facts = (
        (
            "select-open-root-obligation",
            selector_accepts_root,
            "selector keeps graph correctness as an open root",
            "selector did not expose the graph-correctness root",
        ),
        (
            "accept-correctness-target",
            correctness_target_accepted,
            "correctness target accepted without proof promotion",
            "correctness target rejected or promoted",
        ),
        (
            "accept-correctness-case-rollup",
            correctness_cases_accepted,
            "correctness case rollup accepted",
            "correctness case rollup rejected",
        ),
        (
            "accept-bridge-report",
            bridge_report_accepted,
            "fixed-point graph-correctness bridge accepted",
            "fixed-point graph-correctness bridge rejected",
        ),
        (
            "check-correctness-case-count",
            correctness_case_count == expected_case_count,
            f"correctness case count {correctness_case_count}",
            f"expected {expected_case_count} cases but found {correctness_case_count}",
        ),
        (
            "check-finite-dependency-coverage",
            finite_dependency_count == expected_dependency_count,
            f"finite dependency count {finite_dependency_count}",
            "expected "
            f"{expected_dependency_count} finite dependencies but found "
            f"{finite_dependency_count}",
        ),
        (
            "preserve-open-proof-boundary",
            proof_boundary_preserved,
            "proof boundary remains open",
            "proof boundary was promoted or weakened",
        ),
    )
    return tuple(
        FixedPointSubstitutionGraphCorrectnessCertificateStep(
            step_id=step_id,
            accepted=accepted,
            detail=ok_detail if accepted else fail_detail,
        )
        for step_id, accepted, ok_detail, fail_detail in step_facts
    )


def _validate_certificates(
    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest,
    certificates: list[FixedPointSubstitutionGraphCorrectnessCertificate],
) -> list[FixedPointSubstitutionGraphCorrectnessCertificateValidation]:
    results: list[FixedPointSubstitutionGraphCorrectnessCertificateValidation] = []
    if len(certificates) == manifest.expected_certificate_count:
        results.append(
            _accepted(
                "certificate_count",
                f"certificate count {len(certificates)} matches",
            )
        )
    else:
        results.append(
            _rejected(
                "certificate_count",
                "certificate count mismatch: expected "
                f"{manifest.expected_certificate_count} but found "
                f"{len(certificates)}",
            )
        )
    if not certificates:
        return results

    certificate = certificates[0]
    observed_step_ids = tuple(step.step_id for step in certificate.steps)
    if observed_step_ids == manifest.expected_step_ids:
        results.append(_accepted("certificate_steps", "certificate steps match"))
    else:
        results.append(_rejected("certificate_steps", "step id mismatch"))

    if certificate.selected_case_kind == manifest.expected_selected_case_kind:
        results.append(_accepted("selected_case_kind", "selected root matches"))
    else:
        results.append(_rejected("selected_case_kind", "selected root mismatch"))

    if certificate.correctness_case_count == manifest.expected_correctness_case_count:
        results.append(_accepted("correctness_case_count", "case count matches"))
    else:
        results.append(_rejected("correctness_case_count", "case count mismatch"))

    if certificate.finite_dependency_count == manifest.expected_finite_dependency_count:
        results.append(
            _accepted("finite_dependency_count", "finite dependency count matches")
        )
    else:
        results.append(
            _rejected("finite_dependency_count", "finite dependency count mismatch")
        )

    if certificate.accepted:
        results.append(_accepted("certificate", "certificate support accepted"))
    else:
        results.append(_rejected("certificate", "certificate support rejected"))
    return results


def _proof_boundary_preserved(
    manifest: FixedPointSubstitutionGraphCorrectnessCertificateManifest,
    selected_case: Any,
    target: Any,
    correctness_cases: tuple[Any, ...],
    bridge: Any,
    bridge_report: Any,
) -> bool:
    required_non_claims = set(REQUIRED_NON_CLAIMS)
    case_non_claims = [
        set(case.non_claims) for case in correctness_cases
    ]
    return (
        selected_case.status == REQUIRED_CASE_STATUS
        and target.status == REQUIRED_TARGET_STATUS
        and all(case.status == REQUIRED_CASE_STATUS for case in correctness_cases)
        and bridge.construction_case_is_open
        and required_non_claims.issubset(set(manifest.non_claims))
        and required_non_claims.issubset(set(bridge_report.manifest.non_claims))
        and all(required_non_claims & non_claims for non_claims in case_non_claims)
    )


def _find_case_kind(cases: tuple[Any, ...], case_kind: str) -> Any | None:
    for case in cases:
        if case.case_kind == case_kind:
            return case
    return None


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionGraphCorrectnessCertificateValidation:
    return FixedPointSubstitutionGraphCorrectnessCertificateValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointSubstitutionGraphCorrectnessCertificateValidation:
    return FixedPointSubstitutionGraphCorrectnessCertificateValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_step_ids", "certificate_steps"}:
        return "fixed-point-substitution-graph-correctness-certificate-steps"
    if subject in {"certificate_count", "expected_certificate_count"}:
        return "fixed-point-substitution-graph-correctness-certificate-count"
    if subject == "expected_selected_case_kind" or subject == "selected_case_kind":
        return "fixed-point-substitution-graph-correctness-certificate-selected-root"
    if subject in {"expected_correctness_case_count", "correctness_case_count"}:
        return "fixed-point-substitution-graph-correctness-certificate-case-count"
    if subject in {"expected_finite_dependency_count", "finite_dependency_count"}:
        return "fixed-point-substitution-graph-correctness-certificate-dependencies"
    if subject == "non_claims":
        return "fixed-point-substitution-graph-correctness-certificate-non-claim"
    if subject.endswith("_path"):
        return "fixed-point-substitution-graph-correctness-certificate-path"
    if subject == "certificate":
        return "fixed-point-substitution-graph-correctness-certificate"
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
    if not isinstance(value, list) or not value:
        raise ValueError(f"{key} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{key} must contain only non-empty strings")
    return value


def _joined_or_none(items: tuple[str, ...]) -> str:
    if not items:
        return "none"
    return ", ".join(items)


if __name__ == "__main__":
    raise SystemExit(run_fixed_point_substitution_graph_correctness_certificate_cli())
