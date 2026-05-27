"""Coverage surface for selected fixed-point root certificates.

The fixed-point frontier selector currently exposes two open root obligations.
ADR-0303 and ADR-0304 added finite certificate support for those roots
individually. This module checks that the selected root set is covered by those
accepted certificate surfaces while preserving the open proof boundary. It
does not prove any fixed-point construction case or promote downstream cases.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from autarkic_systems.fixed_point_diagonal_instance_closure_certificate import (
    load_fixed_point_diagonal_instance_closure_certificate,
    validate_fixed_point_diagonal_instance_closure_certificate,
)
from autarkic_systems.fixed_point_frontier_selector import (
    load_fixed_point_frontier_selector,
    validate_fixed_point_frontier_selector,
)
from autarkic_systems.fixed_point_substitution_graph_correctness_certificate import (
    load_fixed_point_substitution_graph_correctness_certificate,
    validate_fixed_point_substitution_graph_correctness_certificate,
)


DEFAULT_COVERAGE = Path("claims/fixed_point_selected_root_certificate_coverage.json")
DEFAULT_WILLARD_MAP = Path("sources/willard_definition_map.json")

REQUIRED_SELECTED_CASE_KINDS = (
    "diagonal-instance-closure",
    "substitution-graph-correctness-proof",
)
REQUIRED_DEFERRED_CASE_KINDS = (
    "substitution-representability-proof",
    "bridge-equality-proof",
    "fixed-point-equation-lifting",
)
REQUIRED_NON_CLAIMS = (
    "no diagonal-instance closure proof",
    "no substitution graph correctness proof",
    "no substitution representability proof",
    "no bridge equality proof",
    "no fixed-point equation proof",
    "no arithmetized proof predicate",
    "no self-consistency theorem",
)
EXPECTED_DEPENDENCY_PATHS = {
    "frontier_selector_path": "claims/fixed_point_frontier_selector.json",
    "diagonal_instance_closure_certificate_path": (
        "claims/fixed_point_diagonal_instance_closure_certificate.json"
    ),
    "substitution_graph_correctness_certificate_path": (
        "claims/fixed_point_substitution_graph_correctness_certificate.json"
    ),
}
REQUIRED_CASE_STATUS = "proof-case-open"


@dataclass(frozen=True)
class FixedPointSelectedRootCertificateCoverageManifest:
    """Loaded manifest for selected-root certificate coverage."""

    path: Path
    schema_version: int
    coverage_set_id: str
    reviewed_at: str
    purpose: str
    frontier_selector_path: str
    diagonal_instance_closure_certificate_path: str
    substitution_graph_correctness_certificate_path: str
    expected_selected_certificate_count: int
    expected_total_certificate_step_count: int
    expected_selected_case_kinds: tuple[str, ...]
    expected_deferred_case_kinds: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_as_action: str


@dataclass(frozen=True)
class FixedPointSelectedRootCertificateCoverageEntry:
    """One selected root covered by one accepted finite certificate."""

    coverage_id: str
    selected_case_kind: str
    construction_case_id: str
    certificate_set_id: str
    certificate_id: str
    certificate_step_count: int
    coverage_status: str
    selector_selects_case: bool
    construction_case_open: bool
    certificate_accepted: bool
    proof_boundary_preserved: bool

    @property
    def accepted(self) -> bool:
        """Return whether this selected-root coverage entry accepted."""

        return (
            self.coverage_status == "accepted-finite-certificate-coverage-not-proof"
            and self.selector_selects_case
            and self.construction_case_open
            and self.certificate_accepted
            and self.proof_boundary_preserved
        )


@dataclass(frozen=True)
class FixedPointSelectedRootCertificateCoverageValidation:
    """One validation result for selected-root certificate coverage."""

    subject: str
    accepted: bool
    detail: str


@dataclass(frozen=True)
class FixedPointSelectedRootCertificateCoverageReport:
    """Validation report for selected-root certificate coverage."""

    manifest: FixedPointSelectedRootCertificateCoverageManifest
    frontier_selector_path: Path
    diagonal_instance_closure_certificate_path: Path
    substitution_graph_correctness_certificate_path: Path
    willard_map_path: Path
    selected_case_kinds: tuple[str, ...]
    deferred_case_kinds: tuple[str, ...]
    proof_boundary_preserved: bool
    coverage_entries: tuple[FixedPointSelectedRootCertificateCoverageEntry, ...]
    results: tuple[FixedPointSelectedRootCertificateCoverageValidation, ...]

    @property
    def accepted(self) -> bool:
        """Return whether selected-root certificate coverage accepted."""

        return all(result.accepted for result in self.results)

    @property
    def coverage_count(self) -> int:
        """Return the number of selected-root coverage entries."""

        return len(self.coverage_entries)

    @property
    def total_certificate_step_count(self) -> int:
        """Return the total checked certificate steps across coverage entries."""

        return sum(entry.certificate_step_count for entry in self.coverage_entries)

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
    selected: tuple[Any, ...] = ()
    deferred: tuple[Any, ...] = ()
    certificates: tuple[Any, ...] = ()
    manifest: Any | None = None


def load_fixed_point_selected_root_certificate_coverage(
    path: Path | str = DEFAULT_COVERAGE,
) -> FixedPointSelectedRootCertificateCoverageManifest:
    """Load the selected-root certificate coverage manifest."""

    coverage_path = Path(path)
    data = json.loads(coverage_path.read_text(encoding="utf-8"))
    return FixedPointSelectedRootCertificateCoverageManifest(
        path=coverage_path,
        schema_version=_required_int(data, "schema_version"),
        coverage_set_id=_required_text(data, "coverage_set_id"),
        reviewed_at=_required_text(data, "reviewed_at"),
        purpose=_required_text(data, "purpose"),
        frontier_selector_path=_required_text(data, "frontier_selector_path"),
        diagonal_instance_closure_certificate_path=_required_text(
            data,
            "diagonal_instance_closure_certificate_path",
        ),
        substitution_graph_correctness_certificate_path=_required_text(
            data,
            "substitution_graph_correctness_certificate_path",
        ),
        expected_selected_certificate_count=_required_int(
            data,
            "expected_selected_certificate_count",
        ),
        expected_total_certificate_step_count=_required_int(
            data,
            "expected_total_certificate_step_count",
        ),
        expected_selected_case_kinds=tuple(
            _required_text_list(data, "expected_selected_case_kinds")
        ),
        expected_deferred_case_kinds=tuple(
            _required_text_list(data, "expected_deferred_case_kinds")
        ),
        non_claims=tuple(_required_text_list(data, "non_claims")),
        next_as_action=_required_text(data, "next_as_action"),
    )


@lru_cache(maxsize=32)
def validate_fixed_point_selected_root_certificate_coverage(
    manifest: FixedPointSelectedRootCertificateCoverageManifest,
    willard_map_path: Path | str = DEFAULT_WILLARD_MAP,
) -> FixedPointSelectedRootCertificateCoverageReport:
    """Validate finite certificate coverage for selected fixed-point roots."""

    checked_willard_map_path = Path(willard_map_path)
    paths = _manifest_paths(manifest)
    results: list[FixedPointSelectedRootCertificateCoverageValidation] = [
        _accepted("manifest", f"loaded {manifest.coverage_set_id}")
    ]
    results.extend(_validate_manifest(manifest))

    selector_report = _load_selector(
        paths["frontier_selector_path"],
        checked_willard_map_path,
    )
    diagonal_certificate_report = _load_diagonal_certificate(
        paths["diagonal_instance_closure_certificate_path"],
        checked_willard_map_path,
    )
    graph_certificate_report = _load_graph_certificate(
        paths["substitution_graph_correctness_certificate_path"],
        checked_willard_map_path,
    )
    results.extend(
        _validate_dependencies(
            selector_report,
            diagonal_certificate_report,
            graph_certificate_report,
        )
    )

    selected_case_kinds = tuple(case.case_kind for case in selector_report.selected)
    deferred_case_kinds = tuple(case.case_kind for case in selector_report.deferred)
    proof_boundary_preserved = _proof_boundary_preserved(
        manifest,
        selector_report,
        diagonal_certificate_report,
        graph_certificate_report,
    )
    coverage_entries = _derive_coverage_entries(
        selector_report,
        diagonal_certificate_report,
        graph_certificate_report,
        proof_boundary_preserved,
    )
    results.extend(
        _validate_coverage(
            manifest,
            selected_case_kinds,
            deferred_case_kinds,
            proof_boundary_preserved,
            coverage_entries,
        )
    )

    return FixedPointSelectedRootCertificateCoverageReport(
        manifest=manifest,
        frontier_selector_path=paths["frontier_selector_path"],
        diagonal_instance_closure_certificate_path=paths[
            "diagonal_instance_closure_certificate_path"
        ],
        substitution_graph_correctness_certificate_path=paths[
            "substitution_graph_correctness_certificate_path"
        ],
        willard_map_path=checked_willard_map_path,
        selected_case_kinds=selected_case_kinds,
        deferred_case_kinds=deferred_case_kinds,
        proof_boundary_preserved=proof_boundary_preserved,
        coverage_entries=tuple(coverage_entries),
        results=tuple(results),
    )


def fixed_point_selected_root_certificate_coverage_payload(
    report: FixedPointSelectedRootCertificateCoverageReport,
) -> dict[str, Any]:
    """Return a JSON-ready selected-root certificate coverage payload."""

    return {
        "accepted": report.accepted,
        "schema_version": report.manifest.schema_version,
        "coverage_manifest": str(report.manifest.path),
        "coverage_set_id": report.manifest.coverage_set_id,
        "reviewed_at": report.manifest.reviewed_at,
        "purpose": report.manifest.purpose,
        "frontier_selector_path": str(report.frontier_selector_path),
        "diagonal_instance_closure_certificate_path": str(
            report.diagonal_instance_closure_certificate_path
        ),
        "substitution_graph_correctness_certificate_path": str(
            report.substitution_graph_correctness_certificate_path
        ),
        "willard_map": str(report.willard_map_path),
        "expected_selected_certificate_count": (
            report.manifest.expected_selected_certificate_count
        ),
        "expected_total_certificate_step_count": (
            report.manifest.expected_total_certificate_step_count
        ),
        "expected_selected_case_kinds": list(
            report.manifest.expected_selected_case_kinds
        ),
        "expected_deferred_case_kinds": list(
            report.manifest.expected_deferred_case_kinds
        ),
        "selected_case_kinds": list(report.selected_case_kinds),
        "deferred_case_kinds": list(report.deferred_case_kinds),
        "coverage_count": report.coverage_count,
        "total_certificate_step_count": report.total_certificate_step_count,
        "observed_proof_boundary_preserved": report.proof_boundary_preserved,
        "non_claims": list(report.manifest.non_claims),
        "next_as_action": report.manifest.next_as_action,
        "failed_subjects": list(report.failed_subjects),
        "coverage_entries": [
            {
                "coverage_id": entry.coverage_id,
                "selected_case_kind": entry.selected_case_kind,
                "construction_case_id": entry.construction_case_id,
                "certificate_set_id": entry.certificate_set_id,
                "certificate_id": entry.certificate_id,
                "certificate_step_count": entry.certificate_step_count,
                "coverage_status": entry.coverage_status,
                "observed_selector_selects_case": entry.selector_selects_case,
                "observed_construction_case_open": entry.construction_case_open,
                "observed_certificate_accepted": entry.certificate_accepted,
                "observed_proof_boundary_preserved": (
                    entry.proof_boundary_preserved
                ),
                "accepted": entry.accepted,
            }
            for entry in report.coverage_entries
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


def format_fixed_point_selected_root_certificate_coverage_report(
    report: FixedPointSelectedRootCertificateCoverageReport,
) -> str:
    """Format a concise selected-root certificate coverage report."""

    status = "accepted" if report.accepted else "rejected"
    lines = [
        f"Fixed-point selected root certificate coverage: {status}",
        f"Coverage set: {report.manifest.coverage_set_id}",
        f"Selected roots: {_joined_or_none(report.selected_case_kinds)}",
        f"Deferred cases: {_joined_or_none(report.deferred_case_kinds)}",
        f"Coverage entries: {report.coverage_count}",
        f"Total certificate steps: {report.total_certificate_step_count}",
        "Non-claims: " + _joined_or_none(report.manifest.non_claims),
        f"Failed subjects: {_joined_or_none(report.failed_subjects)}",
    ]
    for entry in report.coverage_entries:
        prefix = "accepted" if entry.accepted else "rejected"
        lines.append(
            f"{entry.selected_case_kind}: {prefix} "
            f"({entry.certificate_id}, {entry.certificate_step_count} steps)"
        )
    lines.append("Validation:")
    for result in report.results:
        prefix = "OK" if result.accepted else "FAIL"
        lines.append(f"{prefix} {result.subject}: {result.detail}")
    return "\n".join(lines)


def run_fixed_point_selected_root_certificate_coverage_cli(
    argv: list[str] | None = None,
) -> int:
    """Run selected-root certificate coverage validation."""

    parser = argparse.ArgumentParser(
        prog=(
            "python -m "
            "autarkic_systems.fixed_point_selected_root_certificate_coverage"
        ),
        description=(
            "Validate finite certificate coverage for selected AS fixed-point "
            "root obligations."
        ),
    )
    parser.add_argument(
        "--coverage",
        default=str(DEFAULT_COVERAGE),
        help="Path to the selected-root certificate coverage manifest.",
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

    manifest = load_fixed_point_selected_root_certificate_coverage(args.coverage)
    report = validate_fixed_point_selected_root_certificate_coverage(
        manifest,
        args.willard_map,
    )
    if args.format == "json":
        print(
            json.dumps(
                fixed_point_selected_root_certificate_coverage_payload(report),
                sort_keys=True,
            )
        )
    else:
        print(format_fixed_point_selected_root_certificate_coverage_report(report))
    return 0 if report.accepted else 1


def _manifest_paths(
    manifest: FixedPointSelectedRootCertificateCoverageManifest,
) -> dict[str, Path]:
    return {
        "frontier_selector_path": Path(manifest.frontier_selector_path),
        "diagonal_instance_closure_certificate_path": Path(
            manifest.diagonal_instance_closure_certificate_path
        ),
        "substitution_graph_correctness_certificate_path": Path(
            manifest.substitution_graph_correctness_certificate_path
        ),
    }


def _load_selector(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_frontier_selector(path)
        return validate_fixed_point_frontier_selector(manifest, willard_map_path)
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(False, ("fixed-point-frontier-selector-load",))


def _load_diagonal_certificate(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_diagonal_instance_closure_certificate(path)
        return validate_fixed_point_diagonal_instance_closure_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-diagonal-instance-closure-certificate-load",),
        )


def _load_graph_certificate(path: Path, willard_map_path: Path) -> Any:
    try:
        manifest = load_fixed_point_substitution_graph_correctness_certificate(path)
        return validate_fixed_point_substitution_graph_correctness_certificate(
            manifest,
            willard_map_path,
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return _DependencyFailure(
            False,
            ("fixed-point-substitution-graph-correctness-certificate-load",),
        )


def _validate_manifest(
    manifest: FixedPointSelectedRootCertificateCoverageManifest,
) -> list[FixedPointSelectedRootCertificateCoverageValidation]:
    results: list[FixedPointSelectedRootCertificateCoverageValidation] = []
    if manifest.schema_version == 1:
        results.append(_accepted("schema_version", "schema version 1"))
    else:
        results.append(
            _rejected("schema_version", f"unsupported schema: {manifest.schema_version}")
        )

    if manifest.coverage_set_id == "as-fixed-point-selected-root-certificate-coverage-v1":
        results.append(_accepted("coverage_set_id", "coverage set id matches"))
    else:
        results.append(_rejected("coverage_set_id", "unexpected coverage set id"))

    for field, expected in EXPECTED_DEPENDENCY_PATHS.items():
        actual = getattr(manifest, field)
        if actual == expected:
            results.append(_accepted(field, f"{expected} referenced"))
        else:
            results.append(_rejected(field, f"expected {expected} but found {actual}"))

    if manifest.expected_selected_certificate_count == 2:
        results.append(_accepted("expected_selected_certificate_count", "two certificates"))
    else:
        results.append(
            _rejected(
                "expected_selected_certificate_count",
                "expected two selected-root certificates",
            )
        )

    if manifest.expected_total_certificate_step_count == 14:
        results.append(_accepted("expected_total_certificate_step_count", "fourteen steps"))
    else:
        results.append(
            _rejected(
                "expected_total_certificate_step_count",
                "expected fourteen total certificate steps",
            )
        )

    if manifest.expected_selected_case_kinds == REQUIRED_SELECTED_CASE_KINDS:
        results.append(_accepted("expected_selected_case_kinds", "selected roots match"))
    else:
        results.append(
            _rejected("expected_selected_case_kinds", "selected root mismatch")
        )

    if manifest.expected_deferred_case_kinds == REQUIRED_DEFERRED_CASE_KINDS:
        results.append(_accepted("expected_deferred_case_kinds", "deferred cases match"))
    else:
        results.append(
            _rejected("expected_deferred_case_kinds", "deferred case mismatch")
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
    diagonal_certificate_report: Any,
    graph_certificate_report: Any,
) -> list[FixedPointSelectedRootCertificateCoverageValidation]:
    checks = (
        ("frontier_selector", selector_report, "frontier selector"),
        (
            "diagonal_instance_closure_certificate",
            diagonal_certificate_report,
            "diagonal-instance closure certificate",
        ),
        (
            "substitution_graph_correctness_certificate",
            graph_certificate_report,
            "substitution graph correctness certificate",
        ),
    )
    results: list[FixedPointSelectedRootCertificateCoverageValidation] = []
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


def _derive_coverage_entries(
    selector_report: Any,
    diagonal_certificate_report: Any,
    graph_certificate_report: Any,
    proof_boundary_preserved: bool,
) -> list[FixedPointSelectedRootCertificateCoverageEntry]:
    if not (
        selector_report.accepted
        and diagonal_certificate_report.accepted
        and graph_certificate_report.accepted
    ):
        return []

    selected_by_kind = {case.case_kind: case for case in selector_report.selected}
    reports_by_kind = {
        "diagonal-instance-closure": diagonal_certificate_report,
        "substitution-graph-correctness-proof": graph_certificate_report,
    }
    entries: list[FixedPointSelectedRootCertificateCoverageEntry] = []
    for case_kind in REQUIRED_SELECTED_CASE_KINDS:
        selected_case = selected_by_kind.get(case_kind)
        certificate_report = reports_by_kind[case_kind]
        if selected_case is None or not certificate_report.certificates:
            continue
        certificate = certificate_report.certificates[0]
        selector_selects_case = selected_case.case_kind == certificate.selected_case_kind
        construction_case_open = selected_case.status == REQUIRED_CASE_STATUS
        certificate_accepted = certificate.accepted
        entries.append(
            FixedPointSelectedRootCertificateCoverageEntry(
                coverage_id="AS-FIXED-POINT-SELECTED-ROOT-COVERAGE-" + case_kind.upper().replace("-", "_"),
                selected_case_kind=case_kind,
                construction_case_id=selected_case.case_id,
                certificate_set_id=certificate_report.manifest.certificate_set_id,
                certificate_id=certificate.certificate_id,
                certificate_step_count=len(certificate.steps),
                coverage_status="accepted-finite-certificate-coverage-not-proof",
                selector_selects_case=selector_selects_case,
                construction_case_open=construction_case_open,
                certificate_accepted=certificate_accepted,
                proof_boundary_preserved=proof_boundary_preserved,
            )
        )
    return entries


def _validate_coverage(
    manifest: FixedPointSelectedRootCertificateCoverageManifest,
    selected_case_kinds: tuple[str, ...],
    deferred_case_kinds: tuple[str, ...],
    proof_boundary_preserved: bool,
    coverage_entries: list[FixedPointSelectedRootCertificateCoverageEntry],
) -> list[FixedPointSelectedRootCertificateCoverageValidation]:
    results: list[FixedPointSelectedRootCertificateCoverageValidation] = []
    if selected_case_kinds == manifest.expected_selected_case_kinds:
        results.append(_accepted("selected_case_kinds", "selected roots match"))
    else:
        results.append(_rejected("selected_case_kinds", "selected root mismatch"))

    if deferred_case_kinds == manifest.expected_deferred_case_kinds:
        results.append(_accepted("deferred_case_kinds", "deferred cases match"))
    else:
        results.append(_rejected("deferred_case_kinds", "deferred case mismatch"))

    if len(coverage_entries) == manifest.expected_selected_certificate_count:
        results.append(
            _accepted(
                "coverage_count",
                f"coverage count {len(coverage_entries)} matches",
            )
        )
    else:
        results.append(
            _rejected(
                "coverage_count",
                "coverage count mismatch: expected "
                f"{manifest.expected_selected_certificate_count} but found "
                f"{len(coverage_entries)}",
            )
        )

    total_steps = sum(entry.certificate_step_count for entry in coverage_entries)
    if total_steps == manifest.expected_total_certificate_step_count:
        results.append(_accepted("total_certificate_step_count", "step count matches"))
    else:
        results.append(
            _rejected(
                "total_certificate_step_count",
                "total certificate step count mismatch: expected "
                f"{manifest.expected_total_certificate_step_count} but found "
                f"{total_steps}",
            )
        )

    if proof_boundary_preserved:
        results.append(_accepted("proof_boundary", "proof boundary preserved"))
    else:
        results.append(_rejected("proof_boundary", "proof boundary not preserved"))

    rejected_entries = [
        entry.selected_case_kind for entry in coverage_entries if not entry.accepted
    ]
    if rejected_entries:
        results.append(
            _rejected(
                "coverage_entries",
                "rejected entries: " + ", ".join(rejected_entries),
            )
        )
    else:
        results.append(_accepted("coverage_entries", "all coverage entries accepted"))
    return results


def _proof_boundary_preserved(
    manifest: FixedPointSelectedRootCertificateCoverageManifest,
    selector_report: Any,
    diagonal_certificate_report: Any,
    graph_certificate_report: Any,
) -> bool:
    selected_open = all(
        case.status == REQUIRED_CASE_STATUS for case in selector_report.selected
    )
    deferred_open_with_blockers = all(
        case.status == REQUIRED_CASE_STATUS and bool(case.blocking_predecessors)
        for case in selector_report.deferred
    )
    certificate_non_claims = (
        set(diagonal_certificate_report.manifest.non_claims)
        | set(graph_certificate_report.manifest.non_claims)
    )
    return (
        selected_open
        and deferred_open_with_blockers
        and selector_report.frontier_status == "blocked"
        and selector_report.frontier_blocked_by == "fixed-point-construction"
        and set(REQUIRED_NON_CLAIMS).issubset(set(manifest.non_claims))
        and "no fixed-point equation proof" in certificate_non_claims
        and "no self-consistency theorem" in certificate_non_claims
    )


def _accepted(
    subject: str,
    detail: str,
) -> FixedPointSelectedRootCertificateCoverageValidation:
    return FixedPointSelectedRootCertificateCoverageValidation(
        subject=subject,
        accepted=True,
        detail=detail,
    )


def _rejected(
    subject: str,
    detail: str,
) -> FixedPointSelectedRootCertificateCoverageValidation:
    return FixedPointSelectedRootCertificateCoverageValidation(
        subject=subject,
        accepted=False,
        detail=detail,
    )


def _failed_subject_for_result(subject: str) -> str:
    if subject in {"expected_selected_case_kinds", "selected_case_kinds"}:
        return "fixed-point-selected-root-certificate-coverage-selected-roots"
    if subject in {"expected_deferred_case_kinds", "deferred_case_kinds"}:
        return "fixed-point-selected-root-certificate-coverage-deferred-cases"
    if subject in {"expected_selected_certificate_count", "coverage_count"}:
        return "fixed-point-selected-root-certificate-coverage-count"
    if subject in {
        "expected_total_certificate_step_count",
        "total_certificate_step_count",
    }:
        return "fixed-point-selected-root-certificate-coverage-step-count"
    if subject == "non_claims":
        return "fixed-point-selected-root-certificate-coverage-non-claim"
    if subject == "proof_boundary":
        return "fixed-point-selected-root-certificate-coverage-boundary"
    if subject == "coverage_entries":
        return "fixed-point-selected-root-certificate-coverage-entry"
    if subject.endswith("_path"):
        return "fixed-point-selected-root-certificate-coverage-path"
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
    raise SystemExit(run_fixed_point_selected_root_certificate_coverage_cli())
